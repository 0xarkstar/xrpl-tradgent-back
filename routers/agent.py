from fastapi import APIRouter
from pydantic import BaseModel
from services.langchain_agent import agent_executor

router = APIRouter()

class AgentRequest(BaseModel):
    wallet_address: str
    risk_profile: str
    experience: list[str]
    question: str  # ex: "내 XRP로 지금 어떤 전략이 좋아?"

@router.post("/ask")
async def ask_agent(req: AgentRequest):
    context = (
        f"지갑 주소: {req.wallet_address}, "
        f"투자 성향: {req.risk_profile}, "
        f"경험: {', '.join(req.experience)}\n"
        f"질문: {req.question}"
    )

    result = agent_executor.run(context)
    return {"answer": result}
