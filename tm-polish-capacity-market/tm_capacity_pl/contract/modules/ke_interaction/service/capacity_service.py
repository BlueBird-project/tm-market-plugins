from datetime import timedelta
from typing import List

from isodate import duration_isoformat
from rdflib import Literal

from tm_capacity_pl.contract.modules.ke_interaction.interactions.capacity_market_interactions import post_market_ack
from tm_capacity_pl.contract.modules.ke_interaction.interactions.capacity_market_model import MarketPrice, \
    MarketOfferUri, MarketOfferDPUri, DurationURI, MarketOfferDPRUri, TMContract


def get_prices() -> List[MarketPrice]:
    from tm_capacity_pl.core import smart_client
    kb_id = smart_client.kb_id
    # todo: get data
    year = 0
    value = -1
    quarter = -1
    offer_uri = MarketOfferUri(prefix=kb_id).uri_ref
    timedelta()
    duration = Literal(
        duration_isoformat({"years": 1})
    )
    # duration=Literal(
    #     duration_isoformat({"months": 3})
    # )
    market_price = MarketPrice(offer_uri=offer_uri,
                               dp=MarketOfferDPUri(year=year, prefix=offer_uri).uri_ref,
                               dpr=MarketOfferDPRUri(year=year, prefix=offer_uri).uri_ref,
                               duration_uri=DurationURI(year=year), duration=duration, value=Literal(value)
                               )

    return [market_price]


def process_contract(contracts: List[TMContract]):
    # todo:
    # intearact with market and post ACK
    def publish_job():
        # todo:
        # market_contract_ack =
        post_market_ack([])
    return
