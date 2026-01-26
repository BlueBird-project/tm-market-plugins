from typing import Optional

from pydantic import BaseModel


class Market(BaseModel):
    market_id: Optional[int] = None
    market_uri: str
    market_name: str
    market_type: str
    market_description: Optional[str] = None
    market_location: Optional[str] = None
    subscribe: bool
    update_ts: Optional[int] = None
    ext: Optional[str] = None
