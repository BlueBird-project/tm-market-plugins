import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import List, Iterable, Dict, Set
from zoneinfo import ZoneInfo

import pytz
from apscheduler.schedulers.base import BaseScheduler
from effi_onto_tools.db import TimeSpan

__TIME_ZONE__ = ZoneInfo("Europe/Warsaw")

from ke_client.utils import to_json

from tm_entso_e.modules.entso_e_web_api.model import MarketAgreementTypeCode, SubscribedEIC, MarketTypeInfo
from tm_entso_e.schemas.service_log import ServiceLogDAO, ERROR_TAG
from tm_entso_e.utils import time_utils


@dataclass(frozen=True)
class JobMeta:
    market_type_code: str
    market_eic_code: str
    market_type_info: MarketTypeInfo


def check_offer(job_meta: Iterable[JobMeta], current_ts: int, last_day: TimeSpan) -> Set[JobMeta]:
    from tm_entso_e.core.db.postgresql import dao_manager
    err_markets: Set[JobMeta] = set()
    from tm_entso_e.modules.entso_e_web_api.service import subscribe_offer
    dao_manager.log_api.log(ServiceLogDAO(log_tag="INFO", log_message="START: check_offer",
                                          log_ts=time_utils.current_timestamp()))
    logging.info("START: check_offer")
    # TODO check what time interval requries ENTSOE api (past or future) for the day ahead offer
    # next day
    day_ts = 24 * 3600 * 1000
    for market_metadata in job_meta:
        try:
            # TODO check timezone
            if market_metadata.market_type_info.is_publish_timeout:
                dao_manager.log_api.log(ServiceLogDAO(log_tag="WARNING", log_message="Market offer is delayed",
                                                      log_ts=time_utils.current_timestamp(),
                                                      log_obj_type=f"{JobMeta.__module__}.{JobMeta.__name__}",
                                                      log_obj_json=to_json(market_metadata)))
            subscribe_offer(eic_code=market_metadata.market_eic_code,
                            market_type_code=market_metadata.market_type_code,
                            ti=last_day)
            # next day
            subscribe_offer(eic_code=market_metadata.market_eic_code,
                            market_type_code=market_metadata.market_type_code,
                            ti=TimeSpan(ts_from=current_ts, ts_to=current_ts + day_ts))
            dao_manager.log_api.log(ServiceLogDAO(log_tag="INFO", log_message="Read market success",
                                                  log_ts=time_utils.current_timestamp(),
                                                  log_obj_type=f"{JobMeta.__module__}.{JobMeta.__name__}",
                                                  log_obj_json=to_json(market_metadata),
                                                  log_context=str(hash(market_metadata)))
                                    )
        except Exception as ex:
            logging.error(f"subscribe_offer job  failed {ex}")
            dao_manager.log_api.log(ServiceLogDAO(log_tag=ERROR_TAG, log_message=f"Failed to read market offer: {ex}",
                                                  log_ts=time_utils.current_timestamp(),
                                                  log_obj_type=f"{JobMeta.__module__}.{JobMeta.__name__}",
                                                  log_obj_json=to_json(market_metadata),
                                                  log_context=str(hash(market_metadata)))
                                    )
            err_markets.add(market_metadata)
    return err_markets


max_attempts = 3


def start_retry_job(attempt: int, scheduler: BaseScheduler, errors: Set[JobMeta], current_ts: int,
                    last_day: TimeSpan):
    logging.info(f"Start retry job ({attempt})")
    logging.info(f"Start retry job ( [{",".join([x.market_eic_code for x in errors])}])")
    f = init_retry_check_offer_job(attempt=attempt + 1, scheduler=scheduler, job_meta=errors,
                                   current_ts=current_ts, last_day=last_day)
    next_run = datetime.now(pytz.utc) + timedelta(seconds=900)
    # next_run = datetime.now(pytz.utc) + timedelta(seconds=15)

    scheduler.add_job(
        f,
        trigger="date",
        next_run_time=next_run,
        id=f"{hash_set(errors)}_{attempt}",
        replace_existing=True,
        coalesce=True
    )


