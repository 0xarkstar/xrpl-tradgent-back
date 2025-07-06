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

SYSTEM_PROMPT = (
    "당신은 온체인 활동을 도와주는 AI 에이전트 입니다. "
)

# Router Tags
TAG_EXECUTOR = "Executor"
TAG_XRPL_TEST = "XRPL Test"
TAG_USER = "User"
TAG_AGENT = "Agent"
TAG_DASHBOARD = "Dashboard"

# Root Message
ROOT_MESSAGE = "XRPL DeFi AI Agent Backend is running!"

#.env 로드 (민감한 정보)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
POSTGRES_CONNECTION_STRING = os.getenv("POSTGRES_CONNECTION_STRING")