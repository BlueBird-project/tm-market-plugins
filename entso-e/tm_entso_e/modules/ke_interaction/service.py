from typing import List, Dict

from rdflib import Literal, URIRef

from tm_entso_e.core.db.postgresql import dao_manager
from tm_entso_e.modules.entso_e_web_api.model import MarketAgreementTypeCode
from tm_entso_e.modules.ke_interaction.interactions.dam_model import EnergyMarketBindings, CountryURI, \
    EnergyMarketBindingsQuery
from tm_entso_e.schemas.market import Market


#
# from ke_client.client import KEClient
# from effi_onto_tools.utils import time_utils
#
#
# def process_point(pnt: dict):
#     # isp_unit is in minutes
#     #  isp_start - isp's index
#     offset = (pnt["isp_start"]) * pnt["isp_unit"] * 60 * 1000
#     return {
#         "offer": f"<https://tge.pcss.pl/dayahead/offer/{pnt["date_str"]}>",
#         "dp": f"<https://tge.pcss.pl/dayahead/dp/{pnt["ts"]}_{pnt["isp_start"]}>",
#         "dpr": f"<https://tge.pcss.pl/dayahead/dpr/{pnt["ts"]}_{pnt["isp_start"]}>",
#         "value": pnt["cost_mwh"],
#         "timestamp": f'"{time_utils.xsd_from_ts(int(pnt["ts"] + offset))}"',
#     }
#
#
# def _extract_date_isp_from_id(ts_id: str):
#     start = len('<https://tge.pcss.pl/dayahead/offer/')
#     date_isp = ts_id[start: len(ts_id) - 1]
#     return tuple(date_isp.split("/"))
#
#
# def get_ts(ts_id: Optional[str] = None):
#     from tm.core.db.postgresql import dao_manager
#     date_str, isp_unit = None, 60 if ts_id is None else _extract_date_isp_from_id(ts_id)
#     if date_str is not None:
#         offer_points = dao_manager.day_ahead_dao.get_day_offer(date_str=date_str, isp_unit=isp_unit)
#     else:
#         ts = dao_manager.day_ahead_dao.get_offer_last_ts()
#         offer_points = dao_manager.day_ahead_dao.get_day_offer_by_ts(ts=ts, isp_unit=isp_unit)
#     if len(offer_points) > 0:
#         pnt = offer_points[0]
#         return pnt["date_str"], int(pnt["ts"])
#
#     else:
#         raise Exception("No new offers or offer is available ")
#
#
# def get_dp(ts_id: Optional[str] = None):
#     from tm.core.db.postgresql import dao_manager
#     date_str, isp_unit = None, 60 if ts_id is None else _extract_date_isp_from_id(ts_id)
#     if date_str is not None:
#         offer_points = dao_manager.day_ahead_dao.get_day_offer(date_str=date_str, isp_unit=isp_unit)
#     else:
#         ts = dao_manager.day_ahead_dao.get_offer_last_ts()
#         offer_points = dao_manager.day_ahead_dao.get_day_offer_by_ts(ts=ts, isp_unit=isp_unit)
#     if len(offer_points) > 0:
#         bindings = [process_point(pnt) for pnt in offer_points]
#         return bindings
#
#     else:
#         raise Exception("No new offers or offer is available ")
#
#
# def get_dp_bindings(bindings: Dict, ke_client: KEClient):
#     if "offer" in bindings:
#         offer_id = bindings["offer"]
#     else:
#         offer_id = None
#     bindings = get_dp(ts_id=offer_id)
#     return bindings
#
#
# def get_ts_bindings(bindings: Dict, ke_client: KEClient):
#     if "offer" in bindings:
#         offer_id = bindings["offer"]
#     else:
#         offer_id = None
#     date_str, ts = get_ts(ts_id=offer_id)
#     return {
#         "market": f"<{ke_client.kb_id}>",
#         "offer": f"<https://tge.pcss.pl/dayahead/offer/{date_str}>",
#         "offerCreationTime": f'"{time_utils.xsd_from_ts(ts)}"',
#     }

def list_markets() -> List[EnergyMarketBindings]:
    from tm_entso_e.core.db.postgresql import dao_manager
    # TODO: list only subscribed markets here
    markets: List[Market] = dao_manager.market_dao.list_market()
    from tm_entso_e.modules.entso_e_web_api.config import api_settings
    # TODO: publish all country codes not only one

    return [EnergyMarketBindings(market_uri=URIRef(m.market_uri),
                                 country_uri=CountryURI(country_name=m.market_location).uri_ref,
                                 country_name=Literal(m.market_location),
                                 market_type=MarketAgreementTypeCode.parse(m.market_type).uri_ref)
            for m in markets]


def find_markets(queries: List[EnergyMarketBindingsQuery]) -> List[EnergyMarketBindings]:
    res: Dict[str, Market] = {}
    for q in queries:
        if q.market_uri is not None:
            m = dao_manager.market_dao.get_market_uri(market_uri=q.market_uri)
            if m is not None:
                res[m.market_uri] = m
        else:
            # todo add filtering method to dao by market_type and country
            filtered = [m for m in dao_manager.market_dao.list_market() if
                        m.market_location.lower() == q.country_name.lower()]
            for m in filtered:
                res[m.market_uri] = m

    return [EnergyMarketBindings(market_uri=URIRef(m.market_uri),
                                 country_uri=CountryURI(country_name=m.market_location).uri_ref,
                                 country_name=Literal(m.market_location),
                                 market_type=MarketAgreementTypeCode.parse(m.market_type).uri_ref)
            for m in res.values()]
