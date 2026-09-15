from ke_client import KEClient

from tm_capacity_pl.contract.core import APPSettings, ServiceSettings
from tm_capacity_pl.core.smart_client import init_client

app_settings: APPSettings = APPSettings.load()
service_settings: ServiceSettings = ServiceSettings.load()
smart_client: KEClient


def init_sc():
    global smart_client
    smart_client = init_client()
