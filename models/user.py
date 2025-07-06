
from pydantic import BaseModel
from typing import List, Optional

class UserInitRequest(BaseModel):
    wallet_address: str
    risk_profile: str
    experience: List[str]
    delegated: Optional[bool] = False
    delegated_at: Optional[str] = None
