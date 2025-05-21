from web3 import Web3
import os

XRPL_EVM_RPC = os.getenv("XRPL_EVM_RPC", "https://evm.devnet.xrpl.org")

w3 = Web3(Web3.HTTPProvider(XRPL_EVM_RPC))

def get_eth_balance(address: str):
    return w3.eth.get_balance(address)

def send_native_token(private_key: str, to: str, amount_wei: int):
    account = w3.eth.account.from_key(private_key)
    tx = {
        "to": to,
        "value": amount_wei,
        "gas": 21000,
        "gasPrice": w3.eth.gas_price,
        "nonce": w3.eth.get_transaction_count(account.address),
    }
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)
