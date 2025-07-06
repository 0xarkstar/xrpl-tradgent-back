from fastapi import APIRouter
from pydantic import BaseModel
from mcp_tools import xrpl_executor, evm_executor, bridge_executor

router = APIRouter()

# XRPL Payment
class XRPLPaymentRequest(BaseModel):
    sender_seed: str
    destination: str
    amount_drops: str

@router.post("/xrpl/send-payment")
async def send_payment_api(req: XRPLPaymentRequest):
    result = await xrpl_executor.send_payment(req.sender_seed, req.destination, req.amount_drops)
    return {"result": result}


# XRPL 잔액 조회
class XRPLBalanceRequest(BaseModel):
    address: str

@router.post("/xrpl/get-balance")
async def get_balance(req: XRPLBalanceRequest):
    balance = await xrpl_executor.get_account_balance(req.address)
    return {"balance": balance}


# XRPL Offer 생성


# XRPL AMM Deposit



# XRPL to EVM Bridge (XRP)
class BridgeXRPLToEVMRequest(BaseModel):
    sender_seed: str
    evm_dest: str
    amount_drops: str
    axelar_chain: str = "xrpl-evm"

@router.post("/bridge/xrpl-to-evm")
async def bridge_to_evm(req: BridgeXRPLToEVMRequest):
    result = await bridge_executor.bridge_xrp_to_evm(
        req.sender_seed, req.evm_dest, req.amount_drops, req.axelar_chain
    )
    return {"result": result}

# EVM to XRPL Bridge


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
async def get_evm_balance(req: EVMBalanceRequest):
    balance = await evm_executor.get_eth_balance(req.address)
    return {"balance_wei": balance}

# EVM Send
class EVMSendRequest(BaseModel):
    private_key: str
    destination: str
    amount_wei: int

@router.post("/evm/send")
async def send_token_evm(req: EVMSendRequest):
    result = await evm_executor.send_native_token(req.private_key, req.destination, req.amount_wei)
    return {"tx_receipt": result}

# EVM Liquidity (Dummy)
@router.post("/evm/add-liquidity")
async def add_liquidity():
    return {"result": await evm_executor.dummy_uniswap_add_liquidity()}