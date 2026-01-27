from typing import Optional, Union

from effi_onto_tools.utils import time_utils
from isodate import parse_duration
from ke_client import ki_object, is_nil, ki_split_uri, SplitURIBase
from ke_client import BindingsBase
from rdflib import URIRef, Literal
from rdflib.util import from_n3


# DAM_market_type: Literal = Literal("ubmarket:DayAheadMarket")


@ki_object("market")
class EnergyMarketBindings(BindingsBase):
    market_uri: URIRef
    country_uri: URIRef
    country_name: Literal
    market_type: URIRef

    # market_type: Literal = DAM_market_type

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


@ki_object("market", allow_partial=True)
class EnergyMarketBindingsQuery(BindingsBase):
    market_uri: Optional[URIRef] = None
    country_name: Optional[Literal] = None
    market_type: Optional[URIRef] = None

    # market_type: Literal = DAM_market_type

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


#
# @ki_object("market", allow_partial=True)
# class EnergyMarketRequest(BindingsBase):
#     market_location: Literal
#
#
# @ki_object("market-offer-info-query", allow_partial=True)
# class MarketOfferInfoQuery(BindingsBase):
#     ts_interval_uri: URIRef
#     market_uri: URIRef
#     ts_date_from: Literal
#     ts_date_to: Literal
#
#     def __init__(self, **kwargs):
#         super().__init__(bindings=kwargs)
#
#     @property
#     def ts_from(self) -> int:
#         return time_utils.xsd_to_ts(self.ts_date_from)
#
#     @property
#     def ts_to(self) -> int:
#         return time_utils.xsd_to_ts(self.ts_date_to)
#
#
# @ki_object("market-offer-info-query", result=True)
# class MarketOfferInfoResponse(BindingsBase):
#     market_uri: URIRef
#     offer_uri: URIRef
#     time_create: Literal
#
#     @property
#     def create_ts(self):
#         return time_utils.xsd_to_ts(self.time_create)
#
#
# @ki_object("market-offer-info")
# class MarketOfferInfoBindings(BindingsBase):
#     market_uri: URIRef
#     offer_uri: URIRef
#     time_create: Literal
#
#     def __init__(self, **kwargs):
#         super().__init__(bindings=kwargs)
#
#     @property
#     def create_ts(self):
#         return time_utils.xsd_to_ts(self.time_create)
#
#     @property
#     def isp_unit(self) -> int:
#         from tm.modules.ke_interaction import KIVars
#         res = from_n3(KIVars.ISP_UNIT)
#         return int(parse_duration(res, as_timedelta_if_possible=True).total_seconds() / 60)
#
#     @property
#     def isp_len(self) -> int:
#         from tm.modules.ke_interaction import KIVars
#         res = from_n3(KIVars.DAY_DURATION)
#         day_duration = int(parse_duration(res, as_timedelta_if_possible=True).total_seconds() / 60)
#         isp_unit = self.isp_unit
#         if day_duration % isp_unit == 0:
#             return int(day_duration / isp_unit)
#             # TODO: raise exception ? the last isp is going to have different length
#         return int(day_duration / isp_unit) + 1
#
# @ki_object("market-offer-info",allow_partial=True)
# class MarketOfferInfoRequest(BindingsBase):
#     market_uri: URIRef
#
# @ki_object("market-offer")
# class MarketOfferBindings(BindingsBase):
#     offer_uri: URIRef
#     dp: URIRef
#     ts: Literal
#     dpr: URIRef
#     value: Union[URIRef, Literal, None]
#
#     def __init__(self, **kwargs):
#         super().__init__(bindings=kwargs)
#
#     @property
#     def ts_ms(self) -> int:
#         return time_utils.xsd_to_ts(self.ts)
#
#     def get_value(self) -> Optional[float]:
#         return self.convert_value(self.value,float)
#
#
# @ki_object("market-offer",allow_partial=True)
# class MarketOfferRequest(BindingsBase):
#     offer_uri: URIRef
#
#

@ki_split_uri(uri_template="https://ubeflex.bluebird.eu/country/${country_name}")
class CountryURI(SplitURIBase):
    # TODO use different country uri prefix
    country_name: str

# @ki_split_uri(uri_template="http://bluebird.com/interval/${ts_from}/${ts_to}")
# class TimeIntervalUri(SplitURIBase):
#     ts_from: int
#     ts_to: int
