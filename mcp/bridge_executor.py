from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment, Memo
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.asyncio.transaction import autofill, sign, submit_and_wait
from web3 import Web3
from typing import Optional, Dict, Any
import logging
import asyncio
from config import settings

from mcp_tools.mcp_instance import mcp

client = AsyncJsonRpcClient(settings.XRPL_JSON_RPC_URL)
w3 = Web3(Web3.HTTPProvider(settings.EVM_RPC_URL))

ITS_CONTRACT_ADDRESS = "0x1a7580C2ef5D485E069B7cf1DF9f6478603024d3"

@mcp.tool
def create_wallet_from_seed(seed: str) -> Wallet:
    """Create an XRPL wallet from a seed."""
    return Wallet.from_seed(seed=seed)

@mcp.tool
def validate_evm_address(evm_dest: str) -> str:
    """Validate and clean an EVM address for bridging."""
    if not evm_dest.startswith("0x") or len(evm_dest) != 42:
        raise ValueError("Invalid EVM address")
    return evm_dest[2:].upper()

@mcp.tool
def build_memos(
    evm_dest: str,
    axelar_chain: str = "xrpl-evm",
    gas_fee_drops: str = "3000000",
    tx_type: str = "interchain_transfer"
) -> list:
    """Build memos for cross-chain transfer."""
    evm_dest_clean = validate_evm_address(evm_dest)
    evm_dest_ascii_hex = evm_dest_clean.encode('ascii').hex()
    memos = [
        Memo(
            memo_data=tx_type.encode().hex(),
            memo_type="type".encode().hex()
        ),
        Memo(
            memo_data=evm_dest_ascii_hex,
            memo_type="destination_address".encode().hex()
        ),
        Memo(
            memo_data=axelar_chain.encode().hex(),
            memo_type="destination_chain".encode().hex()
        ),
        Memo(
            memo_data=gas_fee_drops.encode().hex(),
            memo_type="gas_fee_amount".encode().hex()
        )
    ]
    return memos

@mcp.tool
async def bridge_xrp_to_evm(seed: str, evm_dest: str, amount_drops: str, axelar_chain: str = "xrpl-evm", gas_fee_drops: str = "3000000"):
    """Bridge XRP from XRPL to EVM chain using Axelar."""
    wallet = create_wallet_from_seed(seed)
    memos = build_memos(evm_dest, axelar_chain, gas_fee_drops)
    tx = Payment(
        account=wallet.classic_address,
        amount=amount_drops,
        destination=ITS_CONTRACT_ADDRESS,
        memos=memos
    )
    tx = await autofill(tx, client)
    signed_tx = await sign(tx, wallet)
    result = await submit_and_wait(signed_tx, client)
    return result.result
