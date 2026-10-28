def init_service():
    # if ke is enabled
    import logging
    from tm_capacity_pl.core import app_settings
    from tm_capacity_pl.notification.core.db import setup_db
    setup_db()
    if app_settings.use_ke_api:
        logging.info("INIT KI")

        from tm_capacity_pl.notification.modules.ke_interaction.interactions.capacity_market_interactions import \
            ki as cm_ki
        from tm_capacity_pl.core import init_sc, app_args
        smart_client = init_sc(env_path=app_args.env_path)
        smart_client.include(cm_ki)
    if app_settings.use_scheduler:
        # from tm.core import task_manager

        from tm_capacity_pl.core import task_manager
        task_manager.setup_scheduler()


def start_service():
    from tm_capacity_pl.core.task_manager import start_scheduler
    from tm_capacity_pl.core import start_sc
    from tm_capacity_pl.core import app_settings
    if app_settings.use_ke_api:
        start_sc()
    if app_settings.use_scheduler:
        start_scheduler()

    if app_settings.use_rest_api:
        import uvicorn
        from tm_capacity_pl.notification.modules.rest.app import app
        from tm_capacity_pl.core import service_settings
        uvicorn.run(app, port=service_settings.port, host=service_settings.host, root_path=service_settings.root_path,
                    log_config=None)
