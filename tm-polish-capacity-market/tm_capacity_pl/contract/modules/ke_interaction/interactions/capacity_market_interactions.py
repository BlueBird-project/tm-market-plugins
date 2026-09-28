import logging
from typing import List, Tuple

from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse

from tm_capacity_pl.contract.modules.ke_interaction.interactions.capacity_market_model import BaselineFlexRequest, \
    BaselineFlexResponse

ki = KIHolder()


@ki.post("baseline-flexibility")
def _request_flexibility_offer(baseline: List[BaselineFlexRequest]):
    return baseline


def request_flexibility_offer(baseline: List[BaselineFlexRequest]) -> BaselineFlexResponse:
    resp_bindings: KIPostResponse = _request_flexibility_offer(baseline=baseline)
    flex_offer = [BaselineFlexResponse(**b) for b in resp_bindings.result_binding_set]
    assert len(flex_offer) == 1
    return flex_offer[0]
