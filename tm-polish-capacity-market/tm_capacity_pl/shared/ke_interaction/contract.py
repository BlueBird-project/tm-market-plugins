from typing import Optional

from isodate import parse_duration
from ke_client import ki_object, BindingsBase
from ke_client.utils import time_utils
from rdflib import URIRef, Literal


@ki_object("contract")
class MarketContract(BindingsBase):
    flex_offer: URIRef
    market: URIRef
    contract: URIRef
    flex_dp: URIRef
    flex_dpr: URIRef
    cost_dp: URIRef
    v: URIRef
    duration_uri: URIRef
    ts: Literal
    duration: Literal
    cost_value: Literal
    flex_value: Literal

    @property
    def end_ts(self) -> int:
        return int(
            parse_duration(self.duration, as_timedelta_if_possible=True).total_seconds() * 1000) + time_utils.xsd_to_ts(
            self.time_create)

    @property
    def ts_ms(self):
        return time_utils.xsd_to_ts(self.time_create)

    @property
    def duration_ms(self) -> int:
        return int(parse_duration(self.duration, as_timedelta_if_possible=True).total_seconds() * 1000)

    def get_cost_value(self) -> Optional[float]:
        return self.convert_value(self.cost_value, float)

    def get_flex_value(self) -> Optional[float]:
        return self.convert_value(self.flex_value, float)


@ki_object("contract-ack")
class ContractACK(BindingsBase):
    ack_execution: URIRef
    contract: URIRef
    result: URIRef
    ack_time: URIRef

    @property
    def ts_ms(self):
        return time_utils.xsd_to_ts(self.ack_time)
