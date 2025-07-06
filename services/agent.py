

from typing import Annotated, List, Optional
import graphviz
from db.queries import get_user_by_address
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, FunctionMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from config import settings
import logging
import os
from config.settings import SYSTEM_PROMPT
from psycopg_pool import AsyncConnectionPool
from functools import partial
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient


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

    try:
        logging.info("Initializing agent executor...")
        # MCP 서버 URL (mcp_server.py가 실행되는 주소)
        mcp_server_url = settings.MCP_SERVER_URL
        
        # MultiServerMCPClient를 인스턴스화합니다.
        # 이 클라이언트는 MCP 서버에 대한 연결 정보를 관리합니다.
        # 단일 서버의 경우에도 이 클라이언트를 통해 도구를 가져오는 것이 권장됩니다.
        mcp_client = MultiServerMCPClient(connections={"default": {"url": f"{mcp_server_url}/mcp", "transport": "streamable_http"}})
        
        # mcp_client의 get_tools() 메서드를 사용하여 도구들을 가져옵니다.
        # 이 메서드는 내부적으로 load_mcp_tools를 호출하며 올바른 세션을 관리합니다.
        tools = await mcp_client.get_tools(server_name="default")

        global llm
        llm = llm.bind_tools(tools)
        logging.debug(f"Tools bound to LLM: {[tool.name for tool in tools]}")

        tool_node = ToolNode(tools=tools)
        logging.debug(f"Tools in ToolNode: {[tool.name for tool in tools]}")

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
            pool = AsyncConnectionPool(POSTGRES_CONN_STR, open=True)
            checkpointer = AsyncPostgresSaver(pool)
            
        else:
            raise RuntimeError("PostgreSQL 연결 정보가 없습니다. POSTGRES_CONNECTION_STRING 환경 변수를 확인하세요.")

        # 그래프 컴파일
        _agent_executor_instance = graph_builder.compile(checkpointer=checkpointer)
        logging.info("Agent executor initialized successfully.")
        return _agent_executor_instance
    except Exception as e:
        logging.error(f"Error during agent executor initialization: {e}", exc_info=True)
        raise

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

