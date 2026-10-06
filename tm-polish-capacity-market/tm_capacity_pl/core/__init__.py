from typing import Optional

from ke_client import KEClient

from tm_capacity_pl.core.config import APPSettings, ServiceSettings

app_settings: APPSettings = APPSettings.load()
service_settings: ServiceSettings = ServiceSettings.load()
smart_client: KEClient


def init_sc(env_path: str = ".env"):
    global smart_client
    if smart_client:
        return smart_client
    import ke_client

    ke_client.VERIFY_SERVER_CERT = False
    ke_client.ENV_FILE = env_path
    from tm_capacity_pl.core.smart_client import setup_ke
    setup_ke()
    from ke_client import KEClient
    import logging
    ki_client: KEClient = KEClient.build(logger=logging.getLogger())
    smart_client = ki_client
    return smart_client


def start_sc():
    global smart_client
    from tm_capacity_pl.core.smart_client import start_client

    start_client()
