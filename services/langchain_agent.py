from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain.tools import Tool

# 임시 예시 도구 (나중에 실제 체인 연동으로 대체)
def dummy_balance_tool(input: str) -> str:
    return f"{input}의 XRP 잔액은 약 235.78 XRP입니다."

tools = [
    Tool(
        name="CheckBalance",
        func=dummy_balance_tool,
        description="사용자의 XRP 또는 EVM 지갑의 잔액을 조회합니다. 입력은 지갑 주소입니다."
    )
]

llm = ChatOpenAI(model="gpt-4", temperature=0.2)

agent_executor = create_react_agent(llm, tools)
