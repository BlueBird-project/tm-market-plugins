from typing import Optional, Union

from effi_onto_tools.utils import time_utils
from isodate import parse_duration
from ke_client import BindingsBase, is_nil
from ke_client import ki_object, ki_split_uri, SplitURIBase, OptionalLiteral
from rdflib import URIRef, Literal


@ki_object("market")
class EnergyMarketBindings(BindingsBase):
    market_uri: URIRef
    country_uri: URIRef
    country_name: Literal
    market_type: URIRef

    # market_type: Literal = DAM_market_type

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


@ki_object("market", allow_partial=True)
class EnergyMarketBindingsQuery(BindingsBase):
    market_uri: Optional[URIRef] = None
    country_name: Optional[Literal] = None
    market_type: Optional[URIRef] = None

    # market_type: Literal = DAM_market_type

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


#
#
# @ki_object("market-offer-info-query", allow_partial=True)
# class MarketOfferInfoQuery(BindingsBase):
#     ts_interval_uri: URIRef
#     market_uri: URIRef
#     ts_date_from: Literal
#     ts_date_to: Literal
#
#     def __init__(self, **kwargs):
#         super().__init__(bindings=kwargs)
#
#     @property
#     def ts_from(self) -> int:
#         return time_utils.xsd_to_ts(self.ts_date_from)
#
#     @property
#     def ts_to(self) -> int:
#         return time_utils.xsd_to_ts(self.ts_date_to)
#
#
# @ki_object("market-offer-info-query", result=True)
# class MarketOfferInfoResponse(BindingsBase):
#     market_uri: URIRef
#     offer_uri: URIRef
#     time_create: Literal
#
#     @property
#     def create_ts(self):
#         return time_utils.xsd_to_ts(self.time_create)
#
#
@ki_object("market-offer-info")
class MarketOfferInfoBindings(BindingsBase):
    market_uri: URIRef
    market_type: URIRef
    offer_uri: URIRef
    sequence: Union[Literal, URIRef, None] = None
    update_rate: Literal
    time_create: Literal
    duration: Literal

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)

    @property
    def create_ts(self):
        return time_utils.xsd_to_ts(self.time_create)

    @property
    def duration_ms(self) -> int:
        return int(parse_duration(self.duration, as_timedelta_if_possible=True).total_seconds() * 1000)

    @property
    def update_rate_min(self) -> int:
        return int(parse_duration(self.update_rate, as_timedelta_if_possible=True).total_seconds() / 60)


@ki_object("market-offer-info-filtered")
class MarketOfferInfoFilteredBindings(MarketOfferInfoBindings):
    ts_interval_uri: Optional[URIRef]
    ts_date_from: OptionalLiteral
    ts_date_to: OptionalLiteral

    @property
    def ts_from(self):
        return time_utils.xsd_to_ts(self.ts_date_from)

    @property
    def ts_to(self):
        return time_utils.xsd_to_ts(self.ts_date_to)


#
@ki_object("market-offer-info", allow_partial=True)
class MarketOfferInfoRequest(BindingsBase):
    market_uri: Optional[URIRef] = None
    market_type: Optional[URIRef] = None
    sequence: Optional[Literal] = None


@ki_object("market-offer-info-filtered", allow_partial=True)
class MarketOfferInfoFilteredRequest(MarketOfferInfoRequest):
    ts_interval_uri: Optional[URIRef]
    ts_date_from: OptionalLiteral
    ts_date_to: OptionalLiteral

    @property
    def ts_from(self):
        if is_nil(self.ts_date_from):
            return None
        return time_utils.xsd_to_ts(self.ts_date_from)

    @property
    def ts_to(self):
        if is_nil(self.ts_date_to):
            return None
        return time_utils.xsd_to_ts(self.ts_date_to)


@ki_object("market-offer")
class MarketOfferBindings(BindingsBase):
    offer_uri: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    is_measured_in: Literal
    duration: Literal
    value: Union[URIRef, Literal, None]

    # def __init__(self, **kwargs):
    #     super().__init__(bindings=kwargs)

    @property
    def ts_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts)

    def get_value(self) -> Optional[float]:
        return self.convert_value(self.value, float)


@ki_object("market-offer", allow_partial=True)
class MarketOfferRequest(BindingsBase):
    offer_uri: URIRef


@ki_split_uri(uri_template="${eic_area}/${market_code}")
class MarketURI(SplitURIBase):
    eic_area: str
    market_code: str
    __MARKET_PREFIX__: str = ""

    def __init__(self, eic_area: str, market_code: str):
        # if prefix is None:
        #     prefix = MarketURI.__PREFIX__
        super().__init__(prefix=MarketURI.__MARKET_PREFIX__, eic_area=eic_area, market_code=market_code)


@ki_split_uri(uri_template="https://ubeflex.bluebird.eu/country/${country_name}")
class CountryURI(SplitURIBase):
    # TODO use different country uri prefix
    country_name: str


@ki_split_uri(uri_template="offer/${sequence}/${ts_start}/${ts_len}")
class OfferUri(SplitURIBase):
    __EMPTY__ = "_"
    sequence: str
    ts_start: int
    ts_len: int

    def __init__(self, sequence: Optional[str], **kwargs):
        if sequence is None:
            sequence = OfferUri.__EMPTY__
        super().__init__(sequence=sequence, **kwargs)

    @property
    def processed_sequence(self) -> Optional[str]:
        if self.sequence == OfferUri.__EMPTY__:
            return None
        return self.sequence

    @staticmethod
    def get_prefix(uri: [str, URIRef]) -> str:
        return str(uri).split("/offer/")[0]
