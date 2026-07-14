from builtins import super
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional, Dict, Iterable, Type, Union

from pydantic import BaseModel, ConfigDict
from rdflib import URIRef

from tm_entso_e.schemas.market import DAYAHEAD_MARKET_TYPE, INTRADAY_MARKET_TYPE
from tm_entso_e.utils import time_utils
from tm_entso_e.utils.enum_utils import BaseEnum


class MarketAgreementTypeCode(BaseEnum):
    class _Value(BaseModel):
        model_config = ConfigDict(arbitrary_types_allowed=True)
        code: str
        uri_ref: URIRef

    DAY_AHEAD = _Value(code="A01", uri_ref=DAYAHEAD_MARKET_TYPE)
    INTRADAY = _Value(code="A07", uri_ref=INTRADAY_MARKET_TYPE)

    @classmethod
    def parse(cls: Type, s: str, nullable: bool = False) -> Optional[_Value]:
        return super().parse(s=s, nullable=nullable)


# Literal("PT60M", datatype=XSD.duration)
@dataclass(frozen=True)
class MarketTypeInfo:
    publish: str
    offer_length: Optional[int] = None
    sequence: Optional[str] = None
    max_delay: Optional[str] = None
    # UTC publish hour
    publish_hour: int = 15
    publish_min: int = 0

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     if self.publish:
    #         f = self.publish.split(":")
    #         self.publish_hour = int(f[0])
    #         self.publish_min = int(f[1])
    def __post_init__(self, ):
        if self.publish:
            f = self.publish.split(":")
            object.__setattr__(self, "publish_hour", int(f[0]))
            object.__setattr__(self, "publish_min", int(f[1]))

    @staticmethod
    def init_default():
        return MarketTypeInfo(publish="15:00", max_delay="PT2H")

    @property
    def max_delay_ts(self) -> int:
        from isodate import parse_duration
        if self.max_delay is None:
            return 3600000
        return int(parse_duration(self.max_delay).total_seconds() * 1000.0)

    @property
    def current_publish_ts(self) -> int:
        # TODO: check
        dt = datetime.now(tz=timezone.utc)
        publish_dt = datetime(year=dt.year, month=dt.month, day=dt.day, hour=self.publish_hour, minute=self.publish_min,
                              second=0, microsecond=0)
        return int(publish_dt.timestamp() * 1000.0)

    @property
    def is_publish_timeout(self):
        return (self.current_publish_ts + self.max_delay_ts) < time_utils.current_timestamp()


class SubscribedEIC(BaseModel):
    code: str
    market_types: Union[Dict[str, List[MarketTypeInfo]], List[str]]
    _market_codes_: Dict[str, str]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._market_codes_ = {MarketAgreementTypeCode.parse(s).code: MarketAgreementTypeCode.parse(s).name
                               for s in self.market_types}

    @property
    def market_codes(self) -> Iterable[str]:
        return self._market_codes_.keys()

    def get_market_type_name(self, code: str) -> str:
        return self._market_codes_[code]

    def get_market_type_info(self, code: str) -> Optional[List[MarketTypeInfo]]:
        market_type_name = self.get_market_type_name(code).lower()
        type_info = self.get_market_type(market_type_name)
        if isinstance(type_info, str):
            return None
        return type_info

    def get_market_type(self, market_type_code: str, default: bool = False) -> Union[List[MarketTypeInfo], str]:
        if isinstance(self.market_types, dict):
            try:
                return self.market_types[market_type_code]
            except KeyError:
                raise KeyError(f"Missing market type code: {market_type_code}, for market: {self.code}")

        if market_type_code in self.market_types:
            return market_type_code
        else:
            raise KeyError(f"Missing market type code: {market_type_code}, for market: {self.code}")


class EICArea(BaseModel):
    code: str
    area_names: List[str]
    country_codes: Optional[List[str]] = None
