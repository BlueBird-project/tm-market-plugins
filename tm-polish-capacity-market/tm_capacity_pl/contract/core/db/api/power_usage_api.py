from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO

from tm_capacity_pl.models.contract import CapacityPowerDAO


class PowerUsageAPI(DAO):
    def __init__(self, table_prefix: str):
        super(PowerUsageAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def list_power(self, ts: TimeSpan) -> List[CapacityPowerDAO]:
        pass

    @abstractmethod
    def log_power(self, power_history: List[CapacityPowerDAO]) -> Optional[CapacityPowerDAO]:
        pass
