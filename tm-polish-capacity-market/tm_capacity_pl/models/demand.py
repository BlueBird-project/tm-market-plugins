from dataclasses import dataclass
from typing import Optional


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
    demand_id: int
    baseline: float
    expected_capacity: float
    delivered_capacity: float
