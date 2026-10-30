from typing import Union, Optional

from ke_client import BindingsBase, ki_object, ki_split_uri, SplitURIBase, OptionalLiteral
from ke_client.utils import time_utils
from rdflib import URIRef, Literal

from tm_capacity_pl.shared.ke_interaction.contract import FlexContractRequest


@ki_object("contract")
class FlexContract(FlexContractRequest):
    flex_request: URIRef
    # contract: URIRef
    asset_manager: URIRef

    flex_dp: URIRef
    cost_dp: URIRef
    flex_dpr: URIRef
    cost_dpr: URIRef
    flex_value: Literal
    cost_value: Literal

    period_uri: URIRef
    ts_date_from: Literal
    ts_date_to: Literal

    @property
    def ts_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts)

    @property
    def ts_date_from_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts_date_from)

    @property
    def ts_date_to_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts_date_to)

    def get_cost_value(self) -> Optional[float]:
        return self.convert_value(self.cost_value, float)

    def get_flex_value(self) -> Optional[float]:
        return self.convert_value(self.flex_value, float)

@ki_object("baseline-request")
class BaselineDateRequest(BindingsBase):
    ts_uri: URIRef
    ts_baseline_from: Literal
    ts_baseline_to: Literal
    baseline_interval_uri: URIRef

    @property
    def from_ts(self) -> int:
        return time_utils.xsd_to_ts(self.ts_baseline_from)

    @property
    def to_ts(self) -> int:
        return time_utils.xsd_to_ts(self.ts_baseline_to)


@ki_object("baseline-request", result=True)
class BaselineDateResponse(BindingsBase):
    day_interval_uri: URIRef
    ts_day_from: URIRef
    ts_day_to: URIRef

    @property
    def from_ts(self) -> int:
        return time_utils.xsd_to_ts(self.ts_baseline_from)

    @property
    def to_ts(self) -> int:
        return time_utils.xsd_to_ts(self.ts_baseline_to)


@ki_object("baseline")
class BaselineRequest(BindingsBase):
    ts_uri: URIRef
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
class FlexRequest(BindingsBase):
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


@ki_split_uri(uri_template="/flex_request/{ts}")
class FlexRequestUri(SplitURIBase):
    ts: int


@ki_object("flex-offer")
class FlexOffer(BindingsBase):
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


@ki_object("price-offer")
class FlexPriceOffer(BindingsBase):
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
    cost_value: Literal

    @property
    def ts_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts)


@ki_split_uri(uri_template="/flex_request/{ts}")
class FlexRequestUri(SplitURIBase):
    ts: int




@ki_split_uri(uri_template="/flex_contract/{ts}")
class FlexContractUri(SplitURIBase):
    ts: int


@ki_object("contract-ack")
class FlexContractACK(BindingsBase):
    ack_execution: URIRef
    # contract: URIRef
    contract: URIRef

    result: URIRef
    ack_time: URIRef

    @property
    def ack_time_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ack_time)


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

