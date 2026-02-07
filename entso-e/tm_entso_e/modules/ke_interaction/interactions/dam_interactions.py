import logging
from typing import List

from effi_onto_tools.db import TimeSpan
from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse

from tm_entso_e.modules.ke_interaction.interactions.dam_model import EnergyMarketBindingsQuery, EnergyMarketBindings, \
    MarketOfferInfoBindings, MarketOfferInfoRequest, MarketOfferInfoFilteredRequest, \
    MarketOfferInfoFilteredBindings, MarketOfferRequest, OfferUri
from tm_entso_e.modules.ke_interaction.service import list_markets, find_markets, get_all_offer_details, \
    get_offer_details, get_market_offer
from tm_entso_e.schemas.market import MarketOffer

ki = KIHolder()


# region datapoints
@ki.answer("market-offer")
def answer_offer_values(ki_id, bindings: List[MarketOfferRequest]) -> List[MarketOffer]:
    logging.info(f"Ask offer arrived {ki_id}")
    logging.debug(f"Ask offer arrived {ki_id}, {bindings}")
    accu = []
    for b in bindings:
        # TODO: maybe include market_id in some generic offer uri
        # market_uri is prefix
        market_uri = OfferUri.get_prefix(uri=b.offer_uri)
        # print(OfferUri.parse(b.offer_uri, market_uri))

        # accu = []
        # for r in requests:
        #     accu += [pnt.n3() for pnt in get_offer(r.offer_uri)]
        dp_bindings = get_market_offer(offer_uri=b.offer_uri)
        accu += dp_bindings
    # print("answer publish: " + str(len(accu)))
    logging.info("answer publish: " + str(len(accu)))
    return accu


@ki.post("market-offer")
def _publish_market_offer() -> List[MarketOffer]:
    accu = []
    offer_infos = get_all_offer_details()
    for oi in offer_infos:
        dp_bindings = get_market_offer(offer_uri=oi.offer_uri)
        accu += dp_bindings
    # print("publish: " + str(len(accu)))
    logging.info("Market offer publish: " + str(len(accu)))
    return accu


def publish_market_offer():
    # logging.info("Publish market offer")
    # offer_details = get_all_offer_details()
    resp: KIPostResponse = _publish_market_offer()
    return


# endregion


# region offer details
@ki.post("market-offer-info")
def _publish_market_offer_information(offer_details: List[MarketOfferInfoBindings]):
    return offer_details


@ki.react("market-offer-info")
def market_offer_information(ki_id, bindings: List[MarketOfferInfoRequest]) -> List[MarketOfferInfoBindings]:
    # logging.info(f"Ask arrived {ki_id}")
    logging.debug(f"Ask arrived {ki_id}, {bindings}")
    # print(f"Ask arrived {ki_id}, {bindings}")
    if len(bindings) > 1:
        logging.warning("Supported only one query binding")
    if len(bindings) == 0:
        return get_all_offer_details()
    return get_offer_details(bindings[0])


@ki.answer("market-offer-info-filtered")
def market_offer_information(ki_id, bindings: List[MarketOfferInfoFilteredRequest]) -> \
        List[MarketOfferInfoFilteredBindings]:
    # logging.info(f"Ask arrived {ki_id}")
    logging.debug(f"Ask arrived {ki_id}, {bindings}")
    # print(f"Ask arrived {ki_id}, {bindings}")
    if len(bindings) > 1:
        logging.warning("Supported only one query binding")
    if len(bindings) == 0:
        logging.warning("Empty bindings query")
        return []
    q: MarketOfferInfoFilteredRequest = bindings[0]
    if q.ts_interval_uri is not None:
        offer_details = get_offer_details(bindings[0], ti=TimeSpan(ts_from=q.ts_from, ts_to=q.ts_to))
        resp_bindings = [MarketOfferInfoFilteredBindings(ts_interval_uri=q.ts_interval_uri, ts_date_from=q.ts_date_from,
                                                         ts_date_to=q.ts_date_to, **b.__dict__) for b in offer_details]
    else:
        offer_details = get_offer_details(bindings[0], ti=None)
        resp_bindings = [MarketOfferInfoFilteredBindings(ts_interval_uri=None, ts_date_from=None,
                                                         ts_date_to=None, **b.__dict__) for b in offer_details]
    # todo: not very efficient to reinialize this object
    return resp_bindings


def publish_market_offer_information():
    logging.info("Publish market offer details")
    offer_details = get_all_offer_details()
    resp: KIPostResponse = _publish_market_offer_information(offer_details=offer_details)
    return


# endregion

# region market ki
@ki.answer("market")
def market_information(ki_id, bindings: List[EnergyMarketBindingsQuery]):
    print("on market query")
    print(bindings)
    res = find_markets(queries=bindings)
    # print(res)
    return res


@ki.post("market")
def _publish_market_information(markets: List[EnergyMarketBindings]):
    return markets


def publish_market_information():
    logging.info("Publish market information")
    resp: KIPostResponse = _publish_market_information(markets=list_markets())
    return

# endregion
