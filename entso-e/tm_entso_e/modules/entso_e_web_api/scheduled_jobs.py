import logging
from zoneinfo import ZoneInfo

from apscheduler.schedulers.base import BaseScheduler
from effi_onto_tools.db import TimeSpan

__TIME_ZONE__ = ZoneInfo("Europe/Warsaw")


def add_jobs(service_job_scheduler: BaseScheduler):
    logging.info("Add ENTSO-E jobs")

    @service_job_scheduler.scheduled_job(trigger='cron', id="entso_e_check_offer_job", day_of_week='*',
                                         hour='0/8,10,13,17',
                                         minute='0', month='*', year='*', day='*', max_instances=1, coalesce=True)
    def check_offer_job():
        from tm_entso_e.modules.entso_e_web_api.service import subscribe_data
        subscribe_data(ti=TimeSpan.last_day())

    from datetime import datetime, timedelta

    @service_job_scheduler.scheduled_job(trigger='date', id='entso_e_check_offer_job_init',
                                         run_date=(datetime.now(tz=__TIME_ZONE__) + timedelta(seconds=30)))
    def check_offer_job_init():
        from tm_entso_e.modules.entso_e_web_api.service import subscribe_data
        subscribe_data(ti=TimeSpan.last_day())

    job = service_job_scheduler.get_job("entso_e_check_offer_job")
    # job.modify(next_run_time=time_utils.from_timestamp(time_utils.current_timestamp() + 30000))
    job.modify(next_run_time=(datetime.now(tz=__TIME_ZONE__) + timedelta(seconds=30)))

    # job = service_job_scheduler.get_job("tge_check_offer_job")
