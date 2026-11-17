from typing import List, Optional, Dict

from effi_onto_tools.db import TimeSpan
from fastapi import APIRouter

from tm_capacity_pl.models.contract import FlexRequest, FlexPriceOffer

router = APIRouter(prefix="")


@router.post("/flex_request/init")
async def flex_request_init(ts_from: Optional[int] = None, ts_to: Optional[int] = None) -> FlexRequest:
    from tm_capacity_pl.contract.modules.rest import service
    return service.init_flex_request(ts_from=ts_from, ts_to=ts_to)


@router.get("/flex_request")
async def current_request() -> FlexRequest:
    from tm_capacity_pl.contract.modules.rest import service
    return service.get_current_request()

@router.get("/flex_offer")
async def get_current_offer() -> List[FlexPriceOffer]:
    from tm_capacity_pl.contract.modules.market.contract import current_offer

    return current_offer()


@router.post("/flex_request/publish", tags=["publish"])
async def post_current_request() -> List[str]:
    from tm_capacity_pl.contract.modules.rest import service
    return service.post_current_request()


@router.get("/contract_ack", tags=["publish"])
async def post_current_request() -> FlexRequest:
    from tm_capacity_pl.contract.modules.market.contract import confirm_current_offer
    return confirm_current_offer()

#     return service.init_contract(contract_ts=contract_ts)


# @router.post("/contract/init")
# @router.put("/contract/init/{contract_ts}")
# async def contract_init(contract_ts: Optional[int]) -> ContractDAO:
#     # TODO start contract background job
#     from tm_capacity_pl.contract.modules.rest import service
#     return service.init_contract(contract_ts=contract_ts)


# @router.post("/baseline/calc/contract/{contract_ts}")
# async def contract_init(contract_ts: int) -> List[BaselineDAO]:
#     # TODO start contract background job
#     from tm_capacity_pl.contract.modules.rest import service
#     return service.calc_baseline(contract_id=contract_ts)
#
#
# @router.post("/baseline/calc/contract/{contract_ts}/ack")
# async def contract_init(contract: ContractDAO) -> List[BaselineDAO]:
#     # TODO start contract background job
#     from tm_capacity_pl.contract.modules.rest import service
#     return service.ack_contract(contract=contract)

# @router.get("/market/{market_id}/offer")
# async def get_market_offer(market_id: int, ts_from: Optional[int] = None, ts_to: Optional[int] = None,
#                            ) -> List[MarketOfferValues]:
#     from tm_entso_e.modules.entsoe_api import service
#     ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
#     return service.get_offer(market_id=market_id, ts=ts)

#
# @router.post("/market/country/{country_name}/update", description="Synchronous offer update ")
# async def update_market_offer(country_name: str,
#                               ts_from: Optional[int] = None, ts_to: Optional[int] = None) -> Optional[str]:
#     from tm_entso_e.modules.entsoe_api import service
#     ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
#     return service.update_offer(country_name=country_name, ts=ts)
#
#
# @router.get("/market/{market_id}/verify", description="verify downloaded data")
# @router.get("/market/country/{country_name}/verify", description="verify downloaded data")
# @router.get("/market/verify", description="verify downloaded data")
# async def verify_data(market_id: Optional[int]=None,country_name: Optional[str]=None,
#                       ts_from: Optional[int] = None, ts_to: Optional[int] = None) -> List[MarketOfferValuesState]:
#     from tm_entso_e.modules.entsoe_api import service
#     ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
#     return service.verify_offer(market_location=country_name,market_id=market_id, ts=ts)
#
#
# @router.post("/market/country/job/{country_name}", description="Async update  country offer")
# async def update_market_offer_bg(country_name: str,
#                                  ts_from: Optional[int] = None, ts_to: Optional[int] = None,
#                                  override_running_job: bool = False) -> Optional[Dict]:
#     from tm_entso_e.modules.entsoe_api import service
#     ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
#     return service.update_offer(country_name=country_name, ts=ts, bg=True, override=override_running_job)
#
#
# @router.get("/market/country/job/state", description="Get job state")
# async def update_market_offer_bg() -> Optional[Dict]:
#     from tm_entso_e.modules.entsoe_api import service
#     return service.update_job_state()
#
#
