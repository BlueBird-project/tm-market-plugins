from typing import Optional

from pydantic import BaseModel


class MarketDAO(BaseModel):
    market_id: Optional[int] = None
    market_uri: str
    market_name: str
    market_type: str
    market_description: Optional[str] = None
    market_location: Optional[str] = None
    subscribe: bool
    update_ts: Optional[int] = None
    ext: Optional[str] = None


class MarketOfferDetailsDAO(BaseModel):
    offer_id: Optional[int] = None
    market_id: int
    offer_uri: str
    sequence: Optional[str]
    currency_unit: str
    volume_unit: str
    ts_start: int
    ts_end: int
    isp_unit: int
    update_ts: Optional[int] = None
    ext: Optional[str] = None

    @property
    def is_measured_in(self) -> str:
        return f"{self.currency_unit}Per{self.volume_unit}"


class MarketOfferDAO(BaseModel):
    ts: int
    offer_id: int
    isp_start: int
    isp_len: int
    cost: float
    update_ts: Optional[int] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.isp_len<1:
            raise ValueError("isp_len must be positive integer")
