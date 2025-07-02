from fastapi import APIRouter
from pydantic import BaseModel
from mcp_tools import xrpl_executor, evm_executor, bridge_executor
import asyncio

router = APIRouter()

# XRPL Payment
class XRPLPaymentRequest(BaseModel):
    sender_seed: str
    destination: str
    amount_drops: str

@router.post("/xrpl/send-payment")
def send_payment_api(req: XRPLPaymentRequest):
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

# XRPL AMM Deposit
class XRPLAMMDepositRequest(BaseModel):
    sender_seed: str
    asset1: dict
    asset2: dict
    amount1: str = None
    amount2: str = None
    flags: int = None

@router.post("/xrpl/amm-deposit")
def deposit_to_amm(req: XRPLAMMDepositRequest):
    result = xrpl_executor.deposit_to_amm(
        req.sender_seed, req.asset1, req.asset2, req.amount1, req.amount2, req.flags
    )
    return {"result": result}


# XRPL to EVM Bridge (XRP)
class BridgeXRPLToEVMRequest(BaseModel):
    sender_seed: str
    evm_dest: str
    amount_drops: str
    axelar_chain: str = "xrpl-evm"

@router.post("/bridge/xrpl-to-evm")
async def bridge_to_evm(req: BridgeXRPLToEVMRequest):
    result = bridge_executor.bridge_xrp_to_evm(
        req.sender_seed, req.evm_dest, req.amount_drops, req.axelar_chain
    )
    return {"result": result}

# EVM to XRPL Bridge
class BridgeEVMToXRPLRequest(BaseModel):
    private_key: str
    xrpl_dest: str
    amount_wei: int
    axelar_chain: str = "xrpl-evm"
    token_address: str = None

@router.post("/bridge/evm-to-xrpl")
async def bridge_to_xrpl(req: BridgeEVMToXRPLRequest):
    result = bridge_executor.bridge_evm_to_xrpl(
        req.private_key, req.xrpl_dest, req.amount_wei, req.axelar_chain, req.token_address
    )
    return {"result": result}

# LangChain Bridge Agent
class BridgeAgentRequest(BaseModel):
    query: str
    sender_seed: str = None
    evm_dest: str = None
    amount_drops: str = None
    currency: str = None
    issuer: str = None
    amount: str = None
    private_key: str = None
    xrpl_dest: str = None
    amount_wei: int = None
    axelar_chain: str = "xrpl-evm"

# EVM Balance
class EVMBalanceRequest(BaseModel):
    address: str

@router.post("/evm/get-balance")
def get_evm_balance(req: EVMBalanceRequest):
    balance = evm_executor.get_eth_balance(req.address)
    return {"balance_wei": balance}

# EVM Send
class EVMSendRequest(BaseModel):
    private_key: str
    destination: str
    amount_wei: int

@router.post("/evm/send")
def send_token_evm(req: EVMSendRequest):
    result = evm_executor.send_native_token(req.private_key, req.destination, req.amount_wei)
    return {"tx_receipt": result}

# EVM Liquidity (Dummy)
@router.post("/evm/add-liquidity")
def add_liquidity():
    return {"result": evm_executor.dummy_uniswap_add_liquidity()}