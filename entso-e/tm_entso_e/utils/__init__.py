from typing import Callable, Optional, Union

import yaml
from pydantic import PrivateAttr, BaseModel
from pydantic_settings import BaseSettings, InitSettingsSource, PydanticBaseSettingsSource, SettingsConfigDict

ENV_FILE = ".env"


class MergeConfigMixin:

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        merged = {}
        for base in reversed(cls.__mro__[1:]):  # walk bases
            if hasattr(base, "model_config"):
                merged.update(base.model_config)

        if hasattr(cls, "model_config"):
            merged.update(cls.model_config)

        cls.model_config = SettingsConfigDict(**merged)


class DictBaseSettings(MergeConfigMixin, BaseSettings):
    @staticmethod
    def env_path():
        # os.environ.get("ENV_FILE")
        # TODO check if file exists
        # try
        if ENV_FILE is None or ENV_FILE == ".env":
            return ".env"  # -> log warning if not exists
        return ENV_FILE
        # except:
        #    raise exception env not exists

    # dict_settings_: Optional[dict] = Field(..., alias="dict_settings")
    _dict_settings_: Optional[dict] = PrivateAttr(default=None)
    model_config = SettingsConfigDict(populate_by_name=True)

    @classmethod
    def settings_customise_sources(cls,
                                   settings_cls: type[BaseSettings],
                                   init_settings: InitSettingsSource,  # type: ignore[override]
                                   env_settings: PydanticBaseSettingsSource,
                                   dotenv_settings: PydanticBaseSettingsSource,
                                   file_secret_settings: PydanticBaseSettingsSource, ):
        # init_settings.init_kwargs["_dict_settings"] = init_settings.init_kwargs["dict_settings"]
        # init_settings.init_kwargs["_dict_settings_"] = init_settings.init_kwargs["dict_settings"]
        if "dict_settings" in init_settings.init_kwargs:
            cls._dict_settings_ = init_settings.init_kwargs["dict_settings"]

            del init_settings.init_kwargs["dict_settings"]
        else:
            cls._dict_settings_ = {}

        def dict_source(**kwargs):
            return cls._dict_settings_
            # return init_settings.init_kwargs["dict_settings"]

        # https://docs.pydantic.dev/latest/concepts/pydantic_settings/#customise-settings-sources
        # The order of the returned callables decides the priority of inputs; first item is the highest priority
        return (
            env_settings,  # highest priority , default .env and loaded environemnt var
            dict_source,  # custome settings
            dotenv_settings,  # custom .env file
            init_settings,  # __init__ args
        )

    @classmethod
    def load(cls, yaml_path: Optional[str] = None, section_name: Optional[str] = None):
        # regex = re.compile(r'^__?.+_?_?$')
        if yaml_path:
            app_config = load_yaml_obj(yaml_path, section=section_name, settings_constructor=dict)
            keys = [k for k in vars(cls)["__pydantic_fields__"].keys()]
            fields = {k: f for k, f in app_config.items() if k in keys}
            return cls(dict_settings=fields)
        return cls(dict_settings={})


def load_yaml_obj(config_path: str, section: Optional[str] = None,
                  settings_constructor: Optional[Union[Callable, dict]] = None) -> Union[dict, object]:
    class YAML:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    try:
        _config = _load_yaml(config_path, section)
        if settings_constructor is not None:
            if settings_constructor is dict:
                if type(_config) is not dict:
                    raise TypeError(f"Expected configuration type: 'dict', actual type: {type(_config)}  ")
                return _config
            return settings_constructor(**_config)
        else:
            return YAML(**_config)
    except FileNotFoundError as error:
        message = "Error: yaml config file not found."
        raise FileNotFoundError(error, message) from error


def _load_yaml(config_path, section):
    with open(config_path) as stream:
        try:
            _config = yaml.safe_load(stream, )
            if section is not None:
                try:
                    _config = _config[section]
                except KeyError:
                    #   Todo: handle  error
                    raise KeyError(f"invalid setting section {section}")
        except yaml.YAMLError as exc:
            # TODO: log/handle error
            print(exc)
    return _config


DAY_MS = 24 * 3600 * 1000
WEEK_MS = 7 * DAY_MS


class TimeSpan(BaseModel):
    ts_from: Optional[int] = None
    ts_to: Optional[int] = None

    def __init__(self, ts_from: Optional[int] = None, ts_to: Optional[int] = None):
        if ts_from is None and ts_to is None:
            from ke_client.utils import time_utils
            ts_to = time_utils.current_timestamp() + DAY_MS
            ts_from = ts_to - 2 * DAY_MS
        ts_from = ts_from if ts_from is not None else ts_to - DAY_MS
        ts_to = ts_to if ts_to is not None else ts_from + DAY_MS
        if ts_to < ts_from:
            raise ValueError("Time from cannot be after time to")
        super().__init__(ts_from=ts_from, ts_to=ts_to)

    @staticmethod
    def last_week():
        from ke_client.utils import time_utils
        ts_to = time_utils.current_timestamp()
        ts_from = ts_to - WEEK_MS
        return TimeSpan(ts_from=ts_from, ts_to=ts_to)

    @staticmethod
    def last_day():
        from ke_client.utils import time_utils
        ts_to = time_utils.current_timestamp()
        ts_from = ts_to - DAY_MS
        return TimeSpan(ts_from=ts_from, ts_to=ts_to)

    @staticmethod
    def two_day():
        from ke_client.utils import time_utils
        cur = time_utils.current_timestamp()
        ts_to = cur + DAY_MS
        ts_from = cur - DAY_MS
        return TimeSpan(ts_from=ts_from, ts_to=ts_to)

    @staticmethod
    def next_day():
        from ke_client.utils import time_utils
        ts_from = time_utils.current_timestamp()
        ts_to = ts_from + DAY_MS
        return TimeSpan(ts_from=ts_from, ts_to=ts_to)

    def __len__(self):
        try:
            span = self.ts_to - self.ts_from
            if span < 0:
                raise ValueError("Negative time interval")
            return span
        except AttributeError | TypeError:
            return None

    @staticmethod
    def non_empty(ts: Optional['TimeSpan'] = None) -> 'TimeSpan':
        if ts is None or len(ts) == 0:
            from ke_client.utils import time_utils
            cur_ts = time_utils.current_timestamp()
            return TimeSpan(ts_from=cur_ts - DAY_MS, ts_to=cur_ts + DAY_MS)
        return ts

    @property
    def time_span_ms(self):
        return self.ts_to - self.ts_from

    @property
    def time_span_day(self):
        m = (self.ts_to - self.ts_from) % DAY_MS
        if m == 0:
            return (self.ts_to - self.ts_from) / DAY_MS
        return (self.ts_to - self.ts_from) / DAY_MS + 1

    @property
    def time_span_min(self):
        return self.time_span_ms / 60000
