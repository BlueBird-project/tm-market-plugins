from dataclasses import dataclass


@dataclass
class PowerDemandDAO:
    create_time: int
    demand_start: int
    demand_end: int
    capacity_obligation_ratio: float
