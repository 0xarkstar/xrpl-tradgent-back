from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment, OfferCreate, AMMDeposit, TrustSet, DelegateSet
from xrpl.asyncio.transaction import autofill, autofill_and_sign, submit
from xrpl.models.transactions import Memo, Transaction

import xrpl.utils
from xrpl.models.amounts import IssuedCurrencyAmount
from config import settings

from xrpl.models.requests.account_info import AccountInfo
from xrpl.models.transactions.delegate_set import Permission
import asyncio 
import traceback

RLUSD_CURRENCY_HEX = "524C555344000000000000000000000000000000"
RLUSD_ISSUER = "rQhWct2fv4Vc4KRjRgMrxa8xPN9Zx9iLKV"

import logging

client = AsyncJsonRpcClient(settings.XRPL_JSON_RPC_URL)


def create_wallet_from_seed(seed: str):
    """Create an XRPL wallet from a seed."""
    return Wallet.from_seed(seed=seed)


MAX_TEXT_LENGTH = 20

def text_to_hex(text):
    """Convert text to hex with proper padding"""
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError("Text must be 20 characters or less")
    hex_text = text.encode('ascii').hex().upper()
    return hex_text.ljust(40, '0')

async def send_payment(seed: str, destination: str, amount_drops: str):
    """Send a payment on XRPL from the wallet derived from seed to destination address."""
    wallet = Wallet.from_seed(seed)
    tx = Payment(
        account=wallet.classic_address,
        amount=amount_drops,
        destination=destination,
    )
    signed_tx = await autofill_and_sign(tx, client, wallet)
    result = await submit(signed_tx, client)
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
    signed_tx = await autofill_and_sign(tx, client, wallet)
    result = await submit(signed_tx, client)
    return result.result


async def get_account_balance(address: str):
    """Get the XRP balance of an account address."""
    try:
        req = AccountInfo(
            account=address,
            ledger_index="validated",
        )
        account_info = await client.request(req)
        balance = account_info.result["account_data"]["Balance"]
        logging.debug(f"Successfully retrieved balance for {address}: {balance}")
        return balance
    except Exception as e:
        logging.error(f"Failed to get balance for {address}: {e}")
        traceback.print_exc()
        return {"error": str(e)}




async def create_trustline(seed: str, issuer_address:str, currency_code:str, limit_amount="1000000000"):
    """
    Creates a trustline for a specific currency on the XRPL. This is required before you can hold a token.
    seed: The seed of the wallet to create the trustline from.
    issuer_address: The address of the token issuer.
    currency_code: The currency code (e.g., 'USD').
    limit_amount: The trust line limit amount.
    """
    wallet = Wallet.from_seed(seed)
    
    
    try:
        currency_hex = text_to_hex(currency_code) #입력받은 토큰명을 hex값으로 치환 
    except ValueError as e:
        logging.error(f"Error: {e}")
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
    
    logging.info("\n=== Creating Trustline ===")
    logging.info(f"Account: {wallet.classic_address}")
    logging.info(f"Currency (original): {currency_code}")
    logging.info(f"Currency (hex): {currency_hex}")
    logging.info(f"Issuer: {issuer_address}")
    logging.info(f"Limit: {limit_amount}")
    
    try:
        # Submit and wait for validation
        signed_tx = await autofill_and_sign(trust_set_tx, client, wallet)
        response = await submit(signed_tx, client)
        
        # Check the result
        if response.is_successful():
            logging.info("\nTrustline created successfully!")
            logging.info(f"Transaction hash: {response.result['hash']}")
            return response.result
        else:
            logging.error("\nFailed to create trustline")
            logging.error(f"Error: {response.result.get('engine_result_message')}")
            return {"error": response.result.get('engine_result_message')}
            
    except Exception as e:
        logging.error(f"\nError creating trustline: {str(e)}")
        return {"error": str(e)}
    

async def amm_deposit_single_xrp(seed: str, xrp_amount: str = "0.5"):
    """
    Deposits a single asset (XRP) into an AMM pool. This is useful for providing liquidity.
    seed: The seed of the wallet to deposit from.
    xrp_amount: The amount of XRP to deposit.
    """
    
    
    # Create wallet from seed
    wallet = Wallet.from_seed(seed)
    
    # RLUSD constants
    currency_hex = RLUSD_CURRENCY_HEX
    issuer = RLUSD_ISSUER
    
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
    
    logging.info("\n=== Depositing RLUSD to AMM ===")
    logging.info(f"Account: {wallet.classic_address}")
    logging.info(f"XRP Amount: {xrp_amount} XRP")
    
    try:
        # Sign transaction
        signed_tx = await autofill_and_sign(deposit_tx, client, wallet)
        response = await submit(signed_tx, client)
        
        # Check the result
        if "engine_result" in response.result and response.result["engine_result"] == "tesSUCCESS":
            logging.info("\nDeposit successful!")
            logging.info(f"Transaction hash: {response.result.get('tx_json', {}).get('hash')}")
            return response.result
        else:
            logging.error("\nDeposit failed")
            logging.error(f"Error: {response.result}")
            return {"error": response.result}
            
    except Exception as e:
        logging.error(f"\nError making deposit: {str(e)}")
        raise e

async def delegate_permission(seed: str,  delegated_account: str, permission: str = "Payment"):
    """
    Delegates a specific permission (e.g., 'Payment', 'OfferCreate') to another account.
    seed: The seed of the wallet granting the permission.
    delegated_account: The account to which the permission is delegated.
    permission: The permission to delegate.
    """
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
        
        signed_tx = await autofill_and_sign(delegate_tx, client, wallet)
        response = await submit(signed_tx, client)
        
        # Check the result
        if response.result.get("meta", {}).get("TransactionResult") == "tesSUCCESS":
            logging.info("\nDelegate successful!")
            logging.info(f"Transaction hash: {response.result.get('hash')}")
            return response.result
        else:
            print("\nDelegate failed")
            print(f"Error: {response.result}")
            return {"error": response.result}

    except Exception as e:
        print(f"\nError making delegate: {str(e)}")
        raise e






