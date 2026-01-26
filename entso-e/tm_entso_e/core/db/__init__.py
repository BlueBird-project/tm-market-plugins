def setup_db():
    from tm_entso_e import app_args
    from effi_onto_tools.db.postgresql import configure_pg
    configure_pg(app_args.config_path)

    from tm_entso_e.core.db.postgresql import dao_manager

    def pg_check_db():
        from effi_onto_tools.db.postgresql.dbconnection import connection_manager
        # try:
        connection_manager.check_db(db_meta=db_meta, assert_version=False)
        # except DeprecatedSchemaException as ex:
        #     connection_manager.update_db_schema(ex.db_version, db_meta=db_meta)
        #     connection_manager.check_db(db_meta=db_meta, assert_version=True)

    db_meta = dao_manager.init()
    pg_check_db()
