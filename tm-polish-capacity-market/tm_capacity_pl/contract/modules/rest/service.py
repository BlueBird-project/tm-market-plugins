import logging
from datetime import datetime, timedelta
from time import sleep
from typing import List, Optional, Dict
from zoneinfo import ZoneInfo

from apscheduler.job import Job
from effi_onto_tools.db import TimeSpan
from fastapi import HTTPException

from tm_capacity_pl.models import DEFAULT_MARKET_UPDATE_RATE_MS
from tm_capacity_pl.models.contract import ContractDAO, BaselineDAO, CapacityPowerDAO, Baseline


#
# day_ts = 24 * 3600 * 1000
# __TIME_ZONE__ = ZoneInfo("Europe/Warsaw")
#
#
# #
# def list_markets() -> List[Market]:
#     from tm_entso_e.core.db.postgresql import dao_manager
#     return [Market(**vars(m)) for m in dao_manager.market_api.list_market()]
#
#
# def get_offer(market_id: int, ts: TimeSpan) -> List[MarketOfferValues]:
#     from tm_entso_e.core.db.postgresql import dao_manager
#     market = dao_manager.market_api.get_market(market_id=market_id)
#     if market is None:
#         raise HTTPException(status_code=404, detail="Market not found")
#     return dao_manager.offer_api.get_offer_values(market_id=market.market_id, ti=ts)
#
#
# def update_job_state() -> Dict:
#     from tm_entso_e.core.db.postgresql import dao_manager
#     return {
#         "entsoe_job_state": dao_manager.settings_api.get("entsoe_job_state"),
#         "entsoe_job_country": dao_manager.settings_api.get("entsoe_job_country"),
#         "entsoe_job_progress": dao_manager.settings_api.get("entsoe_job_progress")}
#
#
# def verify_offer(market_location: Optional[str], market_id: Optional[int], ts: TimeSpan) -> List[
#     MarketOfferValuesState]:
#     from tm_entso_e.core.db.postgresql import dao_manager
#     if market_id is not None:
#         market = dao_manager.market_api.get_market(market_id=market_id)
#         if market is None:
#             raise HTTPException(status_code=404, detail="Market not found")
#     return dao_manager.offer_api.verify_stored_offers(ti=ts, market_id=market_id, market_location=market_location)


def init_contract(contract_ts: int) -> ContractDAO:
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    from ke_client.utils import time_utils
    contract = dao_manager.contract_api.add_contract(contract=ContractDAO(create_time=contract_ts))
    # TODO: start ke ask here for
    from tm_capacity_pl.contract.modules.ke_interaction.interactions.fm_interactions import request_data
    # TODO: round to full days , check if all data is there
    ts_now = time_utils.current_timestamp()
    ts_from = ts_now - 24 * 3600 * 100 * 10
    dp_info, datapoints = request_data(ts=TimeSpan(ts_from=ts_from, ts_to=ts_now))

    power_history = [CapacityPowerDAO(ts=dp.ts_ms, granularity_ms=DEFAULT_MARKET_UPDATE_RATE_MS, value=dp.get_value())
                     for dp in datapoints]
    inserted = dao_manager.power_api.log_power(power_history=power_history)
    if inserted != len(power_history):
        raise Exception("Fail to save power history")
    return contract


def calc_baseline(contract_id: int) -> Baseline:
    from ke_client.utils import time_utils
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    from tm_capacity_pl.contract.modules.market import baseline
    contract = dao_manager.contract_api.get_current(contract_ack=False)
    if contract is None:
        raise Exception("Contract does not exists")
    if contract.create_time != contract_id:
        raise Exception("Contract is already outdated")
    # TODO: round to full days , check if all data is there
    ts_now = time_utils.current_timestamp()
    ts_from = ts_now - 24 * 3600 * 100 * 10
    power_history = dao_manager.power_api.list_power(ts=TimeSpan(ts_from=ts_from, ts_to=ts_now))
    new_baseline = dao_manager.baseline_api.init_baseline()
    new_baseline_values = baseline.calc_baseline(baseline_id=new_baseline.baseline_id, power_history=power_history)
    dao_manager.baseline_api.set_baseline(baseline_values=new_baseline_values)
    # TODO: ask for power flexibility from FM according to the baseling  , start KE ask here ,
    dao_manager.contract_api.set_baseline(contract_id=contract.create_time, baseline_id=new_baseline.baseline_id)
    baseline = dao_manager.baseline_api.get_baseline(baseline_id=new_baseline.baseline_id)
    return baseline


def ack_contract(contract_ack: ContractDAO) -> ContractDAO:
    # todo: validate contract_ack
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    return dao_manager.contract_api.ack_contract(contract=contract_ack)
