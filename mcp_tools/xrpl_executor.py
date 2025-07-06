from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment, OfferCreate, AMMDeposit, TrustSet, DelegateSet
from xrpl.asyncio.transaction import autofill, sign, submit_and_wait, autofill_and_sign,submit
from xrpl.models.transactions import Memo, Transaction
from xrpl.account import get_balance
import xrpl.utils
from xrpl.models.amounts import IssuedCurrencyAmount
from config import settings
from mcp_tools.mcp_instance import mcp
from xrpl.models.requests.account_info import AccountInfo
from xrpl.models.transactions.delegate_set import Permission
import asyncio 



client = AsyncJsonRpcClient(settings.XRPL_JSON_RPC_URL)

@mcp.tool
async def create_wallet_from_seed(seed: str):
    """Create an XRPL wallet from a seed."""
    return Wallet.from_seed(seed=seed)


def text_to_hex(text):
    """Convert text to hex with proper padding"""
    if len(text) > 20:
        raise ValueError("Text must be 20 characters or less")
    hex_text = text.encode('ascii').hex().upper()
    return hex_text.ljust(40, '0')

@mcp.tool
async def send_payment(seed: str, destination: str, amount_drops: str):
    """Send a payment on XRPL from the wallet derived from seed to destination address."""
    wallet = Wallet.from_seed(seed)
    tx = Payment(
        account=wallet.classic_address,
        amount=amount_drops,
        destination=destination,
    )
    tx = await autofill(tx, client)
    signed_tx = sign(tx, wallet)
    result = await submit_and_wait(signed_tx, client)
    return result.result


async def delegate_send_payment(seed: str,org_account: str, destination: str, amount_drops: str):
    """Send a payment on XRPL from the wallet derived from seed to destination address."""
    wallet = Wallet.from_seed(seed)
    tx = Payment(
        account=org_account,
        amount=amount_drops,
        delegate = wallet.classic_address,
        destination=destination,
    )
    tx = await autofill(tx, client)
    signed_tx = sign(tx, wallet)
    result = await submit_and_wait(signed_tx, client)
    return result.result


@mcp.tool
async def get_account_balance(address: str):
    """Get the XRP balance of an account address."""
    return await get_balance(address, client)

# @mcp.tool
# def create_offer(seed: str, taker_gets: str, taker_pays: dict, flags: int = None):
#     """Create an offer on XRPL DEX."""
#     wallet = create_wallet_from_seed(seed)
#     tx = OfferCreate(
#         account=wallet.classic_address,
#         taker_gets=taker_gets,
#         taker_pays=taker_pays,
#         flags=flags,
#     )
#     tx = autofill(tx, client)
#     signed_tx = sign(tx, wallet)
#     result = submit_and_wait(signed_tx, client)
#     return result.result


async def create_trustline(seed: str, issuer_address:str, currency_code:str, limit_amount="1000000000"): #trustline 설정함수
    """
    Creates a trustline for a specific currency on XRPL testnet
    
    Parameters:
    seed: The seed of the wallet to create the trustline from
    issuer_address: The address of the token issuer
    currency_code: The currency code (e.g., 'USD')
    limit_amount: The trust line limit amount (default: 1000000000)
    """
    wallet = Wallet.from_seed(seed)
    
    
    try:
        currency_hex = text_to_hex(currency_code) #입력받은 토큰명을 hex값으로 치환 
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Prepare the trust set transaction
    # trustline 설정 트랜잭션
    trust_set_tx = TrustSet( 
        account=wallet.classic_address,
        limit_amount={
            "currency": currency_hex,
            "issuer": issuer_address,
            "value": str(limit_amount)
        }
    )
    
    print("\n=== Creating Trustline ===")
    print(f"Account: {wallet.classic_address}")
    print(f"Currency (original): {currency_code}")
    print(f"Currency (hex): {currency_hex}")
    print(f"Issuer: {issuer_address}")
    print(f"Limit: {limit_amount}")
    
    try:
        # Submit and wait for validation
        response = await submit_and_wait(trust_set_tx, client, wallet)
        
        # Check the result
        if response.is_successful():
            print("\nTrustline created successfully!")
            print(f"Transaction hash: {response.result['hash']}")
        else:
            print("\nFailed to create trustline")
            print(f"Error: {response.result.get('engine_result_message')}")
            
    except Exception as e:
        print(f"\nError creating trustline: {str(e)}")
    
    print("==============================\n")


# xrp 단방향 예치 함수, RLUSD와 페어인 풀에 예치
async def amm_deposit_single_xrp(seed, xrp_amount="0.5"):
    """
    Deposits only RLUSD into an existing AMM
    """
    # Define the network client
    client = AsyncJsonRpcClient(settings.XRPL_JSON_RPC_URL)
    
    # Create wallet from seed
    wallet = Wallet.from_seed(seed)
    
    # RLUSD constants
    currency_hex = "524C555344000000000000000000000000000000"  # Hex for "RLUSD"
    issuer = "rQhWct2fv4Vc4KRjRgMrxa8xPN9Zx9iLKV"
    
    # Get account sequence
    account_info = await client.request(AccountInfo(
        account=wallet.classic_address,
        ledger_index="validated"
    ))
    sequence = account_info.result['account_data']['Sequence']  
    
    # Prepare AMM deposit transaction
    tx_dict = {
        "transaction_type": "AMMDeposit",
        "account": wallet.classic_address,
        "amount":str(int(float(xrp_amount) * 1_000_000)),
        "asset": {
            "currency": "XRP",
            
        },
        "asset2": {
            "currency": currency_hex,
            "issuer": issuer
        },
        "flags": 524288,  # tfSingleAsset -> full doc https://xrpl.org/docs/references/protocol/transactions/types/ammdeposit
        "fee": "10",
        "sequence": sequence
    }
    
    # Create Transaction object
    deposit_tx = Transaction.from_dict(tx_dict)
    
    print("\n=== Depositing RLUSD to AMM ===")
    print(f"Account: {wallet.classic_address}")
    print(f"XRP Amount: {xrp_amount} XRP")
    
    try:
        # Sign transaction
        deposit_tx = await autofill(deposit_tx, client)
        signed_tx =sign(deposit_tx, wallet)
        
        # Submit transaction
        response = await submit_and_wait(signed_tx, client)
        
        # Check the result
        if "engine_result" in response.result and response.result["engine_result"] == "tesSUCCESS":
            print("\nDeposit successful!")
            print(f"Transaction hash: {response.result.get('tx_json', {}).get('hash')}")
            return response
        else:
            print("\nDeposit failed")
            print(f"Error: {response.result}")
            return response
            
    except Exception as e:
        print(f"\nError making deposit: {str(e)}")
        raise e

async def delegate_permission(seed,  delegated_account, permission:str = "Payment"):
    """delegating permission to delegated_account."""
    wallet = Wallet.from_seed(seed)
    
    delegate_tx = DelegateSet(
    account=wallet.classic_address,
    authorize=delegated_account,
    permissions=[
        Permission(permission_value= permission)
    ]
)
    
    
    try:
        # Sign transaction
        
        delegate_tx = await autofill(delegate_tx, client)
        signed_tx =sign(delegate_tx, wallet)
        
        # Submit transaction
        response = await submit_and_wait(signed_tx, client)
        
        # Check the result
        if response.result.get("meta", {}).get("TransactionResult") == "tesSUCCESS":
            print("\nDelegate successful!")
            print(f"Transaction hash: {response.result.get('hash')}")
        else:
            print("\nDelegate failed")
            print(f"Error: {response.result}")

    except Exception as e:
        print(f"\nError making delegate: {str(e)}")
        raise e


