# fastMCP 툴/프롬프트 정의
from fastmcp import Context
from mcp_tools.mcp_instance import mcp
from db.queries import get_user_by_xrpl_address, get_user_by_evm_address

# Import functions from executor files
from mcp_tools.bridge_executor import validate_evm_address as bridge_validate_evm_address
from mcp_tools.bridge_executor import bridge_xrp_to_evm as bridge_xrp_to_evm_func
from mcp_tools.evm_executor import get_eth_balance as evm_get_eth_balance
from mcp_tools.evm_executor import send_native_token as evm_send_native_token
from mcp_tools.evm_executor import dummy_uniswap_add_liquidity as evm_dummy_uniswap_add_liquidity
from mcp_tools.xrpl_executor import send_payment as xrpl_send_payment
from mcp_tools.xrpl_executor import get_account_balance as xrpl_get_account_balance
from mcp_tools.xrpl_executor import create_trustline as xrpl_create_trustline
from mcp_tools.xrpl_executor import amm_deposit_single_xrp as xrpl_amm_deposit_single_xrp
from mcp_tools.xrpl_executor import delegate_permission as xrpl_delegate_permission


@mcp.tool
async def get_user_profile(wallet_address: str, ctx: Context):
    """
    사용자의 지갑 주소를 기반으로 사용자 프로필 정보를 조회합니다.
    """
    user_data = await get_user_by_xrpl_address(wallet_address)
    if not user_data:
        user_data = await get_user_by_evm_address(wallet_address)

    if user_data:
        await ctx.info(f"사용자 프로필 조회 성공: {user_data}")
        return {"user_profile": user_data}
    else:
        await ctx.info(f"사용자 프로필을 찾을 수 없습니다: {wallet_address}")
        return {"user_profile": None}


# --- Wrapped XRPL Executor Tools ---
@mcp.tool
async def send_xrpl_payment(seed: str, destination: str, amount_drops: str, ctx: Context):
    """XRPL에서 지정된 시드로부터 목적지 주소로 결제를 보냅니다.
    seed: 지갑 시드.
    destination: 목적지 주소.
    amount_drops: 보낼 금액 (drops 단위).
    """
    await ctx.info(f"XRPL 결제 전송: {amount_drops} drops to {destination}")
    result = await xrpl_send_payment(seed=seed, destination=destination, amount_drops=amount_drops)
    return {"tx_result": result}

@mcp.tool
async def get_xrpl_account_balance(address: str, ctx: Context):
    """XRPL 계정의 XRP 잔액을 조회합니다.
    address: 계정 주소.
    """
    await ctx.info(f"XRPL 계정 잔액 조회: {address}")
    balance = await xrpl_get_account_balance(address=address)
    return {"balance": balance}

@mcp.tool
async def create_xrpl_trustline(seed: str, issuer_address: str, currency_code: str, ctx: Context, limit_amount: str = "1000000000"):
    """
    XRPL에서 특정 통화에 대한 트러스트라인을 생성합니다.
    seed: 트러스트라인을 생성할 지갑의 시드.
    issuer_address: 토큰 발행자의 주소.
    currency_code: 통화 코드 (예: 'USD').
    limit_amount: 트러스트라인 한도 금액.
    """
    await ctx.info(f"XRPL 트러스트라인 생성: {currency_code} from {issuer_address} with limit {limit_amount}")
    result = await xrpl_create_trustline(seed=seed, issuer_address=issuer_address, currency_code=currency_code, limit_amount=limit_amount)
    return {"result": result}

@mcp.tool
async def amm_deposit_single_xrp(seed: str, ctx: Context, xrp_amount: str = "0.5"):
    """
    단일 자산(XRP)을 AMM 풀에 예치합니다.
    seed: 예치할 지갑의 시드.
    xrp_amount: 예치할 XRP 금액.
    """
    await ctx.info(f"AMM에 XRP 예치: {xrp_amount} XRP")
    result = await xrpl_amm_deposit_single_xrp(seed=seed, xrp_amount=xrp_amount)
    return {"result": result}

