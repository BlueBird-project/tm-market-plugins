from typing import Optional

from pydantic import BaseModel
from rdflib import URIRef

DAYAHEAD_MARKET_TYPE=URIRef(value="DayAheadMarket", base="https://ubeflex.bluebird.eu/market/")
INTRADAY_MARKET_TYPE=URIRef(value="IntradayMarket", base="https://ubeflex.bluebird.eu/market/")

class Market(BaseModel):
    market_id: Optional[int] = None
    market_uri: str
    market_name: str
    market_type: str
    market_description: Optional[str] = None
    market_location: Optional[str] = None
    subscribe: bool
    update_ts: Optional[int] = None
    ext: Optional[str] = None


class MarketOfferDetails(BaseModel):
    offer_id: Optional[int] = None
    market_id: int
    sequence: Optional[int]
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


class MarketOffer(BaseModel):
    ts: int
    offer_id: int
    isp_start: int
    isp_len: int
    cost: float
    update_ts: Optional[int] = None
