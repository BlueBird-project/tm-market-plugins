from typing import List, Optional, Dict

from effi_onto_tools.db import TimeSpan
from fastapi import APIRouter

from tm_entso_e.schemas.market import Market, MarketOfferDetails, MarketOfferValues, MarketOfferValuesState

router = APIRouter(prefix="")


@router.get("/market")
async def list_markets() -> List[Market]:
    from tm_entso_e.modules.entsoe_api import service
    return service.list_markets()


@router.get("/market/{market_id}/offer")
async def get_market_offer(market_id: int, ts_from: Optional[int] = None, ts_to: Optional[int] = None,
                           ) -> List[MarketOfferValues]:
    from tm_entso_e.modules.entsoe_api import service
    ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
    return service.get_offer(market_id=market_id, ts=ts)


@router.post("/market/country/{country_name}/update", description="Synchronous offer update ")
async def update_market_offer(country_name: str,
                              ts_from: Optional[int] = None, ts_to: Optional[int] = None) -> Optional[str]:
    from tm_entso_e.modules.entsoe_api import service
    ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
    return service.update_offer(country_name=country_name, ts=ts)


@router.get("/market/{market_id}/verify", description="verify downloaded data")
@router.get("/market/country/{country_name}/verify", description="verify downloaded data")
@router.get("/market/verify", description="verify downloaded data")
async def verify_data(market_id: Optional[int]=None,country_name: Optional[str]=None,
                      ts_from: Optional[int] = None, ts_to: Optional[int] = None) -> List[MarketOfferValuesState]:
    from tm_entso_e.modules.entsoe_api import service
    ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
    return service.verify_offer(market_location=country_name,market_id=market_id, ts=ts)


@router.post("/market/country/job/{country_name}", description="Async update  country offer")
async def update_market_offer_bg(country_name: str,
                                 ts_from: Optional[int] = None, ts_to: Optional[int] = None,
                                 override_running_job: bool = False) -> Optional[Dict]:
    from tm_entso_e.modules.entsoe_api import service
    ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
    return service.update_offer(country_name=country_name, ts=ts, bg=True, override=override_running_job)


@router.get("/market/country/job/state", description="Get job state")
async def update_market_offer_bg() -> Optional[Dict]:
    from tm_entso_e.modules.entsoe_api import service
    return service.update_job_state()


# @router.get("/")
# @router.get("")
# async def list_extended_offer(ts_from: Optional[int] = None, ts_to: Optional[int] = None,
#                               granularity: Optional[int] = None,):
#     return service.list_extended_offer(ts=TimeSpan(ts_from=ts_from, ts_to=ts_to), granularity=granularity)


# @router.get("/market/{market_id}/offerinfo")
# async def get_market_offer_info(market_id: int, ts_from: Optional[int] = None, ts_to: Optional[int] = None,
#                                 granularity: Optional[int] = None) -> List[EnergyMarketOfferInfo]:
#     from tm.modules.tm_api import service
#     ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
#     return service.list_offer_info(market_id=market_id, ts=ts, granularity=granularity)


@router.get("/current/offerinfo")
async def get_current_offer_info() -> List[MarketOfferDetails]:
    from tm_entso_e.modules.entsoe_api import service
    return service.list_recent_offer()

# @router.get("/market/{market_id}/offer")
# async def get_market_offer(market_id: int, ts_from: Optional[int] = None, ts_to: Optional[int] = None,
#                            granularity: Optional[int] = None) -> List[EnergyMarketOffer]:
#     from tm.modules.tm_api import service
#     ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
#     return service.list_offer(market_id=market_id, ts=ts, granularity=granularity)


# @router.get("/offer/", deprecated=True)
# async def list_offer(ts_from: Optional[int] = None, ts_to: Optional[int] = None,
#                      granularity: Optional[int] = None) -> List[EnergyMarketOfferInfo]:
#     from tm.modules.tm_api import service
#     ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
#     return service.list_offer_info(market_id=None, ts=ts, granularity=granularity)


# @router.get("/offer/{offer_id}")
# async def get_offer(offer_id: int) -> List[EnergyMarketOffer]:
#     from tm.modules.tm_api import service
#     return service.get_offer(offer_id=offer_id)


# @router.get("/range")
# async def get_range(min_value: Optional[float] = None, max_value: Optional[float] = None) -> Optional[RangeInfo]:
#     from tm.modules.tm_api import service
#     return service.get_range(min_value=min_value, max_value=max_value)
#
#
# @router.post("/range")
# async def add_range(min_value: Optional[float] = None, max_value: Optional[float] = None) -> RangeInfo:
#     from tm.modules.tm_api import service
#     return service.add_range(min_value=min_value, max_value=max_value)
