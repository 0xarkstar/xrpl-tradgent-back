# routers/agent.py
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from services import agent as agent_service # 서비스 계층 import

router = APIRouter()

# 1. 요청 본문을 위한 Pydantic 모델 정의
class AgentQueryRequest(BaseModel):
    query: str
    user_id: str # 사용자 식별자

# 2. 일반 비동기 실행 엔드포인트
@router.post("/invoke")
async def invoke_agent(request: AgentQueryRequest):
    """에이전트를 실행하고 최종 결과를 반환합니다."""
    response = await agent_service.arun_agent(request.query, request.user_id)
    return response

# 3. 스트리밍 실행 엔드포인트
@router.post("/stream")
async def stream_agent_endpoint(request: AgentQueryRequest):
    """에이전트를 스트리밍 모드로 실행하고 결과를 실시간으로 전송합니다."""
    # 제너레이터를 StreamingResponse로 감싸서 반환합니다.
    async def stream_generator():
        async for chunk in agent_service.stream_agent(request.query, request.user_id):
            # 스트림 청크를 클라이언트에 맞게 포맷팅 (예: JSON 문자열)
            # 이 부분은 클라이언트 구현에 따라 달라질 수 있습니다.
            import json
            yield json.dumps(chunk) + "\n"

    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")
