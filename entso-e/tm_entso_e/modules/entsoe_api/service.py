import logging
from typing import List

from effi_onto_tools.db import TimeSpan
from fastapi import HTTPException

from tm_entso_e.schemas.market import MarketOfferDetails, Market, MarketOfferValues
from tm_entso_e.utils import time_utils


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
def get_offer(market_id: int, ts: TimeSpan) -> List[MarketOfferValues]:
    from tm_entso_e.core.db.postgresql import dao_manager
    market = dao_manager.market_api.get_market(market_id=market_id)
    if market is None:
        raise HTTPException(status_code=404, detail="Market not found")
    return dao_manager.offer_api.get_offer_values(market_id=market.market_id, ti=ts)


def update_offer(country_name: str, ts: TimeSpan):
    from tm_entso_e.modules.entso_e_web_api.service import subscribe_eic_data

    from tm_entso_e.modules.entso_e_web_api.config import api_settings
    from tm_entso_e.modules.entso_e_web_api.model import SubscribedEIC
    s_eic_area: SubscribedEIC = api_settings.get_subscribed_area(country=country_name)
    if s_eic_area is None:
        raise HTTPException(status_code=404, detail="EIC are not found")
    logging.info(f"Load data ")
    # subscribe_data(ti=TimeSpan.last_day())
    day_ts = 24 * 3600 * 1000
    ts_from = ts.ts_from
    ts_to = ts_from + day_ts
    while ts_from < ts.ts_to:
        subscribe_eic_data(s_eic_area=s_eic_area, ti=TimeSpan(ts_from=ts_from, ts_to=ts_to))
        ts_from += day_ts
        ts_to = ts_from + day_ts
