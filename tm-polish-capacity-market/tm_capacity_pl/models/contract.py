from dataclasses import dataclass
from typing import Optional

from ke_client.utils.enum_utils import EnumItem, BaseEnum


# class PowerDirection(BaseEnum):
#     PRODUCTION = EnumItem(1)
#     CONSUMPTION = EnumItem(0)

# =====================================================
# Positive power is consumption , negative production
# =====================================================

@dataclass
class ContractDAO:
    create_time: int
    update_time: int
    cost_mwh: Optional[float] = None
    # contract_ack: bool = False
    ack_ts: Optional[int] = None


@dataclass
class BaselineDAO:
    contract_id: int
    create_time: int
    update_time: int
    power_span: Optional[float] = None
    baseline: Optional[float] = None
    cost_mwh: Optional[float] = None


class CapacityPowerDAO:
    ts: int
    value: Optional[float] = None
    granularity_ms: int
