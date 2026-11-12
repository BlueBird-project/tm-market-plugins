
from effi_onto_tools.utils import DictBaseSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class MarketSettings(DictBaseSettings):
    uri: str = Field(default="")
    model_config = SettingsConfigDict(env_prefix='MARKET_', env_file=DictBaseSettings.env_path(),
                                      env_file_encoding="utf-8")

    @classmethod
    def load(cls, **kwargs):
        from tm_capacity_pl.core import app_args
        return super().load(app_args.config_path, "MARKET".lower())

market_settings:MarketSettings

def configure() :
    global market_settings
    market_settings  = MarketSettings.load()


