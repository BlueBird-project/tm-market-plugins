import logging

import tm_entso_e

if __name__ == "__main__":
    ###
    # setup configurations
    ###
    tm_entso_e.init_args()
    from tm_entso_e.core import service_settings, app_settings

    # utils.ENV_FILE = main.app_args.env_path
    tm_entso_e.set_logging()
    logging.info(f"START {service_settings.name}")
    ############
    # setup DB #
    ############
    from tm_entso_e.core.db import setup_db

    setup_db()

if app_settings.use_ke_api:
    from tm_entso_e.modules.ke_interaction import set_bg_ke_client, set_sync_ke_client

    ############
    # setup KE #
    ############

    if app_settings.use_scheduler or app_settings.use_rest_api:
        logging.info("Running BG KE client")
        market_prefix = set_bg_ke_client().kb_id
    else:
        set_sync_ke_client()
        exit()
else:
    market_prefix = "https://entsoe.bluebird.com"

from tm_entso_e.modules.ke_interaction.interactions.dam_model import MarketURI
MarketURI.__MARKET_PREFIX__=market_prefix
if __name__ == "__main__" and app_settings:
    # configure entsoe
    from tm_entso_e.modules.entso_e_web_api.config import configure_api

    api_settings = configure_api()
    from tm_entso_e.modules.entso_e_web_api.service import init_service

    # TODO set initial data
    init_service(market_prefix=market_prefix, load_data=True, days_to_load=5)

##########################################################33
if __name__ == "__main__" and app_settings:
    if app_settings.use_scheduler:
        from tm_entso_e.core import task_manager

        task_manager.setup_scheduler()
    if app_settings.use_rest_api:
        import uvicorn
        from fastapi import FastAPI
        from tm_entso_e.core.healthcheck.router import router as healthcheck_router
        from tm_entso_e.modules.entsoe_api.router import router as entsoe_router
        from tm_entso_e.modules.entsoe_api.admin_router import router as admin_router

        app = FastAPI(docs_url="/api",
                      openapi_url="/openapi.json", redoc_url="/redoc")

        healthcheck_app = FastAPI(docs_url="/docs",
                                  openapi_url="/openapi.json", redoc_url="/redoc")

        healthcheck_app.include_router(router=healthcheck_router, prefix="")
        app.mount("/healthcheck", healthcheck_app)
        app.include_router(entsoe_router, prefix="/api")
        admin_app = FastAPI(docs_url="/docs",
                            openapi_url="/openapi.json", redoc_url="/redoc")
        admin_app.include_router(router=admin_router, prefix="")
        app.mount("/admin", admin_app)
        uvicorn.run(app, port=service_settings.port, host=service_settings.host, root_path=service_settings.root_path)
