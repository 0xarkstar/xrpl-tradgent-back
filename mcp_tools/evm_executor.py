from web3 import Web3
from config import settings


w3 = Web3(Web3.HTTPProvider(settings.EVM_RPC_URL))

def get_eth_balance(address: str):
    """Get the ETH balance (in wei) of an EVM account."""
    return w3.eth.get_balance(address)

def send_native_token(private_key: str, destination: str, amount_wei: int):
    """Send native EVM token (ETH) to a destination address."""
    account = w3.eth.account.from_key(private_key)
    tx = {
        "to": destination,
        "value": amount_wei,
        "gas": 21000,
        "gasPrice": w3.eth.gas_price,
        "nonce": w3.eth.get_transaction_count(account.address)
    }
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def dummy_uniswap_add_liquidity():
    """Dummy function for Uniswap liquidity addition (to be implemented)."""
    return {"status": "Dummy liquidity addition successful"}
