from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from xrpl.wallet import generate_faucet_wallet

from mcp_tools import xrpl_executor, bridge_executor
from xrpl.asyncio.clients import AsyncJsonRpcClient
from config import settings


client = AsyncJsonRpcClient(settings.XRPL_JSON_RPC_URL)
router = APIRouter()

test_wallets = []

class PaymentTestRequest(BaseModel):
    sender_index: int
    receiver_index: int
    amount_drops: str

class DelegatePaymentTestRequest(BaseModel):
    sender_index: int
    delegated_sender_index: int
    receiver_index: int
    amount_drops: str


class AMMDepositTestRequest(BaseModel):
    sender_index: int
    asset1: dict
    asset2: dict
    amount1: str = None
    amount2: str = None
    flags: int = None

class BridgeTestRequest(BaseModel):
    sender_index: int
    evm_dest: str
    amount_drops: str
    axelar_chain: str = "xrpl-evm"

class AMMDepositXrpTestRequest(BaseModel):
    sender_index: int
    xrp_amount: str = "0.5"

class SetTrustlineTestRequest(BaseModel):
    sender_index: int
    issuer_address: str = "rQhWct2fv4Vc4KRjRgMrxa8xPN9Zx9iLKV"
    currency_code: str  = "RLUSD"
    limit_amount : str = "1000000000"

class DelegatePermissionTestRequest(BaseModel):
    sender_index: int = 0
    receiver_index: int = 1
    permission: str =  "Payment"

@router.post("/xrpl/test-wallets")
def create_test_wallets(count: int = 3):
    global test_wallets
    test_wallets = []
    for _ in range(count):
        wallet = generate_faucet_wallet(client, debug=True)
        test_wallets.append({
            "classic_address": wallet.classic_address,
            "public_key": wallet.public_key,
            "private_key": wallet.private_key,
            "seed": wallet.seed,
        })
    return {"wallets": test_wallets}


@router.get("/xrpl/test-wallets")
async def get_test_wallets():
    return {"wallets": test_wallets}


@router.post("/xrpl/test-payment")
async def send_test_payment(req: PaymentTestRequest):
    sender = test_wallets[req.sender_index]
    receiver = test_wallets[req.receiver_index]
    result = await xrpl_executor.send_payment(
        seed=sender["seed"],
        destination=receiver["classic_address"],
        amount_drops=req.amount_drops
    )
    return {"tx_result": result}

@router.post("/xrpl/test-delegate-payment")
async def send_test_delegate_payment(req: DelegatePaymentTestRequest):
    sender = test_wallets[req.sender_index]
    delegated_sender = test_wallets[req.delegated_sender_index]
    receiver = test_wallets[req.receiver_index]
    result = await xrpl_executor.delegate_send_payment(
        seed=delegated_sender["seed"],
        org_account=sender["classic_address"],
        destination=receiver["classic_address"],
        amount_drops=req.amount_drops
    )
    return {"tx_result": result}






# XRPL → EVM 브릿지 테스트 엔드포인트 (XRP)

@router.post("/test/bridge/test-xrpl-to-evm")
async def test_xrp_bridge(req: BridgeTestRequest):
    """
    sender_index, evm_dest, amount_drops, axelar_chain을 받아 bridge_xrp_to_evm 호출
    """
    try:
        sender = test_wallets[req.sender_index]
        seed = sender["seed"]
        result = await bridge_executor.bridge_xrp_to_evm(
            seed=seed,
            amount_drops=req.amount_drops,
            evm_dest=req.evm_dest,
            axelar_chain=req.axelar_chain
        )
        return {"status": "success", "result": result}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Bridge failed: {str(e)}")

# trustline 설정 테스트 엔드포인트
@router.post("/test/amm/set-trustline")
async def create_trustline(req:SetTrustlineTestRequest):
    """
    sender_index, issuer_address, currency_code, limit_amount를 받아 create_trustline 호출
    """
    try:
        sender = test_wallets[req.sender_index]
        seed = sender["seed"]
        result = await xrpl_executor.create_trustline(
            seed = seed,
            issuer_address = req.issuer_address,
            currency_code = req.currency_code,
            limit_amount = req.limit_amount
            
        )
        return {"status": "success", "result": result}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"set trustline failed: {str(e)}")

# xrp 단방향 예치 테스트 엔드포인트
@router.post("/test/amm/deposit-single-xrp")
async def amm_deposit_single_xrp(req:AMMDepositXrpTestRequest):
    """
    sender_index, xrp_amount를 받아 amm_deposit_single_xrp를 호출
    """
    try:
        sender = test_wallets[req.sender_index]
        seed = sender["seed"]
        result = await xrpl_executor.amm_deposit_single_xrp(
            seed = seed,
            xrp_amount = req.xrp_amount
        )
        return {"status": "success", "result": result }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Deposit failed: {str(e)}")

@router.post("/test/delegation/delegate-permission")
async def test_delegate_permission(req:DelegatePermissionTestRequest):
    """
    sender_index, receiver_index, Permission을 받아 delegate_permission을 호출 
    """
    try:
        sender = test_wallets[req.sender_index]
        receiver = test_wallets[req.receiver_index]
        response = await xrpl_executor.delegate_permission(
            seed = sender["seed"],
            delegated_account = receiver["classic_address"],
            permission = req.permission
        )
        return {"status": "success", "result": response}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Delegation failed: {str(e)}")