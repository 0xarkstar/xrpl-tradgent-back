from fastapi import APIRouter
from pydantic import BaseModel
from xrpl.wallet import generate_faucet_wallet
from xrpl.clients import JsonRpcClient
from services import xrpl_executor, bridge_executor


client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
router = APIRouter()

test_wallets = []

class PaymentTestRequest(BaseModel):
    sender_index: int
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
    axelar_chain: str = "xrpl-evm-sidechain"


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
def get_test_wallets():
    return {"wallets": test_wallets}


@router.post("/xrpl/test-payment")
def send_test_payment(req: PaymentTestRequest):
    sender = test_wallets[req.sender_index]
    receiver = test_wallets[req.receiver_index]
    result = xrpl_executor.send_payment(
        seed=sender["seed"],
        destination=receiver["classic_address"],
        amount_drops=req.amount_drops
    )
    return {"tx_result": result}


@router.post("/xrpl/test-amm-deposit")
def test_amm_deposit(req: AMMDepositTestRequest):
    sender = test_wallets[req.sender_index]
    result = xrpl_executor.deposit_to_amm(
        seed=sender["seed"],
        asset1=req.asset1,
        asset2=req.asset2,
        amount1=req.amount1,
        amount2=req.amount2,
        flags=req.flags
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
