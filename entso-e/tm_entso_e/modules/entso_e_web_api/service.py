import logging
import math
import threading
from datetime import datetime, timedelta

from effi_onto_tools.db.dao_exception import DAOException
from isodate import parse_duration

from tm_entso_e.modules.entso_e_web_api.api_model import MarketDocument
from tm_entso_e.modules.entso_e_web_api.errors import JobError
from tm_entso_e.schemas.market_dao import MarketOfferDetailsDAO, MarketOfferDAO
from tm_entso_e.utils import time_utils, TimeSpan
from tm_entso_e.modules.entso_e_web_api.energy_api import EnergyMarketAPI

market_api: EnergyMarketAPI


def init_service(market_prefix: str, load_data: bool, days_to_load: int = 31):
    global market_api
    from tm_entso_e.modules.entso_e_web_api import init_db
    from tm_entso_e.modules.ke_interaction.interactions import ki_client
    init_db(market_prefix=market_prefix)
    market_api = EnergyMarketAPI(market_uri_prefix=market_prefix)
    if load_data:
        logging.info(f"Load data on start")
        try:
            # subscribe_data(ti=TimeSpan.last_day())
            current_ts = time_utils.current_timestamp()
            day_ts = 24 * 3600 * 1000
            for i in range(-1, days_to_load):
                subscribe_data(
                    ti=TimeSpan(ts_from=current_ts - (day_ts * (1 + i)), ts_to=current_ts - (day_ts * (i))))
        except Exception as ex:
            logging.error(f"Failed to load data on start: {ex}")

    if ki_client.is_registered:
        from tm_entso_e.modules.ke_interaction.interactions.dam_interactions import publish_market_information
        def _publish():
            try:
                publish_market_information()
            except Exception as ex:
                logging.error(f"Failed to publish market information: {ex}")

        t = threading.Thread(target=_publish)
        t.start()
    else:
        logging.warning("KE Client is not not registered can't publish market information")


def subscribe_data(ti: TimeSpan):
    global market_api
    from tm_entso_e.modules.entso_e_web_api.config import api_settings

    for s_eic_area in api_settings.subscribed_eic:
        try:
            result = market_api.get_energy_prices(eic=s_eic_area, ti=ti)

            for market_code, market_offer in result.items():
                market_uri = market_api.get_market_uri(eic_area_code=s_eic_area.code, market_code=market_code)
                store_offers(market_uri=market_uri, market_offer=market_offer)
        except Exception as ex:
            logging.error(f"Exception {ex}, appeared while get_energy_prices for {s_eic_area.code} in {ti}")


def store_offers(market_uri: str, market_offer: MarketDocument):
    from tm_entso_e.core.db.postgresql import dao_manager
    logging.info(f"Store offers for: {market_uri}")
    market = dao_manager.market_api.get_market_uri(market_uri=market_uri)
    # if market is none log  error todo:
    for ts in market_offer.timeseries:
        for period in ts.periods:
            period_minutes = int(parse_duration(period.resolution, as_timedelta_if_possible=True).total_seconds() / 60)
            period_ms = period_minutes * 60 * 1000
            ts_start = time_utils.xsd_to_ts(period.time_interval.start)
            ts_end = time_utils.xsd_to_ts(period.time_interval.end)
            logging.info(f"Store offers for: {market_uri},{ts_start}:{ts.sequence}")
            sequence = ts.sequence  # if ts.sequence is not None else None
            offer_details = dao_manager.offer_api.get_offer_details(market_id=market.market_id,
                                                                    ts_start=ts_start, sequence=sequence)

            if offer_details is None:
                from tm_entso_e.modules.ke_interaction.interactions.dam_model import OfferUri

                offer_uri_str = OfferUri(prefix=market.market_uri, sequence=sequence, ts_start=ts_start,
                                         ts_len=ts_end - ts_start).uri
                offer_details = MarketOfferDetailsDAO(market_id=market.market_id, offer_uri=offer_uri_str,
                                                      sequence=sequence, currency_unit=ts.currency_unit,
                                                      volume_unit=ts.measurement_unit,
                                                      ts_start=ts_start, ts_end=ts_end, isp_unit=period_minutes)
                offer_details = dao_manager.offer_api.register_day_offer(offer_details=offer_details)
            else:
                # todo: if override previous
                dao_manager.offer_api.clear_offer(offer_id=offer_details.offer_id)
                # else log something and return
            market_offers = [MarketOfferDAO(
                ts=ts_start + p.position * period_ms, offer_id=offer_details.offer_id, isp_start=p.position,
                isp_len=(period.points[i + 1].position - p.position if i < (len(period.points) - 1) else 1),
                cost=p.price
            ) for i, p in enumerate(period.points)]
            dao_manager.offer_api.log_day_offer(market_offers=market_offers)


def unsubscribe_all_markets():
    from tm_entso_e.core.db.postgresql import dao_manager
    for m in dao_manager.market_api.list_market():
        dao_manager.market_api.set_subscribe(market_id=m.market_id, subscribe=False)


def get_data(ti: TimeSpan):
    from tm_entso_e.core.task_manager import service_job_scheduler
    JOB_NAME = "get_data_job"
    DAY_MS = 24 * 3600 * 1000
    MAX_DAYS = 10
    current_job = service_job_scheduler.get_job(JOB_NAME)
    if current_job:
        raise JobError(msg="Wait until previous job end")
    try:
        if (ti.ts_to - ti.ts_from) / DAY_MS > MAX_DAYS:
            raise ValueError
    except Exception as ex:
        raise Exception(f"invalid timeinterval: {ti}. Define end and start. Maximum time span is 32 days.")

    def _job():
        # TODO: check if the data is in the db, so we can avoid extra API cal
        subscribe_data(ti=ti)

    run_time = datetime.now() + timedelta(seconds=5)
    # TODO: make thread safe lock starting new task?
    service_job_scheduler.add_job(_job, trigger='date', max_instances=1, id=JOB_NAME, run_date=run_time)


def get_data_job_running() -> bool:
    from tm_entso_e.core.task_manager import service_job_scheduler
    JOB_NAME = "get_data_job"
    current_job = service_job_scheduler.get_job(JOB_NAME)
    if current_job:
        return True
    else:
        return False
