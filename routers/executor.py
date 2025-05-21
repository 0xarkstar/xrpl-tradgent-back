from fastapi import APIRouter
from pydantic import BaseModel
from services import (
    xrpl_executor,
    xrpl_evm_executor,
    bridge_executor,
    evm_executor,
    evm_bridge_executor
)

router = APIRouter()

# XRPL Payment
class XRPLPaymentRequest(BaseModel):
    sender_seed: str
    destination: str
    amount_drops: str

@router.post("/xrpl/send-payment")
def send_payment(req: XRPLPaymentRequest):
    result = xrpl_executor.send_payment(req.sender_seed, req.destination, req.amount_drops)
    return {"result": result}


# XRPL 잔액 조회
class XRPLBalanceRequest(BaseModel):
    address: str

@router.post("/xrpl/get-balance")
def get_balance(req: XRPLBalanceRequest):
    balance = xrpl_executor.get_account_balance(req.address)
    return {"balance": balance}


# XRPL Offer 생성
class XRPLOfferRequest(BaseModel):
    sender_seed: str
    taker_gets: str
    taker_pays: dict  # {"currency": "USD", "issuer": "r..."}

@router.post("/xrpl/create-offer")
def create_offer(req: XRPLOfferRequest):
    result = xrpl_executor.create_offer(req.sender_seed, req.taker_gets, req.taker_pays)
    return {"result": result}


# XRPL → XRPL EVM 브릿지
class BridgeToEVMRequest(BaseModel):
    sender_seed: str
    evm_dest: str
    amount_drops: str

@router.post("/bridge/xrpl-to-evm")
def bridge_to_evm(req: BridgeToEVMRequest):
    result = bridge_executor.bridge_xrp_to_evm(req.sender_seed, req.evm_dest, req.amount_drops)
    return {"result": result}


# XRPL EVM: 잔액 조회
class XRPLEVMBalanceRequest(BaseModel):
    address: str

@router.post("/xrpl-evm/get-balance")
def get_evm_balance(req: XRPLEVMBalanceRequest):
    balance = xrpl_evm_executor.get_eth_balance(req.address)
    return {"balance_wei": balance}


# XRPL EVM: 토큰 전송
class XRPLEVMSendRequest(BaseModel):
    private_key: str
    destination: str
    amount_wei: int

@router.post("/xrpl-evm/send")
def send_token_evm(req: XRPLEVMSendRequest):
    result = xrpl_evm_executor.send_native_token(req.private_key, req.destination, req.amount_wei)
    return {"tx_receipt": result}


# Dummy: EVM 유동성 추가
@router.post("/evm/add-liquidity")
def dummy_add_liquidity():
    return {"result": evm_executor.dummy_uniswap_add_liquidity()}


# Dummy: EVM 브릿지
@router.post("/bridge/evm-to-other")
def dummy_evm_bridge():
    return {"result": evm_bridge_executor.dummy_bridge_to_other_chain()}
