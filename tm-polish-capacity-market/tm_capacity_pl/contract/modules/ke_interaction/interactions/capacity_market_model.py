from typing import Union, Optional

from ke_client import BindingsBase, ki_object, ki_split_uri, SplitURIBase, OptionalLiteral
from ke_client.utils import time_utils
from rdflib import URIRef, Literal
from rdflib.util import from_n3

from capacity_market_utils import POLAND_TZ
from tm_capacity_pl.contract.config import market_settings
from tm_capacity_pl.models.contract import FlexRequest, FlexOffer, FlexPriceOffer, FlexContract


@ki_object("baseline-request", allow_partial=True)
class BaselineDateRequest(BindingsBase):
    market: URIRef = URIRef(market_settings.uri)
    asset_manager: URIRef
    ts_uri: URIRef
    ts_baseline_from: Literal
    ts_baseline_to: Literal
    baseline_interval_uri: URIRef

    @property
    def baseline_from_ts(self) -> int:
        return time_utils.xsd_to_ts(self.ts_baseline_from)

    @property
    def baseline_to_ts(self) -> int:
        return time_utils.xsd_to_ts(self.ts_baseline_to)


# @ki_object("baseline-request",allow_partial=True)
# class BaselineDate(BaselineDateRequest):
#     baseline_ts_uri: URIRef
#     baseline_interval_uri: URIRef


@ki_object("baseline-request")
class BaselineDateResponse(BaselineDateRequest):
    baseline_ts_uri:URIRef
    ts_uri: URIRef
    day_interval_uri: URIRef
    ts_day_from: Literal
    ts_day_to: Literal


    @property
    def from_ts(self) -> int:
        return time_utils.xsd_to_ts(self.ts_day_from)

    @property
    def to_ts(self) -> int:
        return time_utils.xsd_to_ts(self.ts_day_to)


# @ki_object("baseline-request", result=True)
# class BaselineDateResponse(BindingsBase):
#     ts_uri: URIRef
#     day_interval_uri: URIRef
#     ts_day_from: Literal
#     ts_day_to: Literal
#
#     @property
#     def from_ts(self) -> int:
#         return time_utils.xsd_to_ts(self.ts_day_from)
#
#     @property
#     def to_ts(self) -> int:
#         return time_utils.xsd_to_ts(self.ts_day_to)


@ki_object("baseline",allow_partial=True)
class BaselineRequest(BindingsBase):
    ts_uri: URIRef
    asset_manager: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    value: OptionalLiteral

    @property
    def ts_ms(self):
        return time_utils.xsd_to_ts(self.ts)

    def get_value(self):
        return self.convert_value(self.value, float)


@ki_object("baseline-response" )
class Baseline(BindingsBase):
    ts_uri: URIRef
    dp_baseline: URIRef
    ts: Literal
    dpr_baseline: URIRef
    value_baseline: Union[URIRef, Literal, None]


@ki_object("flex-request")
class KEFlexRequest(BindingsBase):
    market: URIRef = URIRef(market_settings.uri)
    flex_request: URIRef
    offer_period: URIRef
    # s4ener:hasCreationTime
    ts: Literal
    ts_date_from: Literal
    ts_date_to: Literal

    @property
    def from_ts(self) -> int:
        return time_utils.xsd_to_ts(self.ts_baseline_from)

    @property
    def create_ts(self) -> int:
        return time_utils.xsd_to_ts(self.ts)

    @property
    def to_ts(self) -> int:
        return time_utils.xsd_to_ts(self.ts_baseline_to)

    @staticmethod
    def init(request: FlexRequest) -> 'KEFlexRequest':
        return KEFlexRequest(flex_request=from_n3(request.flex_request_uri),
                             offer_period=from_n3(request.offer_period_uri),
                             ts=Literal(time_utils.xsd_from_ts(request.create_ts, tz=POLAND_TZ)),
                             ts_date_from=Literal(time_utils.xsd_from_ts(request.ts_from, tz=POLAND_TZ)),
                             ts_date_to=Literal(time_utils.xsd_from_ts(request.ts_to, tz=POLAND_TZ)))


@ki_split_uri(uri_template="/flex_request/${ts}")
class FlexRequestUri(SplitURIBase):
    ts: int


# @ki_object("flex-offer", allow_partial=True)
# class KEFlexOfferQuery(BindingsBase):
#     flex_request: URIRef


