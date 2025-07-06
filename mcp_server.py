from mcp_tools.mcp_instance import mcp
import mcp_tools.tools # 툴들이 mcp 인스턴스에 등록되도록 임포트

import logging
from config import settings

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) # 기본 로깅 설정
    logging.info(f"Starting FastMCP server on port {settings.MCP_SERVER_PORT}...")
    mcp.run(transport="streamable-http", port=settings.MCP_SERVER_PORT)