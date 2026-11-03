from typing import List, Optional, Dict

from tm_entso_e.utils import TimeSpan
from fastapi import APIRouter

from tm_entso_e.schemas.market import Market, MarketOfferDetails, MarketOfferValues, MarketOfferValuesState, \
    MarketOfferDetailsResponse, MarketOfferValuesStateResponse

router = APIRouter(prefix="", )


@router.get("/market", description="List subscribed markets", tags=["ENTSO-E API"])
async def list_markets() -> List[Market]:
    from tm_entso_e.modules.entsoe_api import service
    return service.list_markets()


@router.get("/market/{market_id}/offer", name="Market Offer", description="List offer timeseries",
            tags=["ENTSO-E API"])
async def get_market_offer(market_id: int, ts_from: Optional[int] = None, ts_to: Optional[int] = None,
                           ) -> List[MarketOfferValues]:
    from tm_entso_e.modules.entsoe_api import service
    ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
    return service.get_offer(market_id=market_id, ts=ts)


@router.get("/market/{market_id}/offer_summary", description="Offer summary", tags=["ENTSO-E API"])
@router.get("/market/country/{country_name}/offer_summary", description="Offer summary", tags=["ENTSO-E API"])
@router.get("/market/offer_summary", description="Offer summary", tags=["ENTSO-E API"])
async def offer_summary(market_id: Optional[int] = None, country_name: Optional[str] = None,
                        ts_from: Optional[int] = None, ts_to: Optional[int] = None) -> List[MarketOfferValuesState]:
    from tm_entso_e.modules.entsoe_api import service
    ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
    return [MarketOfferValuesStateResponse.init(o) for o in
            service.verify_offer(market_location=country_name, market_id=market_id, ts=ts)]


@router.get("/current/offerdetails", description="Get current offer metadata", tags=["ENTSO-E API"])
async def get_current_offer_details() -> List[MarketOfferDetailsResponse]:
    from tm_entso_e.modules.entsoe_api import service
    return service.list_recent_offer()


# region scan
@router.post("/market/country/{country_name}/scan", tags=["Scan"],
             description="Scan for new offers within given timespan (sync) ")
async def scan_market_offer(country_name: str,
                            ts_from: Optional[int] = None, ts_to: Optional[int] = None) -> Optional[str]:
    from tm_entso_e.modules.entsoe_api import service
    ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
    return service.update_offer(country_name=country_name, ts=ts)


@router.post("/market/country/job/{country_name}", description="Async update  country offer", tags=["Scan"])
async def scan_market_offer_bg(country_name: str,
                               ts_from: Optional[int] = None, ts_to: Optional[int] = None,
                               override_running_job: bool = False) -> Optional[Dict]:
    from tm_entso_e.modules.entsoe_api import service
    ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
    return service.update_offer(country_name=country_name, ts=ts, bg=True, override=override_running_job)


@router.get("/market/country/job/state", description="Get job state", tags=["Scan"])
async def update_market_offer_bg() -> Optional[Dict]:
    from tm_entso_e.modules.entsoe_api import service
    return service.update_job_state()
# endregion
