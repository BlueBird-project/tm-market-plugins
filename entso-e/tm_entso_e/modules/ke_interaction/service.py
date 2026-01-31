from datetime import timedelta
from typing import List, Dict, Optional

from isodate import duration_isoformat
from rdflib import Literal, URIRef

from tm_entso_e.modules.entso_e_web_api.model import MarketAgreementTypeCode
from tm_entso_e.modules.ke_interaction.interactions.dam_model import EnergyMarketBindings, CountryURI, \
    EnergyMarketBindingsQuery, MarketOfferInfoBindings, OfferUri, MarketOfferInfoRequest, MarketOfferBindings
from tm_entso_e.schemas.market import Market, MarketOfferDetails, MarketOffer
from tm_entso_e.utils import time_utils, TimeSpan


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
    from tm_entso_e.core.db.postgresql import dao_manager
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


def _get_offer_details_bindings(markets: Dict[int, Market], offer_details: List[MarketOfferDetails]) -> \
        List[MarketOfferInfoBindings]:
    # def offer_uri_helper(market: Market, o: MarketOfferDetails) -> OfferUri:
    #     sequence = OfferUri.__EMPTY__ if o.sequence is None else o.sequence
    #     return OfferUri(prefix=market.market_uri, sequence=sequence, ts_start=o.ts_start,
    #                     ts_len=o.ts_end - o.ts_start)

    offer_bindings = [
        MarketOfferInfoBindings(market_uri=URIRef(markets[o.market_id].market_uri),
                                market_type=MarketAgreementTypeCode.parse(markets[o.market_id].market_type).uri_ref,
                                offer_uri=URIRef(o.offer_uri),
                                # offer_uri=offer_uri_helper(market=markets[o.market_id], o=o).uri_ref,
                                sequence=o.sequence,
                                update_rate=Literal(duration_isoformat(timedelta(minutes=o.isp_unit))),
                                time_create=Literal(time_utils.xsd_from_ts(ts=o.ts_start)),
                                duration=Literal(duration_isoformat(timedelta(milliseconds=(o.ts_end - o.ts_start))))
                                )
        for o in offer_details]
    return offer_bindings


# def get_offer_details(q: MarketOfferInfoRequest):
#     from tm_entso_e.core.db.postgresql import dao_manager
#     if q.market_uri is not None:
#         market = dao_manager.market_dao.get_market_uri(market_uri=q.market_uri)
#         if market is None:
#             return []
#         offer_details = dao_manager.offer_dao.get_recent_market_details(market_id=market.market_id, sequence=q.sequence)
#         return _get_offer_details_bindings(markets={market.market_id: market}, offer_details=offer_details)
#     elif q.market_type is not None:
#         market_type = MarketAgreementTypeCode.parse(q.market_type, nullable=True)
#         if market_type is None:
#             # log invalid market_type todo:
#             return []
#         if market_type == MarketAgreementTypeCode.DAY_AHEAD:
#             offer_details = dao_manager.offer_dao.get_recent_dayahead_details(sequence=q.sequence)
#         elif market_type == MarketAgreementTypeCode.INTRADAY:
#             offer_details = dao_manager.offer_dao.get_recent_intraday_details(sequence=q.sequence)
#         else:
#             raise NotImplementedError
#         markets: Dict[int, Market] = {}
#         for od in offer_details:
#             if od.market_id not in markets:
#                 markets[od.market_id] = dao_manager.market_dao.get_market(market_id=od.market_id)
#         return _get_offer_details_bindings(markets=markets, offer_details=offer_details)
#     else:
#         return get_all_offer_details()


def get_offer_details(q: MarketOfferInfoRequest, ti: Optional[TimeSpan] = None):
    from tm_entso_e.core.db.postgresql.dao_manager import offer_dao, market_dao

    if q.market_uri is not None:
        market = market_dao.get_market_uri(market_uri=q.market_uri)
        if market is None:
            return []
        offer_details = offer_dao.get_recent_market_details(market_id=market.market_id, sequence=q.sequence) \
            if ti is None else offer_dao.find_offer_details(ti=ti, market_id=market.market_id, sequence=q.sequence)
        return _get_offer_details_bindings(markets={market.market_id: market}, offer_details=offer_details)
    elif q.market_type is not None:
        market_type = MarketAgreementTypeCode.parse(q.market_type, nullable=True)
        if market_type is None:
            # log invalid market_type todo:
            return []
        offer_details = offer_dao.get_recent_market_details(sequence=q.sequence, market_type=market_type.name) \
            if ti is None else offer_dao.find_offer_details(ti=ti, sequence=q.sequence, market_type=market_type.name)

        markets: Dict[int, Market] = {}
        for od in offer_details:
            if od.market_id not in markets:
                markets[od.market_id] = market_dao.get_market(market_id=od.market_id)
        return _get_offer_details_bindings(markets=markets, offer_details=offer_details)
    else:
        return get_all_offer_details()


def get_all_offer_details() -> List[MarketOfferInfoBindings]:
    from tm_entso_e.core.db.postgresql import dao_manager
    markets: Dict[int, Market] = {}
    offer_details: List[MarketOfferDetails] = dao_manager.offer_dao.get_recent_intraday_details()
    for od in offer_details:
        if od.market_id not in markets:
            markets[od.market_id] = dao_manager.market_dao.get_market(market_id=od.market_id)
    offer_bindings = _get_offer_details_bindings(markets=markets, offer_details=offer_details)
    offer_details: List[MarketOfferDetails] = dao_manager.offer_dao.get_recent_dayahead_details()
    for od in offer_details:
        if od.market_id not in markets:
            markets[od.market_id] = dao_manager.market_dao.get_market(market_id=od.market_id)
    offer_bindings += _get_offer_details_bindings(markets=markets, offer_details=offer_details)
    return offer_bindings


def get_market_offer(offer_uri: URIRef):
    from tm_entso_e.core.db.postgresql import dao_manager
    # market_uri = OfferUri.get_prefix(uri=offer_uri)
    # offer_uri = OfferUri.parse(uri=offer_uri, prefix=market_uri + "/")
    # market = dao_manager.market_dao.get_market_uri(market_uri=market_uri)
    # if market is None:
    #     print("no market")
    #     #   log error /warning ?
    #     return []
    # offer_details = dao_manager.offer_dao.get_offer_details(market_id=market.market_id, sequence=offer_uri.sequence,
    #                                                         ts_start=offer_uri.ts_start)
    offer_details = dao_manager.offer_dao.get_offer_details_by_uri(offer_uri=offer_uri)
    if offer_details is None:
        print("no offer")
        # todo log error /warning ?
        return []
    offer_uri = offer_details.offer_uri
    market_offer: List[MarketOffer] = dao_manager.offer_dao.get_offer(offer_id=offer_details.offer_id)
    offer_bindings = [
        MarketOfferBindings(offer_uri=URIRef(offer_uri), dp=OfferUri.uri_append_ref(offer_uri, "/dp"),
                            ts=Literal(time_utils.xsd_from_ts(mo.ts)), dpr=OfferUri.uri_append_ref(offer_uri, "/dpr"),
                            is_measured_id=Literal(offer_details.is_measured_in),
                            duration=Literal(duration_isoformat(timedelta(mo.isp_len * offer_details.isp_unit))),
                            value=Literal(mo.cost))
        for mo in market_offer]
    return offer_bindings
