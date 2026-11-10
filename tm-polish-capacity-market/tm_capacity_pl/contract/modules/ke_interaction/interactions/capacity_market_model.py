from typing import Union, Optional

from ke_client import BindingsBase, ki_object, ki_split_uri, SplitURIBase, OptionalLiteral
from ke_client.utils import time_utils
from rdflib import URIRef, Literal

from capacity_market_utils import POLAND_TZ
from tm_capacity_pl.models.contract import FlexRequest, FlexOffer, FlexPriceOffer, FlexContract



@ki_object("baseline-request", allow_partial=True)
class BaselineDateRequest(BindingsBase):
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


@ki_object("baseline-request")
class BaselineDate(BaselineDateRequest):
    baseline_ts_uri: URIRef
    baseline_interval_uri: URIRef


@ki_object("baseline-request", result=True)
class BaselineDateResponse(BindingsBase):
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


@ki_object("baseline")
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


@ki_object("baseline", result=True)
class Baseline(BindingsBase):
    ts_uri: URIRef
    dp_baseline: URIRef
    ts: Literal
    dpr_baseline: URIRef
    value_baseline: Union[URIRef, Literal, None]


@ki_object("flex-request")
class KEFlexRequest(BindingsBase):
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
        return KEFlexRequest(flex_request=URIRef(request.flex_request_uri),
                             offer_period=URIRef(request.offer_period_uri),
                             ts=Literal(time_utils.xsd_from_ts(request.create_ts, tz=POLAND_TZ)),
                             ts_date_from=Literal(time_utils.xsd_from_ts(request.ts_from, tz=POLAND_TZ)),
                             ts_date_to=Literal(time_utils.xsd_from_ts(request.ts_to, tz=POLAND_TZ)))


@ki_split_uri(uri_template="/flex_request/{ts}")
class FlexRequestUri(SplitURIBase):
    ts: int


@ki_object("flex-offer", allow_partial=True)
class KEFlexOfferQuery(BindingsBase):
    flex_request: URIRef


@ki_object("flex-offer")
class KEFlexOffer(BindingsBase):
    flex_request: URIRef
    asset_manager: URIRef
    flex_profile: URIRef
    profile_price: URIRef
    price: Literal
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
        return FlexOffer(
            flex_request_uri=self.flex_request.n3(), asset_manager_uri=self.asset_manager.n3(),
            flex_profile_uri=self.flex_profile.n3(), profile_price_uri=self.profile_price.n3(),
            flex_price=self.convert_value(self.price, float),
            ts=time_utils.xsd_to_ts(self.ts), flex_value=self.convert_value(self.value, float))


@ki_object("price-offer")
class KEFlexOffer(BindingsBase):
    flex_request: URIRef
    asset_manager: URIRef
    flex_profile: URIRef
    profile_price: URIRef
    price: Literal
    dp: URIRef
    cost_dp: URIRef
    ts: Literal
    dpr: URIRef
    cost_dp: URIRef
    value: Literal
    price_value: Literal

    @property
    def ts_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts)

    def rdf_parse(self) -> FlexOffer:
        return FlexOffer(
            flex_request_uri=self.flex_request.n3(), asset_manager_uri=self.asset_manager.n3(),
            flex_profile_uri=self.flex_profile.n3(), profile_price_uri=self.profile_price.n3(),
            flex_price=self.convert_value(self.price, float),
            ts=time_utils.xsd_to_ts(self.ts), flex_value=self.convert_value(self.value, float))


@ki_object("price-offer", allow_partial=True)
class KEFlexPriceOfferQuery(BindingsBase):
    flex_request: URIRef
    asset_manager: Optional[URIRef] = None


@ki_object("price-offer")
class KEFlexPriceOffer(BindingsBase):
    flex_request: URIRef
    flex_profile: URIRef
    asset_manager: URIRef
    profile_price: URIRef
    price: Literal
    dp: URIRef
    cost_dp: URIRef
    ts: Literal
    dpr: URIRef
    cost_dpr: URIRef
    value: Literal
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


@ki_split_uri(uri_template="/flex_request/{ts}")
class FlexRequestUri(SplitURIBase):
    ts: int


@ki_split_uri(uri_template="/flex_contract/{ts}")
class FlexContractUri(SplitURIBase):
    ts: int


@ki_object("capacity-market-price")
class MarketPrice(BindingsBase):
    offer_uri: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    duration_uri: URIRef
    duration: Literal
    value: Union[URIRef, Literal, None]


#############################################################################
@ki_split_uri(uri_template="/price")
class MarketOfferUri(SplitURIBase):
    pass


@ki_split_uri(uri_template="/year/${year}/${quarter}")
class DurationURI(SplitURIBase):
    year: int
    quarter: int = 0


@ki_split_uri(uri_template="/dp/${year}/${quarter}")
class MarketOfferDPUri(SplitURIBase):
    year: int
    quarter: int = 0


@ki_split_uri(uri_template="/dpr/${year}/${quarter}")
class MarketOfferDPRUri(SplitURIBase):
    isp: int
