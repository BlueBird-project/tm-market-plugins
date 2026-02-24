import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.base import BaseScheduler

# TODO: set time zone
__TIME_ZONE__ = ZoneInfo("Europe/Warsaw")


def add_jobs(service_job_scheduler: BaseScheduler):
    logging.info("Add KE jobs")

    # @service_job_scheduler.scheduled_job(trigger='cron', id="tge_check_offer_job", day_of_week='*', hour='13,18',
    #                                      minute='0',
    #                                      month='*', year='*', day='*', max_instances=1, coalesce=True)
    @service_job_scheduler.scheduled_job(trigger='cron', id="entsoe-markets", day_of_week='*', hour='0',
                                         minute='0',
                                         month='*', year='*', day='*', max_instances=1, coalesce=True)
    def post_markets():
        from tm_entso_e.modules.ke_interaction.interactions.dam_interactions import publish_market_information
        publish_market_information()
        # ke_client.stop()

    @service_job_scheduler.scheduled_job(trigger='cron', id="entsoe-offer-info", day_of_week='*', hour='0,7,13,15,18',
                                         minute='30',
                                         month='*', year='*', day='*', max_instances=1, coalesce=True)
    def post_offers_detailed():
        from tm_entso_e.modules.ke_interaction.interactions.dam_interactions import publish_market_offer_information
        publish_market_offer_information()

    @service_job_scheduler.scheduled_job(trigger='cron', id="tge_check_offer_job", day_of_week='*', hour='19',
                                         minute='30',
                                         month='*', year='*', day='*', max_instances=1, coalesce=True)
    def post_offers_detailed():
        from tm_entso_e.modules.ke_interaction.interactions.dam_interactions import publish_market_offer
        publish_market_offer()

    job = service_job_scheduler.get_job("entsoe-markets")

    job.modify(next_run_time=(datetime.now(tz=__TIME_ZONE__) + timedelta(seconds=300)))