def init_retry_check_offer_job(attempt, scheduler: BaseScheduler, job_meta: Iterable[JobMeta], current_ts: int,
                               last_day: TimeSpan):
    logging.info("Start init_retry_check_offer_job")

    def retry_check_offer_job():
        from tm_entso_e.core.db.postgresql import dao_manager

        logging.info(f"Start retry_check_offer_job({attempt})")
        dao_manager.log_api.log(ServiceLogDAO(log_tag="INFO", log_message="START: retry offer check",
                                              log_ts=time_utils.current_timestamp()))
        errors = check_offer(job_meta=job_meta, current_ts=current_ts, last_day=last_day)
        if errors:
            if attempt >= max_attempts:
                dao_manager.log_api.log(
                    ServiceLogDAO(log_tag=ERROR_TAG, log_message=f"Missing markets: Max retries exhausted",
                                  log_ts=time_utils.current_timestamp(),
                                  log_obj_json=to_json({"missing_markets": [f"{x.market_eic_code}:{x.market_eic_code}"
                                                                            for x in errors]})))
                logging.error(
                    f"missing markets: [{",".join([x.market_eic_code for x in errors])}]. Max retries exhausted")
                return
            start_retry_job(attempt=attempt, scheduler=scheduler, errors=errors, current_ts=current_ts,
                            last_day=last_day)

    return retry_check_offer_job


def _init_check_offer_job(job_meta: Iterable[JobMeta], scheduler: BaseScheduler):
    def check_offer_job():
        current_ts = time_utils.current_timestamp()
        last_day = TimeSpan.last_day()

        errors: Set[JobMeta] = check_offer(job_meta=job_meta, current_ts=current_ts, last_day=last_day)
        if errors:
            start_retry_job(attempt=0, scheduler=scheduler, errors=errors, current_ts=current_ts, last_day=last_day)

    return check_offer_job


def hash_set(objects: Set[JobMeta]):
    return hash(frozenset(objects))


def add_jobs(service_job_scheduler: BaseScheduler):
    logging.info("Add ENTSO-E jobs")
    time_table: Dict[str, Set[JobMeta]] = defaultdict(lambda: set())
    from tm_entso_e.modules.entso_e_web_api.config import api_settings
    for eic in api_settings.subscribed_eic:
        if isinstance(eic.market_types, list):
            for market_type_code in eic.market_codes:
                job_meta = JobMeta(market_eic_code=eic.code, market_type_code=market_type_code,
                                   market_type_info=MarketTypeInfo.init_default())
                time_table["14:00"].add(job_meta)
                time_table["18:00"].add(job_meta)
        else:
            for market_type, market_type_settings in eic.market_types.items():
                market_type_code = MarketAgreementTypeCode.parse(market_type).code
                for settings in market_type_settings:
                    job_meta = JobMeta(market_eic_code=eic.code, market_type_code=market_type_code,
                                       market_type_info=settings)
                    time_table[settings.publish].add(job_meta)
                    time_table["18:00"].add(job_meta)
    for time, job_meta in time_table.items():
        hour_str, minutes_str = time.split(":")
        service_job_scheduler.add_job(id=str(hash_set(job_meta)),
                                      func=_init_check_offer_job(job_meta=job_meta, scheduler=service_job_scheduler),
                                      trigger="cron", day_of_week='*',
                                      hour=hour_str, minute=minutes_str, month='*', year='*', day='*', max_instances=1,
                                      coalesce=True, misfire_grace_time=30)
        # # todo: remove call
        # _init_check_offer_job(job_meta=job_meta, scheduler=service_job_scheduler)()

    from datetime import datetime, timedelta

    @service_job_scheduler.scheduled_job(trigger='date', id='entso_e_check_offer_job_init',
                                         run_date=(datetime.now(tz=__TIME_ZONE__) + timedelta(seconds=30)),
                                         coalesce=True)
    def check_offer_job_init():
        from tm_entso_e.modules.entso_e_web_api.service import subscribe_data
        from tm_entso_e.core.db.postgresql import dao_manager
        logging.info("START: check_offer_job_init")
        dao_manager.log_api.log(ServiceLogDAO(log_tag="INFO", log_message="START: initial offer check",
                                              log_ts=time_utils.current_timestamp()))
        # current day
        subscribe_data(ti=TimeSpan.last_day())
        # next day
        current_ts = time_utils.current_timestamp()
        day_ts = 24 * 3600 * 1000
        subscribe_data(ti=TimeSpan(ts_from=current_ts, ts_to=current_ts + day_ts))

    job = service_job_scheduler.get_job("entso_e_check_offer_job_init")
    # job.modify(next_run_time=time_utils.from_timestamp(time_utils.current_timestamp() + 30000))
    job.modify(next_run_time=(datetime.now(tz=__TIME_ZONE__) + timedelta(seconds=30)))

    # job = service_job_scheduler.get_job("tge_check_offer_job")
