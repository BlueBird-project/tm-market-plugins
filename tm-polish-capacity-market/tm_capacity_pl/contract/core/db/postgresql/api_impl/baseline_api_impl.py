from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm_capacity_pl.contract.core.db.api.baseline_api import BaselineAPI
from tm_capacity_pl.contract.core.db.api.contract_api import ContractAPI
from tm_capacity_pl.contract.core.db.postgresql.api_impl import QueryObject
from tm_capacity_pl.models.contract import ContractDAO, BaselineDAO


class BaselineQueries(QueryObject):
    __TABLE_NAME__ = "contract_baseline"

    __PROJECTION__ = """ ${table_alias}."contract_id",${table_alias}."baseline_start",${table_alias}."granularity_ms",
     ${table_alias}."power_span",  ${table_alias}."baseline_value", ${table_alias}."cost_mwh",
      ${table_alias}."update_time" """

    LIST_CONTRACT_BASELINE = """SELECT ${projection} FROM "${table_prefix}contract_details" as ${table_alias} 
    WHERE  ${table_alias}."contract_id" = :contract_id 
    """

    INSERT_CONTRACT_BASELINE = """INSERT INTO "${table_prefix}contract_baseline" 
    ("contract_id", "baseline_start", "granularity_ms","power_span", "baseline_value", "cost_mwh") 
    VALUES (:contract_id,:baseline_start,:granularity_ms,:power_span, :baseline_value, :cost_mwh,
    extract(epoch from now()) * 1000,:ext) 
    """

    UPDATE_CONTRACT_BASELINE = """UPDATE "${table_prefix}contract_baseline" 
    SET "baseline_start" =  :baseline_start , "granularity_ms" = :granularity_ms, "baseline_value" = :baseline_value,
    "update_ts" =  extract(epoch from now()) * 1000  
    WHERE contract_id = :contract_id and "baseline_start" = :baseline_start
    """

    UPDATE_BASELINE_OFFER = """UPDATE "${table_prefix}contract_baseline" 
    SET "power_span" =  :power_span ,  "update_ts" =  extract(epoch from now()) * 1000  
    WHERE contract_id = :contract_id and "baseline_start" = :baseline_start
    """


class BaselineAPIImpl(BaselineAPI):

    def __init__(self, table_prefix: str):
        super(BaselineAPI, self).__init__(table_prefix=table_prefix)
        self.queries: BaselineQueries = self.build_queries(BaselineQueries)

    def get_baseline(self, contract_id: int) -> List[BaselineDAO]:
        with ConnectionWrapper() as conn:
            args = {"contract_id": contract_id}
            contracts = conn.get(q=self.queries.LIST_CONTRACT_BASELINE, args=args, obj_type=BaselineDAO)
            return contracts

    def set_baseline(self, baselines: List[BaselineDAO]):
        with ConnectionWrapper() as conn:
            inserted = conn.insert_batch(q=self.queries.INSERT_CONTRACT_BASELINE,
                                         arg_list=[vars(b) for b in baselines],
                                         return_id_col=["contract_id", "baseline_start"],
                                         fail_safe=False)
            return inserted

    def set_capacity(self, baselines: List[BaselineDAO]) :
        with ConnectionWrapper() as conn:
            for b in baselines:
                updated = conn.update(q=self.queries.INSERT_CONTRACT_BASELINE,
                                             args= vars(b)    )
                if not updated:
                    raise ValueError(f"baseline update failed for : {b.__dict__}")


