from typing import List

from tm_entso_e.schemas.market import MarketOfferDetails, Market


#
def list_markets() -> List[Market]:
    from tm_entso_e.core.db.postgresql import dao_manager
    return [Market(**vars(m)) for m in dao_manager.market_api.list_market()]


def list_recent_offer() -> List[MarketOfferDetails]:
    from tm_entso_e.core.db.postgresql import dao_manager
    return [MarketOfferDetails(**vars(mo)) for mo in dao_manager.offer_api.get_recent_market_details()]

#
# def list_offer_info(market_id, ts: TimeSpan, granularity: Optional[int] = None) -> List[EnergyMarketOfferInfo]:
#     from tm.core.db.postgresql import dao_manager
#     return dao_manager.offer_dao.list_offer_info(market_id=market_id, ts=ts, isp_unit=granularity)
