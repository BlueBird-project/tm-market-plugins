from typing import List

from ke_client.utils import time_utils
from rdflib import Literal, URIRef

from tm_capacity_pl.models.contract import FlexPriceOffer
from tm_capacity_pl.shared import POLAND_TZ
from tm_capacity_pl.shared.ke_interaction.contract import KEFlexContractACK, ACKExecutionUri, ACKContractUri


def current_offer() -> List[FlexPriceOffer]:
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    current_request = dao_manager.contract_api.current_request()
    return dao_manager.contract_api.list_price_offer(current_request.flex_request_uri)



def confirm_current_offer(ratio: float = 1.0):
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    from tm_capacity_pl.contract.modules.ke_interaction.interactions.capacity_market_interactions import \
        post_contract
    from tm_capacity_pl.core import smart_client
    kb_id = smart_client.kb_id
    ts = time_utils.current_timestamp()
    ack_uri = ACKExecutionUri(ack_time=ts, prefix=kb_id)

    contract_ack: List[KEFlexContractACK] = []
    offers = current_offer()
    for o in offers:
        o.flex_value *= ratio
        asset_manager = dao_manager.asset_api.get_asset_manager(asset_manager_uri=o.asset_manager_uri)
        asset_manager_id = asset_manager.asset_manager_id
        contract_uri = ACKContractUri(ack_time=ts, asset_manager_id=asset_manager_id, prefix=kb_id)
        contract = KEFlexContractACK(ack_execution=ack_uri.uri_ref, asset_manager=URIRef(o.asset_manager_uri),
                                     flex_request=URIRef(o.flex_request_uri), contract=contract_uri.uri_ref,
                                     evt=ack_uri.append_ref("evt"),
                                     flex_result=ack_uri.append_ref("flex_result"),
                                     accepted_flex=Literal(o.flex_value * ratio),
                                     price_result=ack_uri.append_ref("price_result"),
                                     accepted_price=Literal(o.price_value * (1 + ratio)),
                                     ack_time=Literal(time_utils.xsd_from_ts(ts=ts, tz=POLAND_TZ))
                                     )
        dao_manager.contract_api.add_contract(contract.rdf_parse(kb_id=kb_id))
        contract_ack.append(contract)
    post_contract(contract_ack=contract_ack)
