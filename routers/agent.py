from fastapi import APIRouter
from pydantic import BaseModel
from services.agent import run_bridge_agent
import asyncio

router = APIRouter()

class BridgeAgentRequest(BaseModel):
    query: str
    sender_seed: str = None
    evm_dest: str = None
    amount_drops: str = None
    private_key: str = None
    xrpl_dest: str = None
    amount_wei: int = None
    axelar_chain: str = "xrpl-evm-sidechain"

@router.post("/agent/bridge")
async def bridge_agent(req: BridgeAgentRequest):
    result = await run_bridge_agent(
        req.query,
        req.sender_seed,
        req.evm_dest,
        req.amount_drops,
        req.private_key,
        req.xrpl_dest,
        req.amount_wei,
        req.axelar_chain
    )
    return {"result": result}
