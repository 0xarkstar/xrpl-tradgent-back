from typing import List, Optional
from pydantic import BaseModel

class SurveyData(BaseModel):
    ceFiExperience: List[str]
    deFiExperience: List[str]
    riskPreference: str
    xrpl_wallet_address: str
