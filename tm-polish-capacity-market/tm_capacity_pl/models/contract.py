from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from zoneinfo import ZoneInfo

from ke_client.utils import time_utils
from ke_client.utils.enum_utils import EnumItem, BaseEnum


# class PowerDirection(BaseEnum):
#     PRODUCTION = EnumItem(1)
#     CONSUMPTION = EnumItem(0)

# =====================================================
# Positive power is consumption , negative production
# =====================================================

@dataclass
class FlexRequest:
    flex_request_uri: str
    offer_period_uri: str
    create_ts: int
    ts_from: int
    ts_to: int


@dataclass
class FlexOffer:
    flex_request_uri: str
    asset_manager_uri: str
    flex_profile_uri: str
    profile_price_uri: str
    flex_price: float
    ts: int
    flex_value: float
    update_ts: Optional[int] = None


@dataclass
class FlexPriceOffer:
    flex_request_uri: str
    asset_manager_uri: str
    flex_profile_uri: str
    profile_price_uri: str
    flex_price: float
    ts: int
    flex_value: float
    price_value: float
    update_ts: Optional[int] = None
    cost_update_ts: Optional[int] = None


@dataclass
class FlexContract:
    contract_uri: str
    flex_request_uri: str
    ack_ts: int
    asset_manager_id: int
    flex_value: Optional[int] = None
    price_value: Optional[float] = None
    update_ts: Optional[int] = None




#
# @dataclass
# class FlexContract:
#     asset_manager_uri: str
#     flex_request_uri: str
#     contract_uri: str
#     market_uri: str
#
#     flex_dp_uri: str
#     cost_dp_uri: str
#     flex_dpr_uri: str
#     cost_dpr_uri: str
#     flex_value: float
#     price_value: float
#
#     period_uri_uri: str
#     ts_date_from: int
#     ts_date_to: int
#     ack: bool = False
#     ack_ts: Optional[int] = None
#     ts: Optional[int] = None
#     update_ts: Optional[int] = None
#

# @dataclass
# class BaselineDAO:
#     baseline_id: int
#     baseline_date: str
#     # contract_id: Optional[int] = None
#     update_time: Optional[int] = None


#
# @dataclass
# class BaselineValueDAO:
#     baseline_id: int
#     baseline_isp: Optional[int] = None
#     isp_len: Optional[int] = None
#     baseline_value: Optional[float] = None
#
#
@dataclass
class BaselineValue:
    ts: int
    baseline_isp: Optional[int]
    baseline_value: Optional[float]
    isp_len: Optional[int]


#
#
# @dataclass
# class Baseline:
#     baseline_id: int
#     values: List[BaselineValueDAO]
#     # contract_id: Optional[int] = None
#     update_time: Optional[int] = None


@dataclass
class ConsumptionPowerDAO:
    ts: int
    granularity_ms: int
    value: Optional[float] = None


@dataclass
class ConsumptionPower(ConsumptionPowerDAO):
    _datetime: Optional[datetime] = field(default=None, repr=False, compare=False)
    _tz: Optional[ZoneInfo] = field(default=None, repr=False, compare=False)

    def set_timezone(self, tzinfo: ZoneInfo):
        self._tz = tzinfo
        self._datetime = None
        return self

    @property
    def dt(self):
        """
        :return: datetime
        """
        # tzinfo = self._tz if tzinfo is None else tzinfo
        if self._datetime is None:
            if self._tz is None:
                dt = time_utils.from_timestamp(ts_ms=self.ts)
            else:
                dt = time_utils.from_timestamp(ts_ms=self.ts).replace(tzinfo=self._tz)
            self._datetime = dt
        return self._datetime
