from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain.tools import tool

@tool
def check_balance(address: str) -> str:
    """사용자의 XRP 또는 EVM 지갑의 잔액을 조회합니다. 입력은 지갑 주소입니다."""
    return f"{address}의 XRP 잔액은 약 235.78 XRP입니다."

tools = [check_balance]

llm = ChatOpenAI(model="gpt-4", temperature=0.2)
agent_executor = create_react_agent(llm, tools)
