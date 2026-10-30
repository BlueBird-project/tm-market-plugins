from typing import Optional

from ke_client import BindingsBase, ki_object, ki_split_uri, SplitURIBase
from ke_client.utils import time_utils
from rdflib import URIRef, Literal

from tm_capacity_pl.shared.ke_interaction.contract import FlexContractRequest

@ki_object("contract")
class FlexContract(FlexContractRequest):
    flex_request: URIRef
    contract: URIRef
    market: URIRef
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
# @ki_object("contract")
# class FlexContract(FlexContractRequest):
#     flex_request: URIRef
#     # contract: URIRef
#     asset_manager: URIRef
#
#     flex_dp: URIRef
#     cost_dp: URIRef
#     flex_dpr: URIRef
#     cost_dpr: URIRef
#     flex_value: Literal
#     cost_value: Literal
#
#     period_uri: URIRef
#     ts_date_from: Literal
#     ts_date_to: Literal
#
#     @property
#     def ts_ms(self) -> int:
#         return time_utils.xsd_to_ts(self.ts)
#
#     @property
#     def ts_date_from_ms(self) -> int:
#         return time_utils.xsd_to_ts(self.ts_date_from)
#
#     @property
#     def ts_date_to_ms(self) -> int:
#         return time_utils.xsd_to_ts(self.ts_date_to)
#
#     def get_cost_value(self) -> Optional[float]:
#         return self.convert_value(self.cost_value, float)
#
#     def get_flex_value(self) -> Optional[float]:
#         return self.convert_value(self.flex_value, float)


@ki_object("flex-demand")
class KECapacityNotification(BindingsBase):
    asset_manager: URIRef
    flex_instruction: URIRef
    flex_offer: URIRef
    flex_profile: URIRef
    power_limit: URIRef
    ts: Literal
    max_consumption: URIRef
    max_consumption_value: Literal


@ki_split_uri(uri_template="/demand/${ts}/${asset_manager_id}")
class FlexInstructionUri(SplitURIBase):
    asset_manager_id: int
    ts: int

    def power_limit_uri(self):
        return URIRef(self.append("powerlimit"))
    def profile_uri(self):
        return URIRef(self.append("profile"))

    def power_limit_max_uri(self):
        return URIRef(self.append("powerlimit/max"))
