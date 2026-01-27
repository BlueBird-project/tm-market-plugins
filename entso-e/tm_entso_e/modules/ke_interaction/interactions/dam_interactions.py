import logging
from typing import List

from effi_onto_tools.utils import time_utils
from ke_client.ki_model import KIAskResponse, KIPostResponse
from rdflib import URIRef, Literal

from tm_entso_e.modules.ke_interaction.interactions._interactions import ke_client
from tm_entso_e.modules.ke_interaction.interactions.dam_model import EnergyMarketBindingsQuery, EnergyMarketBindings
from tm_entso_e.modules.ke_interaction.service import list_markets


#
#
#
# @ke_client.answer("market-offer")
# def answer_offer_values(ki_id, bindings: List[Dict]):
#     logging.info(f"Ask arrived {ki_id}")
#     logging.debug(f"Ask arrived {ki_id}, {bindings}")
#     requests = [OfferRequest(**b) for b in bindings]
#     accu = []
#     for r in requests:
#         accu += [pnt.n3() for pnt in get_offer(r.offer_uri)]
#     return accu
#
#
# @ke_client.post("market-offer")
# def post_offer_values():
#     return [pnt.n3() for pnt in get_offer()]
#
#
# @ke_client.react("market-offer-info-query")
# def market_offer_information(ki_id, bindings):
#     logging.debug(f"Post arrived {ki_id}, {bindings}")
#     # logging.info(f"Ask arrived {ki_id}")
#     logging.debug(f"Ask arrived {ki_id}, {bindings}")
#     if len(bindings) > 0:
#         #     TODO: only one interval supported
#         q = MarketOfferInfoQuery(**bindings[0])
#         res = get_offer_info(ts_from=q.ts_from, ts_to=q.ts_to)
#         return [r.n3() for r in res]
#     else:
#         return []
#
#
# @ke_client.answer("market-offer-info")
# def market_offer_information(ki_id, bindings):
#     # logging.info(f"Ask arrived {ki_id}")
#     logging.debug(f"Ask arrived {ki_id}, {bindings}")
#     request = [MarketOfferInfoRequest(**b) for b in bindings]
#     res = [get_offer_info_by_ts(ts=r.create_ts).n3() for r in request]
#     return res
#
#
# @ke_client.post("market-offer-info")
# def publish_market_offer_information():
#     res = [get_offer_info_by_ts(ts=None).n3()]
#     return res


# @ke_client.answer("market")
# def market_information(ki_id, market_query: List[EnergyMarketBindingsQuery]):
#     return [get_market_info().n3()]


@ke_client.post("market")
def _publish_market_information(markets: List[EnergyMarketBindings]):
    return markets


def publish_market_information():
    logging.info("Publish market information")
    resp: KIPostResponse = _publish_market_information(markets=list_markets())
    return
