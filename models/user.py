from pydantic import BaseModel
from typing import List

class UserInitRequest(BaseModel):
    wallet_address: str
    risk_profile: str
    experience: List[str]
