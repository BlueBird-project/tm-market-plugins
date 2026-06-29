from abc import abstractmethod
from typing import Optional, Dict, Any

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO


class ServiceLogAPI(DAO):

    @abstractmethod
    def list(self, ts: TimeSpan, tag: Optional[str]) -> list[ServiceLogDAO]:
        pass

    @abstractmethod
    def log(self, log_item: ServiceLogDAO):
        pass
