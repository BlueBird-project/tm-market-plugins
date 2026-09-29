import logging
from typing import List, Tuple

from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse

from tm_capacity_pl.contract.modules.ke_interaction.interactions.capacity_market_model import BaselineFlexRequest, \
    BaselineFlexResponse, MarketPrice, TMContract

ki = KIHolder()


@ki.post("baseline-flexibility")
def _request_flexibility_offer(baseline: List[BaselineFlexRequest]):
    return baseline


@ki.react("baseline-flexibility")
def on_contract(kb_id: str, bindings: List[TMContract]):
    # todo:
    # process contract
    return []


@ki.post("capacity-market-price")
def _post_market_price():
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_prices
    return get_prices()


@ki.answer("capacity-market-price")
def _answer_market_price() -> List[MarketPrice]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_prices
    return get_prices()


def request_flexibility_offer(baseline: List[BaselineFlexRequest]) -> BaselineFlexResponse:
    resp_bindings: KIPostResponse = _request_flexibility_offer(baseline=baseline)
    flex_offer = [BaselineFlexResponse(**b) for b in resp_bindings.result_binding_set]
    assert len(flex_offer) == 1
    return flex_offer[0]


def post_market_price():
    resp_bindings: KIPostResponse = _post_market_price()
    pass
