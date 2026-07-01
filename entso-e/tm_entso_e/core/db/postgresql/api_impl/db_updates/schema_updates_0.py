from effi_onto_tools.db.postgresql.init_db import DBMeta

from tm_entso_e.core.db.postgresql.api_impl.db_updates import _run_ddl

_0_2_ddl = """
ALTER TABLE "${table_prefix}market_offer_details"
ADD "created_ts" bigint   NULL;

UPDATE   "${table_prefix}market_offer_details"
set "created_ts" = update_ts    ;

 

ALTER TABLE "${table_prefix}market_offer_details"
ALTER "created_ts" TYPE bigint,
ALTER "created_ts" DROP DEFAULT,
ALTER "created_ts" SET NOT NULL; 


"""


def db_0_2_update(db_meta: DBMeta):
    from tm_entso_e.core.db.postgresql import dao_manager
    _run_ddl(ddl_str=_0_2_ddl, db_version=db_meta.db_version, table_prefix=db_meta.db_table_prefix)

_0_3_ddl="""
DROP TABLE IF EXISTS "${table_prefix}service_log";
DROP SEQUENCE IF EXISTS ${table_prefix}service_log_log_id_seq;
CREATE SEQUENCE ${table_prefix}service_log_log_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

 
CREATE TABLE "${table_prefix}service_log" ( 
   "log_id" bigint DEFAULT nextval('${table_prefix}service_log_log_id_seq') NOT NULL,  
  "log_tag" character varying(10) NOT NULL,
  "log_context" character varying(100) NULL,
  "log_message" character varying(250) NOT NULL,
  "log_obj_type" character varying(150) NULL,
  "log_obj_json" text NULL,
  "log_ts" bigint NOT NULL,
    CONSTRAINT "${table_prefix}service_log_pk" PRIMARY KEY ("log_id")
);

CREATE INDEX "${table_prefix}service_log_log_ts" ON public.${table_prefix}service_log USING btree ("log_ts");
"""
def db_0_3_update(db_meta: DBMeta):
    from tm_entso_e.core.db.postgresql import dao_manager
    _run_ddl(ddl_str=_0_3_ddl, db_version=db_meta.db_version, table_prefix=db_meta.db_table_prefix)