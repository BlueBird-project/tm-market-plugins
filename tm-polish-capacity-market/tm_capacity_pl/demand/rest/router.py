from typing import List, Optional, Dict

from effi_onto_tools.db import TimeSpan
from fastapi import APIRouter

from tm_capacity_pl.models.contract import ContractDAO, BaselineDAO

router = APIRouter(prefix="")


@router.post("/notification/init")
@router.get("/notification/init")  #remove GET: TODO:
async def contract_init(contract_ts: Optional[int]) -> ContractDAO:
    # TODO start contract background job
    from tm_capacity_pl.contract.modules.rest import service
    return service.init_contract(contract_ts=contract_ts)
