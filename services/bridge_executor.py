from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet, generate_faucet_wallet
from xrpl.models.transactions import Payment, Memo
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.transaction import autofill, sign, submit_and_wait
from web3 import Web3

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
EVM_RPC_URL = "https://rpc.testnet.xrplevm.org"
client = JsonRpcClient(JSON_RPC_URL)
w3 = Web3(Web3.HTTPProvider(EVM_RPC_URL))

ITS_CONTRACT_ADDRESS = "0x1a7580C2ef5D485E069B7cf1DF9f6478603024d3"
ITS_ABI = [...]  # Axelar ITS ABI
GATEWAY_ADDRESS = "rNrjh1KGZk2jBR3wPfAQnoidtFFYQKbQn2"

wallet = generate_faucet_wallet(client=client, debug=True) #테스트에 사용할 xrpl 테스트넷 지갑 생성 및 10 xrp faucet

def create_wallet_from_seed(seed: str):
    return Wallet.from_seed(seed=seed)

def generate_payload(evm_dest: str) -> str:
    """EVM 주소를 기반으로 66바이트 payload 생성 (34바이트 메타데이터는 Axelar가 채움)"""
    evm_addr = evm_dest[2:].lower() if evm_dest.startswith("0x") else evm_dest.lower()
    if len(evm_addr) != 40:
        raise ValueError("잘못된 EVM 주소 길이입니다")
    return "000000000000000000000000" + evm_addr + "0" * 68  # 12바이트 패딩 + 20바이트 EVM + 34바이트 플레이스홀더

def bridge_xrp_to_evm_direct(evm_dest: str, amount_drops: str, axelar_chain: str = "xrpl-evm", gas_fee_drops: str = "3000000"): # 테스트 편의상 seed받아서 지갑생성은 빼놨음
    """
    XRPL에서 XRPL EVM Sidechain으로 XRP 브릿지 (Squid Router 없이 Axelar 멀티시그 사용)
    """
    # wallet = create_wallet_from_seed(seed)
    evm_dest_raw = evm_dest[2:].lower() if evm_dest.startswith("0x") else evm_dest.lower()  # 0x 제거
    evm_dest_hex = evm_dest_raw.encode().hex()  # ASCII로 변환 후 HEX 인코딩
    payload = generate_payload(evm_dest)
    memos = [
        Memo(
            memo_data="interchain_transfer".encode().hex(),
            memo_type="type".encode().hex()
        ),
        Memo(
            memo_data=evm_dest_hex,  # ASCII HEX로 인코딩된 EVM 주소
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
        # Memo(
        #     memo_data=payload,  # 직접 HEX 사용
        #     memo_type="payload".encode().hex()
        # )
    ]
    tx = Payment(
        account=wallet.classic_address,
        amount=amount_drops,
        destination=GATEWAY_ADDRESS,
        memos=memos
    )
    tx = autofill(tx, client)
    signed_tx = sign(tx, wallet)
    result = submit_and_wait(signed_tx, client)
    print("Tx Hash:", result.result.get("hash"))
    print("Result:",result.result.get("meta", {}).get("TransactionResult"))
    
    return result.result


def bridge_iou_to_evm_direct(seed: str, evm_dest: str, currency: str, issuer: str, amount: str, axelar_chain: str = "xrpl-evm", gas_fee_drops: str = "3000000"):
    """
    XRPL에서 XRPL EVM Sidechain으로 IOU(예: RLUSD) 브릿지 (Squid Router 없이 Axelar 멀티시그 사용)
    """
    wallet = create_wallet_from_seed(seed)
    evm_dest_raw = evm_dest[2:].lower() if evm_dest.startswith("0x") else evm_dest.lower()  # 0x 제거
    evm_dest_hex = evm_dest_raw.encode().hex()  # ASCII로 변환 후 HEX 인코딩
    payload = generate_payload(evm_dest)
    memos = [
        Memo(
            memo_data="interchain_transfer".encode().hex(),
            memo_type="type".encode().hex()
        ),
        Memo(
            memo_data=evm_dest_hex,  # ASCII HEX로 인코딩된 EVM 주소
            memo_type="destination_address".encode().hex()
        ),
        Memo(
            memo_data=axelar_chain.encode().hex(),
            memo_type="destination_chain".encode().hex()
        ),
        Memo(
            memo_data=gas_fee_drops.encode().hex(),
            memo_type="gas_fee_amount".encode().hex()
        ),
        Memo(
            memo_data=payload,  # 직접 HEX 사용, encode().hex() 제거
            memo_type="payload".encode().hex()
        )
    ]
    tx = Payment(
        account=wallet.classic_address,
        amount=IssuedCurrencyAmount(
            currency=currency,
            issuer=issuer,
            value=amount
        ),
        destination=GATEWAY_ADDRESS,
        memos=memos
    )
    tx = autofill(tx, client)
    signed_tx = sign(tx, wallet)
    result = submit_and_wait(signed_tx, client)
    return result.result

def bridge_evm_to_xrpl(private_key: str, xrpl_dest: str, amount_wei: int, axelar_chain: str = "xrpl-evm-test-1", token_address: str = None):
    """
    XRPL EVM Sidechain에서 XRPL로 자산 브릿지
    """
    account = w3.eth.account.from_key(private_key)
    its_contract = w3.eth.contract(address=ITS_CONTRACT_ADDRESS, abi=ITS_ABI)
    token_address = token_address or "0x..."
    tx = its_contract.functions.interchainTransfer(
        axelar_chain,
        xrpl_dest,
        token_address,
        amount_wei
    ).build_transaction({
        "from": account.address,
        "gas": 200000,
        "gasPrice": w3.eth.gas_price,
        "nonce": w3.eth.get_transaction_count(account.address)
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

evm_destination = "0x79e88288ac11b0cdb53182ee1c43016caa82a1a0" 
response = bridge_xrp_to_evm_direct(evm_destination,"8000000") 
print("Response:",response)