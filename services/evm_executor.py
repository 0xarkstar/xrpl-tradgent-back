from web3 import Web3

EVM_RPC_URL = "https://rpc.testnet.xrplevm.org"
w3 = Web3(Web3.HTTPProvider(EVM_RPC_URL))

def get_eth_balance(address: str):
    """EVM 계정 잔액 조회 (wei 단위)"""
    return w3.eth.get_balance(address)

def send_native_token(private_key: str, destination: str, amount_wei: int):
    """EVM 네이티브 토큰 전송"""
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
    """더미 유동성 추가 함수 (구현 필요)"""
    return {"status": "Dummy liquidity addition successful"}