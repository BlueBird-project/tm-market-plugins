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
    update_time: Optional[int] = None
    offer_mwh: Optional[float] = None
    capacity_obligation: Optional[float] = None
    offer_ack_mwh: Optional[float] = None
    capacity_ack_obligation: Optional[float] = None
    current_baseline_id: Optional[float] = None
    # contract_ack: bool = False
    ack_ts: Optional[int] = None


@dataclass
class CertifiedBaselineDAO:
    baseline_id: int
    update_time: Optional[int] = None


@dataclass
class BaselineDAO:
    baseline_id: int
    contract_id: int
    baseline_isp: Optional[int] = None
    isp_len: Optional[int] = None
    baseline_value: Optional[float] = None


@dataclass
class CapacityPowerDAO:
    ts: int
    granularity_ms: int
    value: Optional[float] = None
