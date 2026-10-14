from dataclasses import dataclass
from typing import Optional


@dataclass
class PowerDemandDAO:
    ts: int
    demand_start: int
    demand_end: int
    capacity_obligation_ratio: float
    contracted_capacity:float
    max_power:float
    update_time: Optional[int] = None


@dataclass
class BaselineCorrection:
    demand_id: int
    baseline_id: int
    # max_correction:float
    baseline_correction: float
    baseline_final: float


@dataclass
class DeliveredCapacity:
    demand_id: int
    baseline: float
    expected_capacity: float
    delivered_capacity: float
