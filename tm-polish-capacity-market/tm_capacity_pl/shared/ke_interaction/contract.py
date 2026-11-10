from typing import Optional

from ke_client import ki_object, BindingsBase, SplitURIBase
from ke_client.utils import time_utils
from rdflib import URIRef, Literal
from rdflib.plugins.sparql.sparql import Bindings

from tm_capacity_pl.models.contract import FlexContract
from tm_capacity_pl.shared import POLAND_TZ


@ki_object("contract", allow_partial=True)
class KEFlexContractQuery(BindingsBase):
    flex_request: Optional[URIRef]
    asset_manager: Optional[URIRef]


@ki_object("contract")
class KEFlexContract(BindingsBase):
    flex_request: URIRef
    contract: URIRef
    asset_manager: URIRef

    flex_dp: URIRef
    price_dp: URIRef
    flex_dpr: URIRef
    price_dpr: URIRef
    flex_value: Literal
    price_value: Literal

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

    def get_price_value(self) -> Optional[float]:
        return self.convert_value(self.price_value, float)

    def get_flex_value(self) -> Optional[float]:
        return self.convert_value(self.flex_value, float)

    @staticmethod
    def init(flex_request: URIRef, asset_manager: URIRef, contract_uri: URIRef, flex_value: Literal,
             price_value: Literal,
             ts_from: int, ts_to: int) -> 'KEFlexContract':
        return KEFlexContract(flex_request=flex_request, contract=contract_uri,
                              asset_manager=asset_manager,
                              flex_dp=SplitURIBase.uri_append_ref(contract_uri, "flex_dp"),
                              price_dp=SplitURIBase.uri_append_ref(contract_uri, "price_dp"),
                              flex_dpr=SplitURIBase.uri_append_ref(contract_uri, "flex_dpr"),
                              price_dpr=SplitURIBase.uri_append_ref(contract_uri, "price_dpr"),
                              flex_value=flex_value, price_value=price_value,
                              period_uri=SplitURIBase.uri_append_ref(contract_uri, "period"),
                              ts_date_from=time_utils.xsd_from_ts(ts=ts_from, tz=POLAND_TZ),
                              ts_date_to=time_utils.xsd_from_ts(ts=ts_to, tz=POLAND_TZ), )


@ki_object("contract-ack")
class KEFlexContractACK(BindingsBase):
    ack_execution: URIRef
    asset_manager: URIRef
    flex_request: URIRef
    contract: URIRef
    evt: URIRef
    flex_result: URIRef
    accepted_flex: Literal
    price_result: URIRef
    accepted_price: Literal
    ack_time: Literal

    @property
    def ack_time_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ack_time)

    def rdf_parse(self) -> FlexContract:
        return FlexContract(
            contract_uri=self.contract_uri.n3(), flex_request_uri=self.flex_request_uri.n3(),
            flex_value=self.convert_value(self.accepted_flex, float),
            price_value=self.convert_value(self.accepted_price, float),
            ack_ts=time_utils.xsd_to_ts(self.ts), )
