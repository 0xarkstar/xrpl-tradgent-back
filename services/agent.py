import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from services import bridge_executor, xrpl_executor
import requests
import json

# 환경 변수 로드
load_dotenv()
llm = ChatOpenAI(model="gpt-4", api_key=os.getenv("OPENAI_API_KEY"))

# MCP 서버 URL (lgcarrier/xrpl-mcp-server)
MCP_SERVER_URL = "http://localhost:8001"  # MCP 서버 실행 URL

# LangChain 프롬프트 템플릿
bridge_prompt = PromptTemplate(
    input_variables=["query", "account_info", "amm_info"],
    template="""
    You are an AI assistant for XRPL DeFi operations. Based on the user query and provided data, determine the appropriate action (e.g., bridge XRP or IOU to EVM, check balance, etc.).
    
    User Query: {query}
    Account Info: {account_info}
    AMM Info: {amm_info}
    
    Respond with a JSON object containing:
    - action: The action to take (e.g., \"bridge_xrp_to_evm\", \"bridge_iou_to_evm\", \"check_balance\")
    - parameters: Parameters required for the action (e.g., sender_seed, evm_dest, amount_drops, currency, issuer, amount)
    """
)

# MCP 서버와 통신
def get_mcp_account_info(address: str):
    """MCP 서버에서 계정 정보 조회"""
    try:
        response = requests.get(f"{MCP_SERVER_URL}/account/{address}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"MCP server error: {str(e)}"}

def get_mcp_amm_info(asset1: dict, asset2: dict):
    """MCP 서버에서 AMM 풀 정보 조회"""
    try:
        payload = {"asset1": asset1, "asset2": asset2}
        response = requests.post(f"{MCP_SERVER_URL}/amm/info", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"MCP server error: {str(e)}"}

async def run_bridge_agent(
    query: str,
    sender_seed: str = None,
    evm_dest: str = None,
    amount_drops: str = None,
    currency: str = None,
    issuer: str = None,
    amount: str = None,
    private_key: str = None,
    xrpl_dest: str = None,
    amount_wei: int = None,
    axelar_chain: str = "xrpl-evm-sidechain"
):
    """
    LangChain과 MCP 서버를 사용하여 브릿지 및 XRPL 작업 처리
    """
    # MCP 서버에서 계정 정보 조회
    wallet = xrpl_executor.create_wallet_from_seed(sender_seed) if sender_seed else None
    account_info = get_mcp_account_info(wallet.classic_address) if wallet else {"error": "No sender_seed provided"}
    
    # AMM 풀 정보 조회 (RLUSD 또는 XRP 관련)
    amm_info = get_mcp_amm_info(
        {"currency": "XRP"},
        {"currency": currency or "XRP", "issuer": issuer}
    ) if currency else {"info": "No AMM query"}
    
    # LangChain으로 쿼리 처리
    chain = LLMChain(llm=llm, prompt=bridge_prompt)
    response = await chain.arun(
        query=query,
        account_info=json.dumps(account_info),
        amm_info=json.dumps(amm_info)
    )
    
    # LangChain 응답 파싱
    try:
        action_data = json.loads(response)
        action = action_data.get("action")
        params = action_data.get("parameters", {})
    except json.JSONDecodeError:
        return {"error": "Invalid LangChain response"}
    
    # 액션 실행
    if action == "bridge_xrp_to_evm":
        # 비동기 함수이므로 await 필요
        result = await bridge_executor.bridge_xrp_to_evm(
            evm_dest or params.get("evm_dest"),
            amount_drops or params.get("amount_drops"),
            axelar_chain or params.get("axelar_chain", "xrpl-evm")
        )
        return {"type": "xrp_to_evm", "result": result}
    elif action == "bridge_iou_to_evm":
        # 동기 함수, direct 버전 사용
        result = bridge_executor.bridge_iou_to_evm_direct(
            sender_seed or params.get("sender_seed"),
            evm_dest or params.get("evm_dest"),
            currency or params.get("currency"),
            issuer or params.get("issuer"),
            amount or params.get("amount"),
            axelar_chain or params.get("axelar_chain", "xrpl-evm")
        )
        return {"type": "iou_to_evm", "result": result}
    elif action == "bridge_evm_to_xrpl":
        # 동기 함수
        result = bridge_executor.bridge_evm_to_xrpl(
            private_key or params.get("private_key"),
            xrpl_dest or params.get("xrpl_dest"),
            amount_wei or params.get("amount_wei"),
            axelar_chain or params.get("axelar_chain", "xrpl-evm"),
            params.get("token_address")
        )
        return {"type": "evm_to_xrpl", "result": result}
    elif action == "check_balance":
        balance = xrpl_executor.get_account_balance(params.get("address"))
        return {"type": "check_balance", "result": balance}
    else:
        return {"error": f"Unknown action: {action}"}