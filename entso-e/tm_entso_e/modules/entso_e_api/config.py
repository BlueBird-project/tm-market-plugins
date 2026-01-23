from typing import Optional, Any, Dict, List

from pydantic import Field, Extra
from pydantic_settings import SettingsConfigDict, BaseSettings

from tm_entso_e import app_variables
from tm_entso_e.modules.entso_e_api.model import SubscribedEIC, EICArea
from tm_entso_e.utils import DictBaseSettings, load_yml_obj

__CONFIG_SECTION__ = "ENTSOE"


class ENTSOEServiceSettings(DictBaseSettings):
    # knowledge_base_id: str = Field(...)
    endpoint: str = Field(default="https://web-api.tp.entsoe.eu/api")
    token: str = Field()
    api_timeout: int = Field(default=30, description="Timeout in seconds")
    api_config_path: Optional[str] = Field(default=None)

    model_config = SettingsConfigDict(env_prefix=__CONFIG_SECTION__ + "_", env_file=app_variables.ENV_FILE,
                                      env_file_encoding="utf-8",
                                      extra="ignore")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, _env_file=app_variables.ENV_FILE, **kwargs)

    @classmethod
    def load(cls, yml_path: Optional[str] = None, **kwargs):
        # regex = re.compile(r'^__?.+_?_?$')
        if yml_path:
            app_config = load_yml_obj(yml_path, section=__CONFIG_SECTION__.lower(), settings_constructor=dict)
            keys = [k for k in vars(cls)["__pydantic_fields__"].keys()]

            fields = {k: f for k, f in app_config.items() if k in keys}
            return cls(dict_settings=fields)

        return cls(dict_settings={})
        # return super().load(yml_path=yml_path, section_name="KE".lower


class ENTSOEAPISettings(BaseSettings, extra=Extra.allow):
    __SECTION__ = "entsoe_api"
    subscribed_regions: Optional[List[SubscribedEIC]] = None
    eic_codes: Dict[str, EICArea]
    _country_eic_code_map_: Dict[str, str]
    _area_eic_code_map_: Dict[str, str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, _country_code_map_={}, _area_eic_code_map_={}, **kwargs)
        for eic_area in self.eic_codes.values():
            if eic_area.country_codes is not None:
                for country_code in eic_area.country_codes:
                    self._country_code_map_[country_code] = eic_area.code
            for area_name in eic_area.area_names:
                self._area_eic_code_map_[area_name] = eic_area.code

    def get_eic_by_country(self, country: str) -> str:
        # TODO: handle key error
        return self._country_eic_code_map_[country]

    def get_eic_by_area(self, area: str) -> str:
        # TODO: handle key error
        return self._area_eic_code_map_[area]


service_settings = ENTSOEServiceSettings()
api_settings: ENTSOEAPISettings = ENTSOEAPISettings(eic_codes={})


def configure_api():
    global service_settings
    global api_settings
    api_config_path = service_settings.api_config_path
    import os
    if api_config_path is None:
        return
        # todo: log warning ?
    if not os.path.exists(api_config_path):
        raise FileNotFoundError(
            f"ENTSOE API config file: '{api_config_path}' does not exist." +
            " set ENTSOE_API_CONFIG_PATH env variable ")

    _api_settings = load_yml_obj(api_config_path, section=ENTSOEAPISettings.__SECTION__, settings_constructor=dict)
    api_settings = ENTSOEAPISettings.model_validate(_api_settings)
