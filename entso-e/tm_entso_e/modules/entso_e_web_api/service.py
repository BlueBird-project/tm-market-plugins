import logging

from isodate import parse_duration

from tm_entso_e.modules.entso_e_web_api.api_model import MarketDocument
from tm_entso_e.schemas.market import Market, MarketOfferDetails, MarketOffer
from tm_entso_e.utils import time_utils, TimeSpan
from tm_entso_e.modules.entso_e_web_api.energy_api import MarketAPI

market_api: MarketAPI


def init_service(market_prefix: str):
    global market_api
    from tm_entso_e.modules.entso_e_web_api import init_db

    init_db(market_prefix=market_prefix)
    market_api = MarketAPI(market_uri_prefix=market_prefix)


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
    market = dao_manager.market_dao.get_market_uri(market_uri=market_uri)
    # if market is none log  error todo:
    for ts in market_offer.timeseries:
        for period in ts.periods:
            period_minutes = int(parse_duration(period.resolution, as_timedelta_if_possible=True).total_seconds() / 60)
            period_ms = period_minutes * 60 * 1000
            ts_start = time_utils.xsd_to_ts(period.time_interval.start)
            logging.info(f"Store offers for: {market_uri},{ts_start}:{ts.sequence}")
            sequence =  ts.sequence # if ts.sequence is not None else None
            offer_details = dao_manager.offer_dao.get_offer_details(market_id=market.market_id,
                                                                    ts_start=ts_start, sequence=sequence)

            if offer_details is None:
                offer_details = MarketOfferDetails(market_id=market.market_id, sequence=sequence,
                                                   currency_unit=ts.currency_unit,
                                                   volume_unit=ts.measurement_unit, ts_start=ts_start,
                                                   ts_end=time_utils.xsd_to_ts(period.time_interval.end),
                                                   isp_unit=period_minutes)
                offer_details = dao_manager.offer_dao.register_day_offer(offer_details=offer_details)
            else:
                # todo: if override previous
                dao_manager.offer_dao.clear_offer(offer_id=offer_details.offer_id)
                # else log something and return
            market_offers = [MarketOffer(
                ts=ts_start + p.position * period_ms, offer_id=offer_details.offer_id, isp_start=p.position,
                isp_len=(period.points[i + 1].position - p.position if i < (len(period.points) - 1) else 1),
                cost=p.price
            ) for i, p in enumerate(period.points)]
            db_resp = dao_manager.offer_dao.log_day_offer(market_offers=market_offers)
