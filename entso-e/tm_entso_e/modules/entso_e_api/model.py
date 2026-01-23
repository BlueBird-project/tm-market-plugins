from typing import List, Optional

from pydantic import BaseModel

from tm_entso_e.utils.enum_utils import EnumUtils


class MarketAgreementTypeCode(EnumUtils):
    DAY_AHEAD = "A01"
    INTRADAY = "A07"


class SubscribedEIC(BaseModel):
    code: str
    market_types: List[str]
    _market_codes_: List[str]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._market_codes_ = [MarketAgreementTypeCode.parse(s) for s in self.market_types]

    @property
    def market_codes(self):
        return self._market_codes_


class EICArea(BaseModel):
    code: str
    area_names: List[str]
    country_codes: Optional[List[str]] = None
