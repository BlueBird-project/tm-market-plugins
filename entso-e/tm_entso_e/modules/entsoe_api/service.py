import logging
from datetime import datetime, timedelta
from time import sleep
from typing import List, Optional, Dict
from zoneinfo import ZoneInfo

from apscheduler.job import Job
from effi_onto_tools.db import TimeSpan
from fastapi import HTTPException

from tm_entso_e.core.task_manager import service_job_scheduler
from tm_entso_e.modules.entso_e_web_api.model import SubscribedEIC
from tm_entso_e.modules.entso_e_web_api.service import subscribe_eic_data
from tm_entso_e.schemas.market import MarketOfferDetails, Market, MarketOfferValues, MarketOfferValuesState

day_ts = 24 * 3600 * 1000
__TIME_ZONE__ = ZoneInfo("Europe/Warsaw")


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


def _update_offer(s_eic_area: SubscribedEIC, ts: TimeSpan, bg: bool = False):
    # subscribe_data(ti=TimeSpan.last_day())
    from tm_entso_e.core.db.postgresql import dao_manager
    ts_from = ts.ts_from
    ts_to = ts_from + day_ts
    total_days = (ts.ts_to - ts.ts_from) / day_ts
    current_day = 0
    if bg:
        dao_manager.settings_api.set("entsoe_job_progress", f"0.0")
    while ts_from < ts.ts_to:
        subscribe_eic_data(s_eic_area=s_eic_area, ti=TimeSpan(ts_from=ts_from, ts_to=ts_to))
        ts_from += day_ts
        ts_to = ts_from + day_ts
        current_day += 1
        if bg:
            dao_manager.settings_api.set("entsoe_job_progress",
                                         f"{min(round(current_day * 100.0 / total_days, 2), 100.0)}")
        print(f"Progress: {min(round(current_day * 100.0 / total_days, 2), 100.0)}")

        sleep(1)

    print(f"Job end: {min(current_day * 100.0 / total_days, 100.0)}")
    if bg:
        dao_manager.settings_api.set("entsoe_job_progress", "100.0")


def update_job_state() -> Dict:
    from tm_entso_e.core.db.postgresql import dao_manager
    return {
        "entsoe_job_state": dao_manager.settings_api.get("entsoe_job_state"),
        "entsoe_job_country": dao_manager.settings_api.get("entsoe_job_country"),
        "entsoe_job_progress": dao_manager.settings_api.get("entsoe_job_progress")}


def verify_offer(market_location: Optional[str], market_id: Optional[int], ts: TimeSpan ) -> List[MarketOfferValuesState]:

    from tm_entso_e.core.db.postgresql import dao_manager
    if market_id is not None:
        market=dao_manager.market_api.get_market(market_id=market_id)
        if market is None:
            raise HTTPException(status_code=404, detail="Market not found")
    return dao_manager.offer_api.verify_stored_offers(ti=ts,market_id=market_id,market_location=market_location)
def update_offer(country_name: str, ts: TimeSpan, bg: bool = False, override: bool = False) -> Optional[Dict]:
    from tm_entso_e.modules.entso_e_web_api.config import api_settings
    from tm_entso_e.modules.entso_e_web_api.model import SubscribedEIC
    from tm_entso_e.core import app_settings
    s_eic_area: SubscribedEIC = api_settings.get_subscribed_area(country=country_name)
    if s_eic_area is None:
        raise HTTPException(status_code=404, detail="EIC are not found")
    if (ts.ts_to - ts.ts_from) > day_ts * 180:
        raise HTTPException(status_code=400, detail="Too long time range (maximum allowed: 180d")
    logging.info(f"Load data: {bg}")
    if bg:
        if not app_settings.use_scheduler:
            raise HTTPException(status_code=400, detail="Scheduler is not configured")

        def _update_offer_job():
            dao_manager.settings_api.set("entsoe_job_state", "started")
            try:
                _update_offer(s_eic_area=s_eic_area, ts=ts, bg=True)
            except Exception as ex:
                logging.error(f"Error {ex} occurred while running update job.")
            dao_manager.settings_api.set("entsoe_job_state", None)

            # job: Job = service_job_scheduler.get_job(job_id="entsoe_update_demand")

        from tm_entso_e.core.db.postgresql import dao_manager
        # print(f"job: {job}")

        if override or not dao_manager.settings_api.get("entsoe_job_state"):
            dao_manager.settings_api.set("entsoe_job_state", "preparing")
            dao_manager.settings_api.set("entsoe_job_country", country_name)
            dao_manager.settings_api.set("entsoe_job_progress", None)
            service_job_scheduler.add_job(id="entsoe_update_demand", trigger='date',
                                          run_date=(datetime.now(tz=__TIME_ZONE__) + timedelta(seconds=120)),
                                          func=_update_offer_job, max_instances=1, coalesce=True)
            job: Job = service_job_scheduler.get_job(job_id="entsoe_update_demand")
            # next_run_time = time_utils.from_timestamp(time_utils.current_timestamp() + 1000)
            # job.modify(next_run_time=(datetime.now() + timedelta(seconds=5)))
            job.modify(next_run_time=(datetime.now(tz=__TIME_ZONE__) + timedelta(seconds=1)))
        return update_job_state()

    else:
        if app_settings.use_scheduler:
            job: Job = service_job_scheduler.get_job("entsoe_update_demand")
            if job is not None:
                raise HTTPException(status_code=400, detail="Job has been already scheduled")

        _update_offer(s_eic_area=s_eic_area, ts=ts, bg=True)
        return {}
