from typing import Optional, Union, Any

from ke_client import ki_split_uri, SplitURIBase, BindingsBase, ki_object, OptionalLiteral
from ke_client.utils import time_utils
from rdflib import URIRef, Literal


@ki_object("fm-ts-info-request", allow_partial=True)
class FMTSRequest(BindingsBase):
    ts_interval_uri: URIRef
    ts_date_from: Literal
    ts_date_to: Literal

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


@ki_object("fm-ts-info-request")
class FMTSResponse(FMTSRequest):
    ts_uri: URIRef
    ts_usage: URIRef
    time_create: Literal

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@ki_object("fm-ts", allow_partial=True)
class FMPntQuery(BindingsBase):
    ts_uri: URIRef

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


@ki_object("fm-ts")
class FMPnt(BindingsBase):
    ts_uri: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    value: Optional[Literal]

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)

    @property
    def ts_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts)

    def get_value(self) -> Optional[float]:
        return self.convert_value(self.value, float)


@ki_split_uri(uri_template="http://ke.bluebird.com/interval/${ts_from}/${ts_to}")
class KETimeIntervalUri(SplitURIBase):
    ts_from: int
    ts_to: int
