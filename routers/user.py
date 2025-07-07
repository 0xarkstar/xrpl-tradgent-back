
from fastapi import APIRouter, HTTPException
from models.user import UserInitRequest
from db.queries import (
    insert_user, get_user_by_xrpl_address, get_user_by_evm_address,
    update_user_delegate, update_user_risk_profile
)
from typing import List, Optional
from pydantic import BaseModel

from config import settings
from mcp_tools import xrpl_executor

class DelegatePermissionRequest(BaseModel):
    user_wallet_seed: str # WARNING: This is highly insecure for production. User's seed should not be sent to backend.
    xrpl_wallet_address: str
    permission_type: str = "Payment" # Default to Payment, can be extended


router = APIRouter()

class DelegateRequest(BaseModel):
    xrpl_wallet_address: str
    delegated: bool
    delegated_at: Optional[str] = None

class RiskProfileRequest(BaseModel):
    xrpl_wallet_address: str
    risk_profile: str
    experience: List[str]

@router.post("/api/user/delegate")
async def delegate_user(req: DelegateRequest):
    user = await get_user_by_xrpl_address(req.xrpl_wallet_address)
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    result = await update_user_delegate(req.xrpl_wallet_address, req.delegated, req.delegated_at)
    return {"success": True, "data": result.data}

@router.post("/api/user/set_risk_profile")
async def set_risk_profile(req: RiskProfileRequest):
    user = await get_user_by_xrpl_address(req.xrpl_wallet_address)
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    result = await update_user_risk_profile(req.xrpl_wallet_address, req.risk_profile, req.experience)
    return {"success": True, "data": result.data}

@router.post("/api/user/register")
async def register_user(user: UserInitRequest):
    print(f"[DEBUG] Register user request received: {user.dict()}")
    # 중복 지갑주소 체크
    if user.xrpl_wallet_address:
        existing_xrpl = await get_user_by_xrpl_address(user.xrpl_wallet_address)
        print(f"[DEBUG] Existing XRPL user check result: {existing_xrpl}")
        if existing_xrpl:
            raise HTTPException(status_code=400, detail="이미 등록된 XRPL 지갑주소입니다.")
    if user.evm_wallet_address:
        existing_evm = await get_user_by_evm_address(user.evm_wallet_address)
        print(f"[DEBUG] Existing EVM user check result: {existing_evm}")
        if existing_evm:
            raise HTTPException(status_code=400, detail="이미 등록된 EVM 지갑주소입니다.")

    # 최소 하나의 지갑 주소는 있어야 함
    if not user.xrpl_wallet_address and not user.evm_wallet_address:
        raise HTTPException(status_code=400, detail="최소 하나의 지갑 주소는 제공되어야 합니다.")

    result = await insert_user(user)
    print(f"[DEBUG] User insert result: {result.data}")
    return {"success": True, "data": result.data}

@router.get("/api/user/profile")
async def get_user_profile(xrpl_wallet_address: Optional[str] = None, evm_wallet_address: Optional[str] = None):
    user = None
    if xrpl_wallet_address:
        user = await get_user_by_xrpl_address(xrpl_wallet_address)
    elif evm_wallet_address:
        user = await get_user_by_evm_address(evm_wallet_address)

    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return {"success": True, "data": user}

@router.post("/api/user/delegate_permission")
async def delegate_permission_to_agent(req: DelegatePermissionRequest):
    """
    Delegates a specific permission from the user's wallet to the AI agent's wallet.
    WARNING: This endpoint is highly insecure for production as it requires the user's seed.
    In a production environment, the user should sign the transaction on the frontend
    and send the signed transaction blob to the backend for submission.
    """
    if not settings.AI_AGENT_WALLET_SEED:
        raise HTTPException(status_code=500, detail="AI Agent wallet seed is not configured.")

    # Create AI agent wallet from its seed
    ai_agent_wallet = xrpl_executor.create_wallet_from_seed(settings.AI_AGENT_WALLET_SEED)
    ai_agent_address = ai_agent_wallet.classic_address

    try:
        # Delegate permission from user's wallet to AI agent's wallet
        result = await xrpl_executor.delegate_permission(
            seed=req.user_wallet_seed,
            delegated_account=ai_agent_address,
            permission=req.permission_type
        )
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"Permission delegation failed: {result['error']}")
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during delegation: {str(e)}")
