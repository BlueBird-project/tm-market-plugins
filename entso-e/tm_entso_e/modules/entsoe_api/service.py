from typing import List, Optional

from effi_onto_tools.db import TimeSpan

from schemas.market import Market


#
# def list_markets() -> List[EnergyMarket]:
#     from tm.core.db.postgresql import dao_manager
#     return dao_manager.market_dao.list_market()

#
# def list_offer_info(market_id, ts: TimeSpan, granularity: Optional[int] = None) -> List[EnergyMarketOfferInfo]:
#     from tm.core.db.postgresql import dao_manager
#     return dao_manager.offer_dao.list_offer_info(market_id=market_id, ts=ts, isp_unit=granularity)


def add_market(market: Market) -> Market:
    from core.db.postgresql import dao_manager
    return dao_manager.market_dao.add_market(market=market)
