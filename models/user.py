
from pydantic import BaseModel
from typing import List, Optional

class UserInitRequest(BaseModel):
    xrpl_wallet_address: Optional[str] = None
    evm_wallet_address: Optional[str] = None
    risk_profile: str
    experience: List[str]
    delegated: Optional[bool] = False
    delegated_at: Optional[str] = None
