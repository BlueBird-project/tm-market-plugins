from dataclasses import dataclass
from typing import Optional


@dataclass
class AssetManager:
    asset_manager_uri: str
    asset_manager_id: Optional[int] = None


@dataclass
class PowerDemandDAO:
    # date timestamp in milliseconds
    ts: int
    # start hour (0-23)
    demand_start: int
    # end hour (0-23)
    demand_end: int
    capacity_obligation_ratio: float
    contracted_capacity: float
    max_power: float
    update_time: Optional[int] = None

    @property
    def demand_start_ts_ms(self):
        return self.ts + self.demand_start * 3600000


# @dataclass
# class BaselineCorrection:
#     demand_id: int
#     baseline_id: int
#     # max_correction:float
#     baseline_correction: float
#     baseline_final: float


@dataclass
class DeliveredCapacity:
    asset_manager_id: int
    flex_instruction: str
    flex_offer: str
    flex_profile: str
    power_limit: str
    max_consumption: str
    ts: int
    expected_capacity: float
    delivered_capacity: float
    max_consumption_value: float


@dataclass
class MarketNotification:
    notification_id: int
    email: str
    date: str
    isp: int
    ts: int


@dataclass
class KECapacityNotification:
    asset_manager_id: int
    flex_instruction_uri: str
    flex_offer_uri: str
    flex_profile_uri: str
    power_limit_uri: str
    ts: int
    max_consumption_uri: str
    max_consumption_value: float
    update_ts: int
