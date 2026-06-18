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