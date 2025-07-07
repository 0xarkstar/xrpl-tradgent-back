from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from services import agent as agent_service # 서비스 계층 import
from typing import Optional

from config import settings # settings 임포트 추가
from mcp_tools import xrpl_executor # xrpl_executor 임포트 추가

router = APIRouter()

# 1. 기존 요청 본문을 위한 Pydantic 모델 정의
class AgentQueryRequest(BaseModel):
    query: str
    user_id: str # 사용자 식별자

# 2. AI Chat 요청 본문을 위한 Pydantic 모델 정의
class AIChatRequest(BaseModel):
    message: str
    user_id: str # user_id로 변경
    context: Optional[dict] = None

# 3. AI Chat 응답 본문을 위한 Pydantic 모델 정의
class AIChatResponse(BaseModel):
    response: str

# 4. 일반 비동기 실행 엔드포인트 (기존)
@router.post("/invoke")
async def invoke_agent(request: AgentQueryRequest):
    """에이전트를 실행하고 최종 결과를 반환합니다."""
    response = await agent_service.arun_agent(request.query, request.user_id)
    return response

# 5. 스트리밍 실행 엔드포인트 (기존)
@router.post("/stream")
async def stream_agent_endpoint(request: AgentQueryRequest):
    """에이전트를 스트리밍 모드로 실행하고 결과를 실시간으로 전송합니다."""
    async def stream_generator():
        async for chunk in agent_service.stream_agent(request.query, request.user_id):
            import json
            yield json.dumps(chunk) + "\n"

    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")

# 6. AI Chat 엔드포인트 추가
@router.post("/chat", response_model=AIChatResponse)
async def chat_with_ai(request: AIChatRequest):
    """AI 에이전트와 채팅하고 응답을 반환합니다."""
    # services/agent.py의 arun_agent 함수 호출
    response = await agent_service.arun_agent(request.message, request.user_id, request.context)
    return AIChatResponse(response=response["response"])

@router.get("/address")
async def get_agent_address():
    """
    AI 에이전트의 XRPL 지갑 주소를 반환합니다.
    """
    if not settings.AI_AGENT_WALLET_SEED:
        raise HTTPException(status_code=500, detail="AI Agent wallet seed is not configured.")
    
    # AI 에이전트 지갑 생성 (시드로부터)
    ai_agent_wallet = xrpl_executor.create_wallet_from_seed(settings.AI_AGENT_WALLET_SEED)
    return {"address": ai_agent_wallet.classic_address}
