
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

from xrpl.asyncio.clients import AsyncJsonRpcClient
from datetime import datetime
from xrpl.core.binarycodec import decode


class SubmitSignedTxRequest(BaseModel):
    signed_tx_blob: str

@router.post("/api/user/submit_signed_tx")
async def submit_signed_transaction_endpoint(req: SubmitSignedTxRequest):
    """
    프론트엔드에서 서명된 트랜잭션 블롭을 받아 XRPL 네트워크에 제출합니다.
    """
    try:
        # XRPL 클라이언트 초기화
        client = AsyncJsonRpcClient(settings.XRPL_JSON_RPC_URL)
        
        # 서명된 트랜잭션 제출
        response = await client.submit(req.signed_tx_blob)
        
        # 응답 확인 및 반환
        if response.result.get("engine_result") == "tesSUCCESS":
            # 트랜잭션 블롭에서 Account (사용자 지갑 주소) 추출
            decoded_tx = decode(req.signed_tx_blob)
            user_xrpl_address = decoded_tx.get("Account")

            if user_xrpl_address:
                # 데이터베이스에 위임 상태 업데이트
                await update_user_delegate(user_xrpl_address, True, datetime.now().isoformat())
                print(f"[DEBUG] User {user_xrpl_address} delegation status updated in DB.")
            else:
                print("[DEBUG] Could not extract Account from signed transaction blob.")

            return {"success": True, "data": response.result}
        else:
            raise HTTPException(status_code=400, detail=f"트랜잭션 제출 실패: {response.result.get('engine_result_message', response.result.get('engine_result'))}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"트랜잭션 제출 중 오류 발생: {str(e)}")
