from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment, OfferCreate, AMMDeposit, TrustSet
from xrpl.transaction import autofill, sign, submit_and_wait, autofill_and_sign,submit
from xrpl.models.transactions import Memo, Transaction
from xrpl.account import get_balance
import xrpl.utils
from xrpl.models.amounts import IssuedCurrencyAmount
from config import settings
from mcp_tools.mcp_instance import mcp
from xrpl.models.requests.account_info import AccountInfo
import asyncio 

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"

client = AsyncJsonRpcClient(settings.XRPL_JSON_RPC_URL)

@mcp.tool
def create_wallet_from_seed(seed: str):
    """Create an XRPL wallet from a seed."""
    return Wallet.from_seed(seed=seed)


def text_to_hex(text):
    """Convert text to hex with proper padding"""
    if len(text) > 20:
        raise ValueError("Text must be 20 characters or less")
    hex_text = text.encode('ascii').hex().upper()
    return hex_text.ljust(40, '0')

@mcp.tool
def send_payment(seed: str, destination: str, amount_drops: str):
    """Send a payment on XRPL from the wallet derived from seed to destination address."""
    wallet = create_wallet_from_seed(seed)
    tx = Payment(
        account=wallet.classic_address,
        amount=amount_drops,
        destination=destination,
    )
    tx = autofill(tx, client)
    signed_tx = sign(tx, wallet)
    result = submit_and_wait(signed_tx, client)
    return result.result

@mcp.tool
def get_account_balance(address: str):
    """Get the XRP balance of an account address."""
    return get_balance(address, client)

@mcp.tool
def create_offer(seed: str, taker_gets: str, taker_pays: dict, flags: int = None):
    """Create an offer on XRPL DEX."""
    wallet = create_wallet_from_seed(seed)
    tx = OfferCreate(
        account=wallet.classic_address,
        taker_gets=taker_gets,
        taker_pays=taker_pays,
        flags=flags,
    )
    tx = autofill(tx, client)
    signed_tx = sign(tx, wallet)
    result = submit_and_wait(signed_tx, client)
    return result.result


async def create_trustline(seed: str, issuer_address:str, currency_code:str, limit_amount="1000000000"):
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
        currency_hex = text_to_hex(currency_code)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Prepare the trust set transaction
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
        response = submit_and_wait(trust_set_tx, client, wallet)
        
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

# if __name__ == "__main__":
#     # Example usage - replace with your values
#     seed = "sEdVZUmeY8oLphH6WPdUBC82Fh8QpTN"  # Replace with your wallet seed
#     issuer_address = "rQhWct2fv4Vc4KRjRgMrxa8xPN9Zx9iLKV"
#     currency_code = "RLUSD"

#     create_trustline(seed, issuer_address, currency_code)







# def deposit_to_amm(seed: str, asset1: dict, asset2: dict, amount1: str = None, amount2: str = None, flags: int = None):
#     wallet = create_wallet_from_seed(seed)
#     tx_fields = {
#         "account": wallet.classic_address,
#         "asset": asset1,
#         "asset2": asset2,
#     }
#     if amount1:
#         if asset1.get("currency") == "XRP":
#             tx_fields["amount"] = amount1
#         else:
#             tx_fields["amount"] = IssuedCurrencyAmount(
#                 currency=asset1["currency"],
#                 issuer=asset1["issuer"],
#                 value=amount1
#             )
#     if amount2:
#         if asset2.get("currency") == "XRP":
#             tx_fields["amount2"] = amount2
#         else:
#             tx_fields["amount2"] = IssuedCurrencyAmount(
#                 currency=asset2["currency"],
#                 issuer=asset2["issuer"],
#                 value=amount2
#             )
#     if flags:
#         tx_fields["flags"] = flags
#     tx = AMMDeposit(**tx_fields)
#     tx = autofill(tx, client)
#     signed_tx = sign(tx, wallet)
#     result = submit_and_wait(signed_tx, client)
#     return result.result


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
