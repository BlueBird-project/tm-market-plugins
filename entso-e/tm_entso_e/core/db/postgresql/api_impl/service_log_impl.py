from abc import abstractmethod
from typing import Optional, Dict, Any, List

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm_entso_e.core.db.api.service_log import ServiceLogAPI
from tm_entso_e.modules.entso_e_web_api.scheduled_jobs import JobMeta
from tm_entso_e.schemas.service_log import ServiceLogDAO


class ServiceLogQueries:
    # TODO: list columns instead of *
    LIST_LOG = """SELECT "log_id","log_tag", "log_message", "log_ts", 
    "log_obj_type", "log_obj_json",  "log_context" 
    FROM "${table_prefix}service_log"  
      WHERE     COALESCE(log_ts >= :ts_from, TRUE) and COALESCE(log_ts <= :ts_to, TRUE) 
      AND COALESCE(log_tag = :log_tag , TRUE) """

    INSERT_LOG = """INSERT INTO "${table_prefix}service_log" 
    ( "log_tag", "log_message", "log_ts", "log_obj_type", "log_obj_json",  "log_context" ) 
    VALUES ( :log_tag,:log_message, :log_ts, :log_obj_type, :log_obj_json ,:log_context ) 
        """

    LIST_JOB_ERR = """ select "log_id","log_tag", "log_message", "log_ts",  "log_obj_type", "log_obj_json",  s_log."log_context" 
    FROM "${table_prefix}service_log" s_log JOIN (
         SELECT log_context,  max(log_ts) as max_ts  FROM "${table_prefix}service_log"
         WHERE  COALESCE(log_ts >= :ts_from, TRUE) and COALESCE(log_ts <= :ts_to, TRUE) 
                AND COALESCE(log_tag = :log_tag , TRUE)          and log_obj_type= :log_obj_type
         GROUP BY "log_context"  	
        ) s_log_ts on s_log.log_context = s_log_ts.log_context and s_log.log_ts = s_log_ts.max_ts 
        """
    COUNT_TAG = """ select count(*)    FROM "${table_prefix}service_log"  
         WHERE  COALESCE(log_ts >= :ts_from, TRUE) and COALESCE(log_ts <= :ts_to, TRUE) 
                AND  log_tag = :log_tag        """


class ServiceLogAPIImpl(ServiceLogAPI):
    def __init__(self, table_prefix: str):
        super(ServiceLogAPI, self).__init__(table_prefix=table_prefix)
        self.queries: ServiceLogQueries = self.build_queries(ServiceLogQueries)

    def list(self, ts: TimeSpan, tag: Optional[str] = None) -> List[ServiceLogDAO]:
        with ConnectionWrapper() as conn:
            args = {"ts_from": ts.ts_from, "ts_to": ts.ts_to, "log_tag": tag}
            return conn.select(q=self.queries.LIST_LOG, args=args, obj_type=ServiceLogDAO)

    def has_tag(self, ts: TimeSpan, tag: str) -> int:
        with ConnectionWrapper() as conn:
            args = {"ts_from": ts.ts_from, "ts_to": ts.ts_to, "log_tag": tag}
            return conn.get(q=self.queries.COUNT_TAG, args=args, raw=True)[0]

    def log(self, log_item: ServiceLogDAO):
        with ConnectionWrapper() as conn:
            inserted_id = conn.insert(q=self.queries.INSERT_LOG, args=vars(log_item),
                                      return_id_col="log_id")
            if inserted_id is None:
                raise ValueError(f"Market not saved: {log_item.__dict__}")
            log_item.log_id = inserted_id
            return log_item

    def list_job_state(self, ts: TimeSpan, tag: Optional[str] = None) -> List[ServiceLogDAO]:
        with ConnectionWrapper() as conn:
            args = {"ts_from": ts.ts_from, "ts_to": ts.ts_to, "log_tag": tag,
                    "log_obj_type": f"{JobMeta.__module__}.{JobMeta.__name__}"}
            return conn.select(q=self.queries.LIST_JOB_ERR, args=args, obj_type=ServiceLogDAO)
