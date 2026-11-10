import logging
from typing import List, Tuple

from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse

from tm_capacity_pl.contract.modules.ke_interaction.interactions.capacity_market_model import MarketPrice, \
    BaselineRequest, Baseline, BaselineDateResponse, BaselineDateRequest, KEFlexRequest, KEFlexOffer, \
    KEFlexPriceOffer, KEFlexContract, KEFlexOfferQuery, KEFlexContractACK
from tm_capacity_pl.shared.ke_interaction.contract import KEFlexContractQuery

ki = KIHolder()


@ki.post("flex-request")
def _post_flex_request() -> List[KEFlexRequest]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_flex_request
    return get_flex_request(kb_id=ki.get_kb_id())


@ki.answer("flex-request")
def _get_flex_request(kb_id: str, bindings: List) -> List[KEFlexRequest]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_flex_request
    return get_flex_request(kb_id=ki.get_kb_id())


@ki.react("baseline-request")
def _get_required_days(kb_id: str, bindings: List[BaselineDateRequest]) -> List[BaselineDateResponse]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_baseline_required_dates
    return get_baseline_required_dates(bindings=bindings)


@ki.react("baseline")
def _calc_baseline(kb_id: str, bindings: List[BaselineRequest]) -> List[Baseline]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import calc_baseline
    return calc_baseline(bindings=bindings)


@ki.react("flex-offer")
def _on_flex_offer(kb_id, bindings: List[KEFlexOffer]) -> List:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import process_offer
    process_offer(bindings)
    return []


# @ki.answer("flex-offer")
# def _on_flex_offer_request(kb_id, bindings: List[KEFlexOfferQuery]) -> List[KEFlexOffer]:
#     from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_flex_offer
#     get_flex_offer(bindings)
#     return []

@ki.react("price-offer")
def _on_price_offer(kb_id, bindings: List[KEFlexPriceOffer]) -> List:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import process_price_offer
    process_price_offer(bindings)
    return []


@ki.post("contract-ack")
def _post_contract_ack(contract_ack: List[KEFlexContractACK]) -> List[KEFlexContractACK]:
    return contract_ack


@ki.post("contract")
def _post_contract() -> List[KEFlexContract]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_contracts
    return get_contracts(kb_id=ki.get_kb_id())


@ki.answer("contract")
def _answer_contract(ki_id, bindings: List[KEFlexContractQuery]) -> List[KEFlexContract]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_contracts
    return get_contracts(kb_id=ki.get_kb_id(), query=bindings)


###############


# verify market interaction todo:
@ki.post("capacity-market-price")
def _post_market_price():
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_prices
    return get_prices()


@ki.answer("capacity-market-price")
def _answer_market_price() -> List[MarketPrice]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_prices
    return get_prices()


def post_market_price():
    resp_bindings: KIPostResponse = _post_market_price()
    # todo:


def post_contract(contract_ack: List[KEFlexContractACK]):
    ack_resp_bindings: KIPostResponse = _post_contract_ack(contract_ack)
    resp_bindings: KIPostResponse = _post_contract()
    pass
    # todo: implement


def post_current_flex_request():
    resp_bindings: KIPostResponse = _post_flex_request()
    # resp_bindings.exchangeInfo[0].knowledgeBaseId
    # todo: process post output
