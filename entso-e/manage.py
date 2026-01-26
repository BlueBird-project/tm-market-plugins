import logging
import tm_entso_e
from tm_entso_e.utils import TimeSpan

if __name__ == "__main__":
    ###
    # setup configurations
    ###
    tm_entso_e.init_args()
    from tm_entso_e.core import service_settings, app_settings

    # utils.ENV_FILE = main.app_args.env_path
    tm_entso_e.set_logging()
    logging.info(f"START {service_settings.name}")
    ###
    # setup DB
    ###
    from tm_entso_e.core.db import setup_db

    setup_db()

if __name__ == "__main__" and app_settings:
    # configure entsoe
    from tm_entso_e.modules.entso_e_api.config import configure_api

    api_settings = configure_api()
    from tm_entso_e.modules.entso_e_api.energy_api import MarketAPI

    # init api client
    market_api = MarketAPI()
    eic_area = api_settings.subscribed_eic[0]
    result = market_api.get_energy_prices(eic=eic_area, ti=TimeSpan.last_48h())
    print(result)
if app_settings.use_ke_api:
#     # setup ke
     import ke_client
#
     ke_client.VERIFY_SERVER_CERT = False
     ke_client.ENV_FILE = tm_entso_e.app_args.env_path
#
     if app_settings.use_scheduler or app_settings.use_rest_api:
         from tm_entso_e.modules.ke_interaction import set_bg_ke_client
#
         logging.info("Running BG KE client")
         set_bg_ke_client()
     else:
         from tm_entso_e.modules.ke_interaction import set_ke_client

         set_ke_client()


# if __name__ == "__main__" and app_settings:
#     if app_settings.use_scheduler:
#         from tm_entso_e.core import task_manager
#
#         task_manager.setup_scheduler()

# if __name__ == "__main__":
#     if app_settings.use_rest_api:
#         import uvicorn
#         from tm_entso_e.modules.day_ahead_api.router import router as dayahead_router
#         from tm_entso_e.core.healthcheck.router import router as healthcheck_router
#         from tm_entso_e.modules.admin.admin_router import router as admin_router
#         from fastapi import FastAPI
#
#         app = FastAPI(docs_url="/docs",
#                       openapi_url="/docs/openapi.json", redoc_url="/redoc")
#         app.include_router(router=dayahead_router, prefix="/api")
#
#         healthcheck_app = FastAPI(docs_url="/docs",
#                                   openapi_url="/openapi.json", redoc_url="/redoc")
#
#         healthcheck_app.include_router(router=healthcheck_router, prefix="")
#         app.mount("/healthcheck", healthcheck_app)
#         admin_app = FastAPI(docs_url="/docs",
#                             openapi_url="/openapi.json", redoc_url="/redoc")
#         admin_app.include_router(router=admin_router, prefix="")
#         app.mount("/admin", admin_app)
#         uvicorn.run(app, port=service_settings.port, host=service_settings.host, root_path=service_settings.root_path)
