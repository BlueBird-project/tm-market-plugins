from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm_capacity_pl.contract.core.db.api.contract_api import ContractAPI
from tm_capacity_pl.contract.core.db.api.power_usage_api import PowerUsageAPI
from tm_capacity_pl.contract.core.db.postgresql.api_impl import QueryObject
from tm_capacity_pl.models.contract import ContractDAO, CapacityPowerDAO


class PowerQueries(QueryObject):
    __TABLE_NAME__ = "power_usage"
    __PROJECTION__ = """ ${table_alias}."ts", ${table_alias}."value", ${table_alias}."granularity_ms"   """

    LIST_POWER_USAGE = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE 
    ( coalesce(:ts_from<=${table_alias}."ts",TRUE) and  coalesce(:ts_to>=${table_alias}."ts",TRUE))
    """

    INSERT_USAGE = """INSERT INTO "${table_prefix}contract_details" 
    ("ts",  "value", "granularity_ms"  )   VALUES (:ts,:value,:granularity_ms )      """




class PowerUsageAPIImpl(PowerUsageAPI):

    def __init__(self, table_prefix: str):
        super(PowerUsageAPI, self).__init__(table_prefix=table_prefix)
        self.queries: PowerQueries = self.build_queries(PowerQueries)

    def list_power(self, ts: TimeSpan) -> List[CapacityPowerDAO]:
        with ConnectionWrapper() as conn:
            args = {"ts_from": ts.ts_from, "ts_to": ts.ts_to}
            power_usage = conn.get(q=self.queries.LIST_POWER_USAGE, args=args, obj_type=CapacityPowerDAO)
            return power_usage

    def log_power(self, power_history: List[CapacityPowerDAO]) -> int:
        with ConnectionWrapper() as conn:
            inserted = conn.insert_batch(q=self.queries.INSERT_USAGE,
                                         arg_list=[vars(p) for p in power_history],
                                         return_id_col=["ts" ],
                                         fail_safe=False)
            return len(inserted)
