import random
from datetime import datetime
from typing import List

from ke_client.utils import time_utils
from rdflib import URIRef, Literal
from ubflex.rdf import UBFLEX_MARKET_BASE

from tm_capacity_pl.demand.ke_interaction.interactions.capacity_market_model import TMNotification
from tm_capacity_pl.demand.market.message_parser import CapacityMarketNotification


def init_message(notification: CapacityMarketNotification) -> List[TMNotification]:
    # TODO: read uris from DB
    r_int = random.randint(0, 10000)

    return [

        TMNotification(
            flex_request=URIRef(value=f"FlexRequest_{r_int}", base=UBFLEX_MARKET_BASE),
            flex_offer=URIRef(value=f"FlexOffer_{r_int}", base=UBFLEX_MARKET_BASE),
            flex_profile=URIRef(value=f"FlexPROFILE_{r_int}", base=UBFLEX_MARKET_BASE),
            flex_participant=URIRef(value=f"TM", base=UBFLEX_MARKET_BASE),
            power_limit=URIRef(value=f"PowerLimit_{r_int}", base=UBFLEX_MARKET_BASE),
            # ts=Literal(time_utils.xsd_from_ts(ts=time_utils.current_timestamp())),
            ts=notification.xsd_start_datetime,
            max_consumption=URIRef(value=f"MaxConsumption_{r_int}", base=UBFLEX_MARKET_BASE),
            max_consumption_value=Literal(notification.ratio * 100000),

        )
    ]