@ki_object("flex-offer")
class KEFlexOffer(BindingsBase):
    market: URIRef = URIRef(market_settings.uri)
    flex_request: URIRef
    asset_manager: URIRef
    flex_profile: URIRef
    profile_price: Optional[URIRef]=None
    price: OptionalLiteral=None
    dp: URIRef
    ts: Literal
    dpr: URIRef
    value: Literal

    @property
    def ts_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts)

    # @staticmethod
    # def init(request: FlexOffer) -> 'KEFlexRequest':
    #     return KEFlexRequest(flex_request=URIRef(request.flex_request_uri),
    #                          offer_period=URIRef(request.offer_period_uri),
    #                          ts=Literal(time_utils.xsd_from_ts(request.create_ts, tz=POLAND_TZ)),
    #                          ts_date_from=Literal(time_utils.xsd_from_ts(request.ts_from, tz=POLAND_TZ)),
    #                          ts_date_to=Literal(time_utils.xsd_from_ts(request.ts_to, tz=POLAND_TZ)))
    def rdf_parse(self) -> FlexOffer:
        if self.price is None:
            flex_price = 0.0
        else:
            flex_price=self.convert_value(self.price, float)
        return FlexOffer(
            flex_request_uri=self.flex_request.n3(), asset_manager_uri=self.asset_manager.n3(),
            flex_profile_uri=self.flex_profile.n3(), profile_price_uri=self.profile_price.n3(),
            flex_price=flex_price,
            ts=time_utils.xsd_to_ts(self.ts), flex_value=self.convert_value(self.value, float))


@ki_object("price-offer")
class KEFlexPriceOffer(BindingsBase):
    market: URIRef = URIRef(market_settings.uri)
    flex_request: URIRef
    asset_manager: URIRef
    flex_profile: URIRef
    profile_price: URIRef
    price: Literal
    flex_dp: URIRef
    flex_dpr: URIRef
    flex_value: Literal
    ts: Literal
    price_dp: URIRef
    price_dpr: URIRef
    price_value: Literal

    @property
    def ts_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts)

    def rdf_parse(self) -> FlexOffer:
        return FlexOffer(
            flex_request_uri=self.flex_request.n3(), asset_manager_uri=self.asset_manager.n3(),
            flex_profile_uri=self.flex_profile.n3(), profile_price_uri=self.profile_price.n3(),
            flex_price=self.convert_value(self.price_value, float),
            ts=time_utils.xsd_to_ts(self.ts), flex_value=self.convert_value(self.flex_value, float))


@ki_object("price-offer", allow_partial=True)
class KEFlexPriceOfferQuery(BindingsBase):
    flex_request: URIRef
    asset_manager: Optional[URIRef] = None


@ki_object("price-offer")
class KEFlexPriceOffer(BindingsBase):
    market: URIRef = URIRef(market_settings.uri)
    flex_request: URIRef
    flex_profile: URIRef
    asset_manager: URIRef
    profile_price: URIRef
    price: Literal
    flex_dp: URIRef
    flex_dpr: URIRef
    ts: Literal
    price_dp: URIRef
    price_dpr: URIRef
    flex_value: Literal
    price_value: Literal

    @property
    def ts_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts)

    def rdf_parse(self) -> FlexPriceOffer:
        return FlexPriceOffer(
            flex_request_uri=self.flex_request.n3(), asset_manager_uri=self.asset_manager.n3(),
            flex_profile_uri=self.flex_profile.n3(), profile_price_uri=self.profile_price.n3(),
            flex_price=self.convert_value(self.price, float),
            ts=time_utils.xsd_to_ts(self.ts), flex_value=self.convert_value(self.value, float),
            price_value=self.convert_value(self.price_value, float), )
    # @staticmethod
    # def to_rdf(o: FlexPriceOffer) -> 'KEFlexPriceOffer':
    #     return KEFlexPriceOffer(
    #         flex_request_uri=URIRef(o.flex_request_uri), asset_manager_uri=URIRef(o.asset_manager_uri),
    #         flex_profile_uri=URIRef(o.flex_profile_uri), profile_price_uri=URIRef(o.profile_price_uri),
    #         price=Literal(o.flex_price),
    #         ts=time_utils.xsd_from_ts(o.ts), value=Literal(o.flex_value),)


@ki_split_uri(uri_template="baseline/${ts_from}/${ts_to}")
class BaselineUri(SplitURIBase):
    ts_from :int
    ts_to :int


@ki_split_uri(uri_template="flex_request/${ts}")
class FlexRequestUri(SplitURIBase):
    ts: int


@ki_split_uri(uri_template="flex_contract/${ts}")
class FlexContractUri(SplitURIBase):
    ts: int


@ki_object("capacity-market-price")
class MarketPrice(BindingsBase):
    market: URIRef = URIRef(market_settings.uri)
    offer_uri: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    duration_uri: URIRef
    duration: Literal
    value: Union[URIRef, Literal, None]


#############################################################################
@ki_split_uri(uri_template="price")
class MarketOfferUri(SplitURIBase):
    pass


@ki_split_uri(uri_template="year/${year}/${quarter}")
class DurationURI(SplitURIBase):
    year: int
    quarter: int = 0


@ki_split_uri(uri_template="dp/${year}/${quarter}")
class MarketOfferDPUri(SplitURIBase):
    year: int
    quarter: int = 0


@ki_split_uri(uri_template="dpr/${isp}")
class MarketOfferDPRUri(SplitURIBase):
    isp: int
