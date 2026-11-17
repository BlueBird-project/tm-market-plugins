from fastapi import FastAPI


def create_app():
    from tm_capacity_pl.contract.modules.rest.router import router as contract_router

    new_app = FastAPI(docs_url="/api",
                      openapi_url="/openapi.json", redoc_url="/redoc")
    new_app.include_router(router=contract_router, prefix="/api")
    # app.include_router(router=ki_router, prefix="/ki")

    # healthcheck_app = FastAPI(docs_url="/docs",
    #                           openapi_url="/openapi.json", redoc_url="/redoc")

    # healthcheck_app.include_router(router=healthcheck_router, prefix="")
    # app.mount("/healthcheck", healthcheck_app)
    # admin_app = FastAPI(docs_url="/docs",
    #                     openapi_url="/openapi.json", redoc_url="/redoc")
    # admin_app.include_router(router=admin_router, prefix="")
    # app.mount("/admin", admin_app)
    return new_app


app: FastAPI = create_app()
