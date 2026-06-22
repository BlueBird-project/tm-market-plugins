from builtins import super
from typing import List, Optional, Dict, Iterable, Type, Union

from pydantic import BaseModel, ConfigDict
from rdflib import URIRef

from tm_entso_e.schemas.market import DAYAHEAD_MARKET_TYPE, INTRADAY_MARKET_TYPE
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
class MarketTypeInfo(BaseModel):
    publish: str
    offer_length: int
    sequence: Optional[str] = None
    max_delay: Optional[str] = None
    publish_hour: int = 15
    publish_min: int = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.publish:
            f = self.publish.split(":")
            self.publish_hour = int(f[0])
            self.publish_min = int(f[1])

    @property
    def max_delay_ts(self) -> int:
        from isodate import parse_duration
        if self.max_delay is None:
            return 3600000
        return int(parse_duration(self.max_delay).total_seconds() * 1000.0)


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


class EICArea(BaseModel):
    code: str
    area_names: List[str]
    country_codes: Optional[List[str]] = None
