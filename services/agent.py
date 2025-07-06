"""
LangGraph 공식 튜토리얼 베스트 프랙티스 기반 XRPL DeFi 파밍 에이전트
- State 구조 확장, prebuilt ToolNode/조건, SqliteSaver checkpointer, human-in-the-loop 확장성
"""
# 시스템 프롬프트: DeFi 파밍 역할 제한
SYSTEM_PROMPT = (
    "당신은 DeFi 파밍 전략 추천 및 실행만 담당하는 AI 에이전트입니다. "
    "사용자 정보를 조회하려면 `get_user_profile` 툴을 사용하세요. "
    "DeFi 파밍과 무관한 질문이나 명령에는 반드시 '죄송합니다. 저는 DeFi 파밍 관련 업무만 도와드릴 수 있습니다.'라고 답변하세요."
)

from typing import Annotated, List, Optional
import graphviz
from db.queries import get_user_by_address
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, FunctionMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.postgres import PostgresSaver
from config import settings
from mcp_tools.mcp_instance import mcp
import os

# LLM 및 툴 준비
llm = ChatOpenAI(model="gpt-4.1", temperature=0, streaming=True)

# State 구조 확장 예시 (필요시 커스텀 필드 추가)
from typing_extensions import TypedDict
class AgentState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    farming_params: Optional[dict]
    approval: Optional[bool]
    # ...추가 필드 확장 가능

# LLM 노드
async def chatbot_node(state: AgentState):
    return {"messages": [await llm.ainvoke(state["messages"])]}

_agent_executor_instance = None # Global variable to store the initialized executor

async def _initialize_agent_executor():
    global _agent_executor_instance
    if _agent_executor_instance is not None:
        return _agent_executor_instance

    tools = await mcp.get_tools() # Await the coroutine

    # prebuilt ToolNode 사용
    tool_node = ToolNode(tools=tools)

    # StateGraph 빌드
    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("chatbot", chatbot_node)
    graph_builder.add_node("tools", tool_node)

    # 조건부 분기: prebuilt tools_condition 사용
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")

    # Supabase(PostgreSQL) 연결 정보 환경변수에서 읽기
    POSTGRES_CONN_STR = getattr(settings, "POSTGRES_CONNECTION_STRING", None)

    if POSTGRES_CONN_STR:
        checkpointer = PostgresSaver(POSTGRES_CONN_STR)
    else:
        raise RuntimeError("PostgreSQL 연결 정보가 없습니다. POSTGRES_CONNECTION_STRING 환경 변수를 확인하세요.")

    # 그래프 컴파일
    _agent_executor_instance = graph_builder.compile(checkpointer=checkpointer)
    return _agent_executor_instance

# 시작점 설정

# (구버전 워크플로우/노드/엣지/컴파일 코드 제거됨)

async def get_agent():    return await _initialize_agent_executor()

async def arun_agent(query: str, user_id: str):
    """
    사용자별로 대화 맥락을 유지하며 에이전트를 비동기 실행합니다.
    """
    agent_executor = await _initialize_agent_executor()
    prompt = SYSTEM_PROMPT + "\n" + query
    inputs = {"messages": [HumanMessage(content=prompt)]}
    response = await agent_executor.ainvoke(inputs, config={"configurable": {"thread_id": user_id}})
    if response and response["messages"]:
        return {"response": response["messages"][-1].content}
    return {"response": "No response from agent."}

async def stream_agent(query: str, user_id: str):
    agent_executor = await _initialize_agent_executor()
    prompt = SYSTEM_PROMPT + "\n" + query
    inputs = {"messages": [HumanMessage(content=prompt)]}
    async for chunk in agent_executor.astream(inputs, config={"configurable": {"thread_id": user_id}}):
        if "messages" in chunk and chunk["messages"]:
            last_message = chunk["messages"][-1]
            if isinstance(last_message, AIMessage):
                yield {"response": last_message.content}
            elif isinstance(last_message, FunctionMessage):
                yield {"tool_output": last_message.content, "tool_name": last_message.name}

async def get_agent_png(user_id: str = "test_user"):
    agent_executor = await _initialize_agent_executor()
    # (디버깅용) 현재 에이전트의 상태 그래프를 PNG 이미지로 생성합니다.
    pass