@mcp.tool
async def delegate_xrpl_permission(seed: str, delegated_account: str, ctx: Context, permission: str = "Payment"):
    """
    특정 계정에 권한을 위임합니다. (예: 'Payment', 'OfferCreate')
    seed: 권한을 부여하는 지갑의 시드.
    delegated_account: 권한을 위임받는 계정.
    permission: 위임할 권한의 종류.
    """
    await ctx.info(f"XRPL 권한 위임 실행: {permission} from {seed} to {delegated_account}")
    result = await xrpl_delegate_permission(seed=seed, delegated_account=delegated_account, permission=permission)
    return {"result": result}


# --- Wrapped Bridge Executor Tools ---
@mcp.tool
def validate_evm_address(evm_dest: str, ctx: Context):
    """EVM 주소를 유효성 검사하고 정리합니다.
    evm_dest: 유효성 검사할 EVM 주소.
    """
    ctx.info(f"EVM 주소 유효성 검사: {evm_dest}")
    result = bridge_validate_evm_address(evm_dest=evm_dest)
    return {"validated_address": result}

@mcp.tool
async def bridge_xrp_to_evm(seed: str, evm_dest: str, amount_drops: str, ctx: Context, axelar_chain: str = "xrpl-evm", gas_fee_drops: str = "3000000"):
    """Axelar를 사용하여 XRPL에서 EVM 체인으로 XRP를 브릿지합니다.
    seed: 지갑 시드.
    evm_dest: EVM 목적지 주소.
    amount_drops: 보낼 금액 (drops 단위).
    axelar_chain: Axelar 체인 이름.
    gas_fee_drops: 가스 요금 (drops 단위).
    """
    await ctx.info(f"XRPL에서 EVM으로 XRP 브릿지: {amount_drops} drops to {evm_dest} on {axelar_chain}")
    result = await bridge_xrp_to_evm_func(seed=seed, evm_dest=evm_dest, amount_drops=amount_drops, axelar_chain=axelar_chain, gas_fee_drops=gas_fee_drops)
    return {"tx_result": result}


# --- Wrapped EVM Executor Tools ---
@mcp.tool
def get_eth_balance(address: str, ctx: Context):
    """EVM 계정의 ETH 잔액(wei 단위)을 조회합니다.
    address: 계정 주소.
    """
    ctx.info(f"EVM ETH 잔액 조회: {address}")
    balance = evm_get_eth_balance(address=address)
    return {"balance_wei": balance}

@mcp.tool
def send_native_token(private_key: str, destination: str, amount_wei: int, ctx: Context):
    """네이티브 EVM 토큰(ETH)을 목적지 주소로 보냅니다.
    private_key: 개인 키.
    destination: 목적지 주소.
    amount_wei: 보낼 금액 (wei 단위).
    """
    ctx.info(f"네이티브 토큰 전송: {amount_wei} wei to {destination}")
    receipt = evm_send_native_token(private_key=private_key, destination=destination, amount_wei=amount_wei)
    return {"tx_receipt": receipt}

@mcp.tool
def dummy_uniswap_add_liquidity(ctx: Context):
    """Uniswap 유동성 추가를 위한 더미 함수 (구현 예정)."""
    raise NotImplementedError("Dummy Uniswap liquidity addition is not yet implemented.")


@mcp.tool
async def deposit_to_vault(wallet_address: str, amount: float, ctx: Context):
    raise NotImplementedError("Deposit to vault is not yet implemented.")

@mcp.tool
async def set_investment_goal(wallet_address: str, goal: str, ctx: Context):
    raise NotImplementedError("Setting investment goal is not yet implemented.")

@mcp.tool
async def ai_strategy_recommendation(wallet_address: str, risk_profile: str, ctx: Context):
    raise NotImplementedError("AI strategy recommendation is not yet implemented.")

@mcp.tool
async def approve_strategy(wallet_address: str, strategy: str, ctx: Context):
    raise NotImplementedError("Strategy approval is not yet implemented.")


# FastMCP 프롬프트 정의
@mcp.prompt
def strategy_explanation_prompt(strategy: str) -> str:
    return f"Please explain the following DeFi strategy in simple terms: {strategy}"
