from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm_capacity_pl.contract.core.db.api.baseline_api import BaselineAPI
from tm_capacity_pl.contract.core.db.api.contract_api import ContractAPI
from tm_capacity_pl.contract.core.db.postgresql.api_impl import QueryObject
from tm_capacity_pl.contract.core.db.postgresql.api_impl.contract_api_impl import ContractQueries
from tm_capacity_pl.models.contract import ContractDAO, BaselineDAO, Baseline, BaselineValueDAO, CertifiedBaseline


class BaselineQueries(QueryObject):
    __TABLE_NAME__ = "capacity_market_baseline"
    __PROJECTION__ = """ ${table_alias}."baseline_id",${table_alias}."update_time"   """

    LIST_BASELINE = """SELECT ${projection}, contract_table.create_ts  FROM "${table_prefix}${table_name}" as ${table_alias} 
    LEFT JOIN  "${table_prefix}""" + ContractQueries.__TABLE_NAME__ + """ as contract_table 
     on contract_table.current_baseline_id =  ${table_alias}."baseline_id"
     WHERE contract_table.create_ts = :contract_id 
    """
    # LIST_BASELINE = """SELECT ${projection}, contract_table.create_ts  FROM "${table_prefix}${table_name}" as ${table_alias}
    # LEFT JOIN  "${table_prefix}""" + ContractQueries.__TABLE_NAME__ + """ as contract_table
    #  on contract_table.current_baseline_id =  ${table_alias}."baseline_id"
    #  WHERE COALESCE(contract_table.create_ts = :contract_id,TRUE)
    # """

    GET_BASELINE = """SELECT ${projection}, contract_table.create_ts  FROM "${table_prefix}${table_name}" as ${table_alias} 
    LEFT JOIN  "${table_prefix}""" + ContractQueries.__TABLE_NAME__ + """ as contract_table 
     on contract_table.current_baseline_id =  ${table_alias}."baseline_id"
     WHERE  ${table_alias}."baseline_id" = :baseline_id
    """

    INSERT_BASELINE = """INSERT INTO "${table_prefix}${table_name}" 
    (   "update_time","ext" )  VALUES (  extract(epoch from now()) * 1000,:ext) 
    """

    UPDATE_BASELINE = """UPDATE "${table_prefix}${table_name}"   
     SET   "update_ts" =  extract(epoch from now()) * 1000     WHERE baseline_id = :baseline_id  
    """


class BaselineValueQueries(QueryObject):
    __TABLE_NAME__ = "capacity_market_baseline_value"

    # __PROJECTION__ = """ ${table_alias}."contract_id",${table_alias}."baseline_isp",${table_alias}."isp_len",
    #  ${table_alias}."power_span",  ${table_alias}."baseline_value", ${table_alias}."offer_mwh",
    #   ${table_alias}."update_time" """
    __PROJECTION__ = """ ${table_alias}."baseline_id",${table_alias}."baseline_isp",${table_alias}."isp_len", 
     ${table_alias}."baseline_value"  """

    LIST_BASELINE_VALUES = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} 
    WHERE  ${table_alias}."baseline_id" = :baseline_id 
    """

    INSERT_BASELINE_VALUES = """INSERT INTO "${table_prefix}${table_name}" 
    ("baseline_id", "baseline_isp", "isp_len",  "baseline_value" ) 
    VALUES (:baseline_id,:baseline_isp,:isp_len,  :baseline_value ) 
    """


class BaselineAPIImpl(BaselineAPI):

    def __init__(self, table_prefix: str):
        super(BaselineAPI, self).__init__(table_prefix=table_prefix)
        self.queries: BaselineQueries = self.build_queries(BaselineQueries)
        self.value_query: BaselineValueQueries = self.build_queries(BaselineValueQueries)

    def list(self, contract_id: int) -> List[CertifiedBaseline]:
        with ConnectionWrapper() as conn:
            args = {"contract_id": contract_id}
            baselines = conn.select(q=self.queries.LIST_BASELINE, args=args, obj_type=CertifiedBaseline)
            return baselines

    def get_baseline(self, baseline_id: int) -> Baseline:
        with ConnectionWrapper() as conn:
            args = {"baseline_id": baseline_id}
            baseline_dao = conn.get(q=self.queries.GET_BASELINE, args=args, obj_type=BaselineDAO)
            values = conn.get(q=self.value_query.LIST_BASELINE_VALUES, args=args, obj_type=BaselineValueDAO)
            baseline = Baseline(**vars(baseline_dao), values=values)
            return baseline

    def init_baseline(self) -> BaselineDAO:
        with ConnectionWrapper() as conn:
            inserted = conn.insert(q=self.queries.INSERT_BASELINE, args={},
                                   return_id_col=["baseline_id", "update_time"])
            if len(inserted) == 1:
                return BaselineDAO(baseline_id=int(inserted[0][0]), update_time=int(inserted[0][1]))
            raise Exception("Baseline not added")

    def set_baseline(self, baseline_values: List[BaselineValueDAO]):
        with ConnectionWrapper() as conn:
            inserted = conn.insert_batch(q=self.value_query.INSERT_BASELINE_VALUES,
                                         arg_list=[vars(b) for b in baseline_values],
                                         return_id_col=["contract_id", "baseline_isp", ],
                                         fail_safe=False)
            return inserted
