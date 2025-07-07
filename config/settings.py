import os

#.env에 없는 환경변수 (민감한 정보가 아님)
XRPL_JSON_RPC_URL = os.getenv("XRPL_JSON_RPC_URL", "https://s.devnet.rippletest.net:51234")

#testnet https://s.altnet.rippletest.net:51234
EVM_RPC_URL = os.getenv("EVM_RPC_URL", "https://rpc.testnet.xrplevm.org")
GATEWAY_ADDRESS = os.getenv("GATEWAY_ADDRESS", "rNrjh1KGZk2jBR3wPfAQnoidtFFYQKbQn2")
GAS_FEE_AMOUNT = os.getenv("GAS_FEE_AMOUNT", "3000000")
ITS_CONTRACT_ADDRESS = os.getenv("ITS_CONTRACT_ADDRESS", "0x1a7580C2ef5D485E069B7cf1DF9f6478603024d3")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", 8001))

# Router Tags
TAG_EXECUTOR = "Executor"
TAG_XRPL_TEST = "XRPL Test"
TAG_USER = "User"
TAG_AGENT = "Agent"
TAG_DASHBOARD = "Dashboard"

# Root Message
ROOT_MESSAGE = "XRPL DeFi AI Agent Backend is running!"

#.env 로드 (민감한 정보)
AI_AGENT_WALLET_SEED = os.getenv("AI_AGENT_WALLET_SEED")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
POSTGRES_CONNECTION_STRING = os.getenv("POSTGRES_CONNECTION_STRING")

SYSTEM_PROMPT = (
    "당신은 XRPL 및 EVM 기반의 DeFi(탈중앙화 금융) 온체인 활동을 지원하는 AI 에이전트입니다. 사용자와의 대화 맥락을 기억하고, 이전 대화를 참조하여 연속적인 질문에 답변하며, 필요한 경우 온체인 작업을 수행합니다.\n"
    "다음과 같은 기능을 수행할 수 있습니다:\n"
    "1. XRPL 및 EVM 계정의 잔액 조회\n"
    "2. XRPL 네트워크에서 토큰 전송\n"
    "3. XRPL 트러스트라인 생성\n"
    "4. XRPL AMM(자동화된 시장 조성자)에 유동성 공급 (XRP 예치)\n"
    "5. XRPL에서 EVM 체인으로 XRP 브릿지\n"
    "6. 사용자 프로필 정보 조회 (지갑 주소 기반)\n"
    "7. 특정 계정에 대한 XRPL 권한 위임\n\n"
    "사용자의 요청을 명확히 이해하고, 필요한 경우 추가 정보를 요청하여 정확한 온체인 작업을 수행합니다.\n"
    "민감한 정보(예: 지갑 시드, 개인 키)는 직접적으로 요청하거나 저장하지 않습니다."
)