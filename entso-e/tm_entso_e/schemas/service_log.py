import logging
from dataclasses import dataclass
from typing import Optional

from tm_entso_e.utils import time_utils

ERROR_TAG="ERROR"
@dataclass
class ServiceLogDAO:
    log_tag: str
    log_message: str
    log_ts: int
    log_id: Optional[int] = None
    log_obj_type: Optional[str] = None
    log_obj_json: Optional[str] = None
    log_context: Optional[str] = None

    def __post_init__(self):
        if len(self.log_message) > 95:
            logging.warning(f"trim log message: {self.log_message}")
            self.log_message = self.log_message[0:95] + "..."
