import logging


from tm_capacity_pl.core import service_settings

if __name__ == "__main__":
    ###
    # setup configurations
    ###
    tm.init_args()
    from effi_onto_tools import utils
    utils.ENV_FILE = tm.app_args.env_path
    tm.set_logging()
    logging.info(f"START {service_settings.name}")
    ###
    # setup DB TODO:!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ###
    # from tm.core.db import setup_db
    #
    # setup_db()


if __name__ == "__main__" :
    from tm_capacity_pl.core import  app_settings
    if app_settings.use_ke_api:
        logging.info("INIT KI")
        # setup ke
        import ke_client

        ke_client.VERIFY_SERVER_CERT = False
        ke_client.ENV_FILE = tm.app_args.env_path

        # setup_ke()

        if app_settings.use_scheduler or app_settings.use_rest_api:
            from tm.modules.ke_interaction import set_bg_ke_client

            logging.info("Running BG KE client")
            set_bg_ke_client()
        else:
            from tm.modules.ke_interaction import set_sync_ke_client

            set_sync_ke_client()

if __name__ == "__main__":
    if app_settings.use_scheduler:
        from tm.core import task_manager

        task_manager.setup_scheduler(on_start=True)

    if app_settings.use_rest_api:
        import uvicorn

        # from main.modules.tge_api.admin_router import router as admin_router
        from fastapi import FastAPI
        from tm_capacity_pl.demand.modules.rest.router import router as demand_router

        app = FastAPI(docs_url="/api",
                      openapi_url="/openapi.json", redoc_url="/redoc")
        app.include_router(router=demand_router, prefix="/api")
        # app.include_router(router=ki_router, prefix="/ki")

        healthcheck_app = FastAPI(docs_url="/docs",
                                  openapi_url="/openapi.json", redoc_url="/redoc")

        healthcheck_app.include_router(router=healthcheck_router, prefix="")
        app.mount("/healthcheck", healthcheck_app)
        # admin_app = FastAPI(docs_url="/docs",
        #                     openapi_url="/openapi.json", redoc_url="/redoc")
        # admin_app.include_router(router=admin_router, prefix="")
        # app.mount("/admin", admin_app)
        uvicorn.run(app, port=service_settings.port, host=service_settings.host, root_path=service_settings.root_path,
                    log_config=None)
