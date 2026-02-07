import logging

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.base import BaseScheduler
from pytz import utc

executors = {
    'default': ThreadPoolExecutor(5)
    # 'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': True,
    'max_instances': 1
}
service_job_scheduler: BaseScheduler


def init(bg=True):
    global service_job_scheduler
    if bg:
        from apscheduler.schedulers.background import BackgroundScheduler
        service_job_scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults, timezone=utc)
    else:
        from apscheduler.schedulers.background import BlockingScheduler
        service_job_scheduler = BlockingScheduler(executors=executors, job_defaults=job_defaults, timezone=utc)


def setup_scheduler():
    from tm_entso_e.core import app_settings
    global service_job_scheduler
    logging.info("INIT task scheduler")

    if app_settings.use_rest_api:
        init(bg=True)
    else:
        print("Start sync scheduler")
        init(bg=False)
    # if app_settings.use_ke_api:
    #     from main.modules.ke_interaction import scheduled_jobs as ke_jobs

    #
    #     ke_jobs.add_jobs(service_job_scheduler)

    from tm_entso_e.modules.entso_e_web_api import scheduled_jobs as entsoe_e_jobs
    from tm_entso_e.modules.ke_interaction import scheduled_jobs as ke_jobs
    entsoe_e_jobs.add_jobs(service_job_scheduler)
    ke_jobs.add_jobs(service_job_scheduler)
    service_job_scheduler.start()
    service_job_scheduler.get_jobs()
