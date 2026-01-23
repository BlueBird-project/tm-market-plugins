from typing import List, Optional

from pydantic import BaseModel


class SubscribedEIC(BaseModel):
    code: str
    market_types: List[str]


class EICArea(BaseModel):
    code: str
    area_names: List[str]
    country_codes: Optional[List[str]] = None
