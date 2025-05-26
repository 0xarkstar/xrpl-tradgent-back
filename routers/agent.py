from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.langchain_agent import agent_executor
from langchain_core.messages import AIMessage

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

    try:
        result = await agent_executor.ainvoke({
            "messages": [{"role": "user", "content": context}]
        })

        messages = result["messages"]
        
        # LangChain 메시지 객체에서 assistant 역할인 AIMessage 찾아 추출
        final_message = next(
            (m for m in reversed(messages) if isinstance(m, AIMessage)),
            None
        )

        if final_message:
            return {"answer": final_message.content}
        else:
            return {"answer": "에이전트 응답을 찾을 수 없습니다."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 이 코드는 FastAPI를 사용하여 LangChain 에이전트와 상호작용하는 API 엔드포인트를 정의합니다.
# 사용자가 지갑 주소, 투자 성향, 경험, 질문을 입력하면 LangChain 에이전트가 해당 정보를 바탕으로 답변을 생성합니다.