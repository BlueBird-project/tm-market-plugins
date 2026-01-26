from typing import List, Optional, Dict, Iterable, Type

from pydantic import BaseModel, ConfigDict
from rdflib import Literal

from tm_entso_e.utils.enum_utils import BaseEnum


class MarketAgreementTypeCode(BaseEnum):
    class _Value(BaseModel):
        model_config = ConfigDict(arbitrary_types_allowed=True)
        code: str
        literal: Literal

    DAY_AHEAD = _Value(code="A01", literal=Literal("DayAheadMarket", datatype="ubmarket"))
    INTRADAY = _Value(code="A07", literal=Literal("IntradayMarket", datatype="ubmarket"))

    @classmethod
    def parse(cls: Type, s: str, nullable: bool = False) -> Optional[_Value]:
        return super().parse(s=s, nullable=nullable)


class SubscribedEIC(BaseModel):
    code: str
    market_types: List[str]
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
