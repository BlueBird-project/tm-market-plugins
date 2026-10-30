import logging
from typing import List, Tuple

from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse

from tm_capacity_pl.contract.modules.ke_interaction.interactions.capacity_market_model import MarketPrice, \
    BaselineRequest, Baseline, BaselineDateResponse, BaselineDateRequest, FlexRequest, FlexOffer, \
    FlexPriceOffer, FlexContract, FlexContractRequest, FlexContractACK

ki = KIHolder()


@ki.react("baseline")
def _calc_baseline(kb_id: str, bindings: List[BaselineRequest]) -> List[Baseline]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import calc_baseline
    return calc_baseline(bindings=bindings)


@ki.react("baseline-request")
def _get_required_days(kb_id: str, bindings: List[BaselineDateRequest]) -> List[BaselineDateResponse]:
    # todo get list of days eligible for capacity market
    return []


@ki.post("flex-request")
def _get_required_days() -> List[FlexRequest]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_flex_request
    return get_flex_request(kb_id=ki.get_kb_id())


@ki.answer("flex-request")
def _get_required_days(kb_id: str, bindings: List) -> List[FlexRequest]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_flex_request
    return get_flex_request(kb_id=ki.get_kb_id())


@ki.react("flex-offer")
def _on_flex_offer(kb_id, bindings: List[FlexOffer]) -> List:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import process_offer
    process_offer(bindings)
    return []


# @ki.post("flex-offer")
# def _publish_flex_offer(current_offer: List[FlexOffer]) -> List[FlexOffer]:
#     return current_offer


@ki.answer("flex-offer")
def _on_flex_offer_request(kb_id, bindings) -> List[FlexOffer]:
    # TM asks for current flex offer
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import process_offer
    # todo: get current flex offer and publish
    return []


@ki.react("price-offer")
def _on_flex_offer(kb_id, bindings: List[FlexPriceOffer]) -> List:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import process_price_offer
    # todo:
    process_price_offer(bindings)
    return []


@ki.post("contract")
def _post_contract():
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_contracts
    return get_contracts(kb_id=ki.get_kb_id())


@ki.answer("contract")
def _answer_contract(ki_id, bindings: List[FlexContractRequest]):
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_contract
    res = []
    for b in bindings:
        res += get_contract(kb_id=ki.get_kb_id(), asset_uri=b.asset_manager)
    return res


@ki.react("contract-ack")
def _on_flex_offer(kb_id, bindings: List[FlexContractACK]) -> List:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import process_contract_ack
    # todo:
    process_contract_ack(bindings)
    return []


# verify market interaction todo:
@ki.post("capacity-market-price")
def _post_market_price():
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_prices
    return get_prices()


@ki.answer("capacity-market-price")
def _answer_market_price() -> List[MarketPrice]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_prices
    return get_prices()


# def request_flexibility_offer(baseline: List[BaselineFlexRequest]) -> BaselineFlexResponse:
#     resp_bindings: KIPostResponse = _request_flexibility_offer(baseline=baseline)
#     flex_offer = [BaselineFlexResponse(**b) for b in resp_bindings.result_binding_set]
#     assert len(flex_offer) == 1
#     return flex_offer[0]


def post_market_price():
    resp_bindings: KIPostResponse = _post_market_price()
    # todo:


def post_market_contract(contract_ack: List[FlexContractACK]):
    resp_bindings: KIPostResponse = _post_contract(contract_ack)
    # resp_bindings.exchangeInfo[0].knowledgeBaseId
    # todo: verify if all have acknowledged the contract
