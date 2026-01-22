from typing import Optional, Any

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from tm_entso_e import app_variables
from tm_entso_e.utils import DictBaseSettings, load_yml_obj

__CONFIG_SECTION__ = "ENTSOE"


class ENTSOEAPISettings(DictBaseSettings):
    # knowledge_base_id: str = Field(...)
    endpoint: str = Field(default="https://web-api.tp.entsoe.eu/api")
    token: str = Field()
    api_timeout: int = Field(default=30, description="Timeout in seconds")

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


api_settings = ENTSOEAPISettings()
