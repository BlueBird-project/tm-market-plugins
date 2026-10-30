import logging
import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import List, Iterable, Dict, Set
from zoneinfo import ZoneInfo

import pytz
from apscheduler.schedulers.base import BaseScheduler

__TIME_ZONE__ = ZoneInfo("Europe/Warsaw")

from ke_client.utils import to_json

from tm_entso_e.modules.entso_e_web_api.model import MarketAgreementTypeCode, MarketTypeInfo
from tm_entso_e.modules.ke_interaction.interactions.dam_model import MarketURI
from tm_entso_e.schemas.service_log import ServiceLogDAO, ERROR_TAG
from tm_entso_e.utils import time_utils, TimeSpan

max_attempts = 3


@dataclass(frozen=True)
class JobMeta:
    market_type_code: str
    market_eic_code: str
    market_type_info: MarketTypeInfo
    ts_from: int
    ts_to: int


# region helpers
def hash_set(objects: Set[JobMeta]):
    return hash(frozenset(objects))


def _init_retry_check_offer_job(attempt, scheduler: BaseScheduler, job_meta: Iterable[JobMeta]):
    logging.info("Start init_retry_check_offer_job")

    def retry_check_offer_job():
        from tm_entso_e.core.db.postgresql import dao_manager

        logging.info(f"Start retry_check_offer_job({attempt})")
        dao_manager.log_api.log(ServiceLogDAO(log_tag="INFO", log_message="START: retry offer check",
                                              log_ts=time_utils.current_timestamp()))
        errors = check_offer(job_meta=job_meta)
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
            start_retry_job(attempt=attempt, scheduler=scheduler, errors=errors)
        else:
            logging.info(f"Start retry_check_offer_job({attempt}) finished successfully ")

    return retry_check_offer_job


def _init_check_offer_job(job_meta: Iterable[JobMeta], scheduler: BaseScheduler):
    def check_offer_job():
        # current_ts = time_utils.current_timestamp()
        # last_day = TimeSpan.last_day()
        # current_day = TimeSpan(ts_from=last_day.ts_to, ts_to=last_day.ts_to + DAY_MS)
        errors: Set[JobMeta] = check_offer(job_meta=job_meta)
        # errors_current: Set[JobMeta] = check_offer(job_meta=job_meta )
        # errors.update(errors_current)
        if errors:
            start_retry_job(attempt=0, scheduler=scheduler, errors=errors)

    return check_offer_job


# endregion

def check_offer(job_meta: Iterable[JobMeta]) -> Set[JobMeta]:
    from tm_entso_e.core.db.postgresql import dao_manager
    from tm_entso_e.modules.entso_e_web_api.config import api_settings
    err_markets: Set[JobMeta] = set()
    from tm_entso_e.modules.entso_e_web_api.service import subscribe_offer
    dao_manager.log_api.log(ServiceLogDAO(log_tag="INFO", log_message="START: check_offer",
                                          log_ts=time_utils.current_timestamp()))
    logging.info("START: check_offer")
    # next day
    for market_metadata in job_meta:
        try:
            time_interval = TimeSpan(ts_from=market_metadata.ts_from, ts_to=market_metadata.ts_to)

            market_uri = MarketURI(eic_area=market_metadata.market_eic_code,
                                   market_code=market_metadata.market_type_code).uri
            market = dao_manager.market_api.get_market_uri(market_uri)
            offers = dao_manager.offer_api.get_ongoing_market_offer(ti=time_interval, market_id=market.market_id)
            area = api_settings.get_subscribed_area_by_code(eic_area_code=market_metadata.market_eic_code)
            number_of_types = area.number_of_types(
                market_type_name=area.get_market_type_name(market_metadata.market_type_code))
            expected_offer_count = time_interval.time_span_day * number_of_types
            # TODO check timezone
            if expected_offer_count == len(offers):
                logging.info(
                    f"market:{market.market_id} - expected_offer_count == len(offers) continue checking offers")
                continue  # market is up to date
            else:
                if market_metadata.market_type_info.is_publish_timeout:
                    dao_manager.log_api.log(ServiceLogDAO(log_tag="WARNING", log_message="Market offer is delayed",
                                                          log_ts=time_utils.current_timestamp(),
                                                          log_obj_type=f"{JobMeta.__module__}.{JobMeta.__name__}",
                                                          log_obj_json=to_json(market_metadata)))
                subscribe_offer(eic_code=market_metadata.market_eic_code,
                                market_type_code=market_metadata.market_type_code,
                                ti=time_interval)
                # next day
                # subscribe_offer(eic_code=market_metadata.market_eic_code,
                #                 market_type_code=market_metadata.market_type_code,
                #                 ti=TimeSpan(ts_from=current_ts, ts_to=current_ts + day_ts))
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


