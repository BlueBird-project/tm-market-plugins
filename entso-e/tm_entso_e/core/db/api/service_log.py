from abc import abstractmethod
from typing import Optional, Dict, Any, List

from tm_entso_e.utils import  TimeSpan
from effi_onto_tools.db.dao import DAO

from tm_entso_e.schemas.service_log import ServiceLogDAO


class ServiceLogAPI(DAO):

    @abstractmethod
    def list(self, ts: TimeSpan, tag: Optional[str]) -> List[ServiceLogDAO]:
        pass

    @abstractmethod
    def has_tag(self, ts: TimeSpan, tag: str) -> int:
        pass

    @abstractmethod
    def log(self, log_item: ServiceLogDAO):
        pass

    @abstractmethod
    def list_job_state(self, ts: TimeSpan, tag: Optional[str]) -> List[ServiceLogDAO]:
        pass
