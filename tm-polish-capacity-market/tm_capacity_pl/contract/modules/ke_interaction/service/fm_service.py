from collections import defaultdict
from typing import List, Dict, Callable, Union

from tm_capacity_pl.contract.modules.ke_interaction.interactions.fm_model import FMPnt
from tm_capacity_pl.models.contract import CapacityPowerDAO


def process_data_points(granularity_ms: int, power_ts: List[FMPnt]):
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    # sorted_power_list=  sorted(power_ts, key=lambda x: x.ts_ms)
    # p:FMPnt
    power_history = [CapacityPowerDAO(ts=p.ts_ms, granularity_ms=granularity_ms, value=p.get_value(), )
                     for p in power_ts]
    inserted = dao_manager.power_api.log_power(power_history=power_history)
    assert inserted == len(power_history)
