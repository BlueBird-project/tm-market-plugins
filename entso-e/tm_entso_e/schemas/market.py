from typing import Optional

from pydantic import BaseModel, ConfigDict
from rdflib import URIRef


class _BaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class Market(_BaseModel):
    market_id: Optional[int] = None
    market_uri: str
    market_name: str
    market_type: str
    market_description: Optional[str] = None
    market_location: Optional[str] = None
    subscribe: bool


class MarketOfferDetails(_BaseModel):
    offer_id: Optional[int] = None
    market_id: int
    offer_uri: str
    sequence: Optional[str]
    currency_unit: str
    volume_unit: str
    ts_start: int
    ts_end: int
    isp_unit: int

    @property
    def is_measured_in(self) -> str:
        return f"{self.currency_unit}Per{self.volume_unit}"


class MarketOfferDetailsResponse(MarketOfferDetails):
    dt_start: str
    dt_end: str
    measured_in: str

    @staticmethod
    def init(md: MarketOfferDetails) -> 'MarketOfferDetailsResponse':
        from ke_client.utils import time_utils
        return MarketOfferDetailsResponse(
            dt_start=time_utils.datetime_to_str(time_utils.from_timestamp(md.ts_start)),
            dt_end=time_utils.datetime_to_str(time_utils.from_timestamp(md.ts_end)),
            measured_in=f"{md.currency_unit}Per{md.volume_unit}",
            **vars(md))


class MarketOffer(_BaseModel):
    ts: int
    offer_id: int
    isp_start: int
    isp_len: int
    cost: float


class MarketOfferValues(BaseModel):
    offer_id: int
    sequence: Optional[str]
    currency_unit: str
    volume_unit: str
    isp_unit: int
    ts_start: int
    ts: int
    isp_start: int
    isp_len: int
    cost: Optional[float]


class MarketOfferValuesState(BaseModel):
    offer_id: int
    data_points: int
    state: bool
    total_isp_span: int
    ts_start: int
    sequence: Optional[str]
    market_id: int
    market_location: str
