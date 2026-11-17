import logging
from threading import Thread
from typing import List

from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse

from tm_capacity_pl.contract.modules.ke_interaction.interactions.capacity_market_model import MarketPrice, \
    BaselineRequest, Baseline, BaselineDateResponse, BaselineDateRequest, KEFlexRequest, KEFlexOffer, \
    KEFlexPriceOffer
from tm_capacity_pl.shared.ke_interaction.contract import KEFlexContractQuery, KEFlexContractACK, KEFlexContract

ki = KIHolder()


@ki.post("flex-request")
def _post_flex_request() -> List[KEFlexRequest]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_flex_request
    return get_flex_request(kb_id=ki.get_kb_id())


@ki.answer("flex-request")
def _get_flex_request(kb_id: str, bindings: List) -> List[KEFlexRequest]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_flex_request
    return get_flex_request(kb_id=ki.get_kb_id())


@ki.answer("baseline-request")
def _get_required_days(kb_id: str, bindings: List[BaselineDateRequest]) -> List[BaselineDateResponse]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_baseline_required_dates
    return get_baseline_required_dates(kb_id=ki.get_kb_id(), bindings=bindings)


# @ki.react("baseline")
# def _calc_baseline(kb_id: str, bindings: List[BaselineRequest]) -> List[Baseline]:
#     from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import calc_baseline
#     return calc_baseline(bindings=bindings)

@ki.post("baseline-response")
def _post_baseline(bindings: List[BaselineRequest]) -> List[Baseline]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import calc_baseline
    print(f"baseline-response: input biding: {len(bindings)}")
    baseline = calc_baseline(bindings=bindings)
    print(f"baseline-response: baseline: {len(baseline)}")
    return baseline


@ki.react("baseline")
def _calc_baseline(kb_id: str, bindings: List[BaselineRequest]):
    def _t():
        resp: KIPostResponse = _post_baseline(bindings=bindings)
        logging.info(f"baseline response {[c.knowledgeBaseId for c in resp.exchangeInfo]}")

    t = Thread(target=_t)
    t.start()
    return []


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


#  todo: market prices
@ki.post("capacity-market-price")
def _post_market_price():
    # todo: move to other service?
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_prices
    return get_prices()


@ki.answer("capacity-market-price")
def _answer_market_price() -> List[MarketPrice]:
    from tm_capacity_pl.contract.modules.ke_interaction.service.capacity_service import get_prices
    return get_prices()


# def post_market_price():
#     resp_bindings: KIPostResponse = _post_market_price()
#     todo
#     # todo:


def post_contract(contract_ack: List[KEFlexContractACK]):
    ack_resp_bindings: KIPostResponse = _post_contract_ack(contract_ack)
    resp_bindings: KIPostResponse = _post_contract()
    pass
    # todo: implement , check KE response, process post output


def post_current_flex_request() -> List[str]:
    resp_bindings: KIPostResponse = _post_flex_request()
    return [ei.knowledgeBaseId for ei in resp_bindings.exchangeInfo]