def start_retry_job(attempt: int, scheduler: BaseScheduler, errors: Set[JobMeta]):
    logging.info(f"Start retry job ({attempt})")
    logging.info(f"Start retry job ( [{",".join([x.market_eic_code for x in errors])}])")
    f = _init_retry_check_offer_job(attempt=attempt + 1, scheduler=scheduler, job_meta=errors)
    if attempt == 0:
        next_run = datetime.now(pytz.utc) + timedelta(seconds=15)
    else:
        next_run = datetime.now(pytz.utc) + timedelta(seconds=900)
    # next_run = datetime.now(pytz.utc) + timedelta(seconds=15)
    scheduler.add_job(f, trigger="date", next_run_time=next_run, id=f"{hash_set(errors)}_{attempt}",
                      replace_existing=True, coalesce=True)


def trigger_check_offer(service_job_scheduler: BaseScheduler):
    from tm_entso_e.modules.entso_e_web_api.config import api_settings
    ti = TimeSpan.two_day()
    jobs = []
    for eic in api_settings.subscribed_eic:
        if isinstance(eic.market_types, list):
            for market_type_code in eic.market_codes:
                job_meta = JobMeta(market_eic_code=eic.code, market_type_code=market_type_code,
                                   market_type_info=MarketTypeInfo.init_default(), ts_from=ti.ts_from, ts_to=ti.ts_to)
                jobs.append(job_meta)
        else:
            for market_type, market_type_settings in eic.market_types.items():
                market_type_code = MarketAgreementTypeCode.parse(market_type).code
                for settings in market_type_settings:
                    job_meta = JobMeta(market_eic_code=eic.code, market_type_code=market_type_code,
                                       market_type_info=settings, ts_from=ti.ts_from, ts_to=ti.ts_to)
                    jobs.append(job_meta)

    run_time = datetime.now(tz=pytz.UTC) + timedelta(seconds=5)
    # TODO: make thread safe lock starting new task?
    service_job_scheduler.add_job(_init_check_offer_job(job_meta=jobs, scheduler=service_job_scheduler), trigger='date',
                                  max_instances=1, id="trigger_check_offer", run_date=run_time)


def add_jobs(service_job_scheduler: BaseScheduler):
    logging.info("Add ENTSO-E jobs")
    time_table: Dict[str, Set[JobMeta]] = defaultdict(lambda: set())
    from tm_entso_e.modules.entso_e_web_api.config import api_settings
    ti = TimeSpan.two_day()
    for eic in api_settings.subscribed_eic:
        if isinstance(eic.market_types, list):
            for market_type_code in eic.market_codes:
                job_meta = JobMeta(market_eic_code=eic.code, market_type_code=market_type_code,
                                   market_type_info=MarketTypeInfo.init_default(), ts_from=ti.ts_from, ts_to=ti.ts_to)
                time_table["14:00"].add(job_meta)
                time_table["18:00"].add(job_meta)
        else:
            for market_type, market_type_settings in eic.market_types.items():
                market_type_code = MarketAgreementTypeCode.parse(market_type).code
                for settings in market_type_settings:
                    job_meta = JobMeta(market_eic_code=eic.code, market_type_code=market_type_code,
                                       market_type_info=settings, ts_from=ti.ts_from, ts_to=ti.ts_to)
                    time_table[settings.publish].add(job_meta)
                    time_table["18:00"].add(job_meta)
    for time, job_meta in time_table.items():
        hour_str, minutes_str = time.split(":")
        service_job_scheduler.add_job(id=str(hash_set(job_meta)),
                                      func=_init_check_offer_job(job_meta=job_meta, scheduler=service_job_scheduler),
                                      trigger="cron", day_of_week='*',
                                      hour=hour_str, minute=minutes_str, month='*', year='*', day='*', max_instances=1,
                                      coalesce=True, misfire_grace_time=30)
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
