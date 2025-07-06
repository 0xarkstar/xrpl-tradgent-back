
from fastapi import APIRouter, HTTPException
from models.user import UserInitRequest
from db.queries import (
    insert_user, get_user_by_address,
    update_user_delegate, update_user_risk_profile
)
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class DelegateRequest(BaseModel):
    wallet_address: str
    delegated: bool
    delegated_at: Optional[str] = None

class RiskProfileRequest(BaseModel):
    wallet_address: str
    risk_profile: str
    experience: List[str]

@router.post("/api/user/delegate")
def delegate_user(req: DelegateRequest):
    user = get_user_by_address(req.wallet_address)
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    result = update_user_delegate(req.wallet_address, req.delegated, req.delegated_at)
    return {"success": True, "data": result.data}

@router.post("/api/user/set_risk_profile")
def set_risk_profile(req: RiskProfileRequest):
    user = get_user_by_address(req.wallet_address)
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    result = update_user_risk_profile(req.wallet_address, req.risk_profile, req.experience)
    return {"success": True, "data": result.data}

@router.post("/api/user/register")
def register_user(user: UserInitRequest):
    # 중복 지갑주소 체크
    existing = get_user_by_address(user.wallet_address)
    if existing:
        raise HTTPException(status_code=400, detail="이미 등록된 지갑주소입니다.")
    result = insert_user(user)
    return {"success": True, "data": result.data}

@router.get("/api/user/profile")
def get_user_profile(wallet_address: str):
    user = get_user_by_address(wallet_address)
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return {"success": True, "data": user}
