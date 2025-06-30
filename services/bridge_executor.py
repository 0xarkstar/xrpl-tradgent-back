from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.wallet import Wallet, generate_faucet_wallet
from xrpl.models.transactions import Payment, Memo
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.asyncio.transaction import autofill, sign, submit_and_wait
from web3 import Web3
from typing import Optional, Dict, Any
import logging
import asyncio

# Testnet 설정
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
EVM_RPC_URL = "https://rpc.testnet.xrplevm.org"
GATEWAY_ADDRESS = "rNrjh1KGZk2jBR3wPfAQnoidtFFYQKbQn2"
GAS_FEE_AMOUNT = "3000000"

client = AsyncJsonRpcClient(JSON_RPC_URL)
w3 = Web3(Web3.HTTPProvider(EVM_RPC_URL))

# 로깅 설정
# logging.basicConfig(level=logging.DEBUG)
ITS_CONTRACT_ADDRESS = "0x1a7580C2ef5D485E069B7cf1DF9f6478603024d3"
ITS_ABI = [...]  # Axelar ITS ABI


wallet = generate_faucet_wallet(client=client, debug=True) #테스트에 사용할 xrpl 테스트넷 지갑 생성 및 10 xrp faucet 받기

def create_wallet_from_seed(seed: str) -> Wallet:
    return Wallet.from_seed(seed=seed)

def validate_evm_address(evm_dest: str) -> str:
    if not evm_dest.startswith("0x") or len(evm_dest) != 42:
        raise ValueError("Invalid EVM address")
    return evm_dest[2:].upper()

def build_memos(
    evm_dest: str,
    axelar_chain: str = "xrpl-evm",
    gas_fee_drops: str = "3000000",
    tx_type: str = "interchain_transfer"
) -> list:
    evm_dest_clean = validate_evm_address(evm_dest)
    # EVM 주소를 ASCII 문자열로 보고, 각 문자를 16진수 ASCII 코드로 변환
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


# def bridge_xrp_to_evm_direct(evm_dest: str, amount_drops: str, axelar_chain: str = "xrpl-evm", gas_fee_drops: str = "3000000"): # 테스트 편의상 seed받아서 지갑생성은 빼놨음
#     """
#     XRPL에서 XRPL EVM Sidechain으로 XRP 브릿지 (Squid Router 없이 Axelar 멀티시그 사용)
#     """
#     # wallet = create_wallet_from_seed(seed)
#     evm_dest_raw = evm_dest[2:].lower() if evm_dest.startswith("0x") else evm_dest.lower()  # 0x 제거
#     evm_dest_hex = evm_dest_raw.encode().hex()  # ASCII로 변환 후 HEX 인코딩
#     payload = generate_payload(evm_dest)
#     memos = [
#         Memo(
#             memo_data=tx_type.encode().hex(),
#             memo_type="type".encode().hex()
#         ),
#         Memo(
#             memo_data=axelar_chain.encode().hex(),
#             memo_type="destination_chain".encode().hex()
#         ),
#         Memo(
#             memo_data=evm_dest_ascii_hex,
#             memo_data=gas_fee_drops.encode().hex(),
#             memo_type="gas_fee_amount".encode().hex()
#         )
#         # Memo(
#         #     memo_data=payload,  # 직접 HEX 사용
#         #     memo_type="payload".encode().hex()
#         # )
#     ]
#     tx = Payment(
#         account=wallet.classic_address,
#         amount=amount_drops,
#         destination=GATEWAY_ADDRESS,
#         memos=memos
#     )
#     tx = autofill(tx, client)
#     signed_tx = sign(tx, wallet)
#     result = submit_and_wait(signed_tx, client)
#     print("Tx Hash:", result.result.get("hash"))
#     print("Result:",result.result.get("meta", {}).get("TransactionResult"))
    
#     return result.result


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
            memo_data=str(gas_fee_amount).encode().hex(),
            memo_type="gas_fee_amount".encode().hex()
        ),
        Memo(
            memo_data=(payload if payload else "0"*64),
            memo_type="payload".encode().hex()
        ),
    ]
    return memos


async def bridge_xrp_to_evm(
    # seed: str, 테스트 편의상 주석처리
    evm_dest: str,
    amount_drops: str = "8000000",
   axelar_chain: str = "xrpl-evm"
) -> Dict[str, Any]:
    TX_TYPE = "interchain_transfer"
    
    try:
        # wallet = create_wallet_from_seed(seed) , 테스트 편의상 주석처리
        logging.debug(f"Bridging XRP: evm_dest={evm_dest}, amount_drops={amount_drops}, axelar_chain={axelar_chain}")
        memos = build_memos(
            evm_dest=evm_dest,
            axelar_chain=axelar_chain,
            gas_fee_drops=GAS_FEE_AMOUNT,
            tx_type=TX_TYPE
        )
        logging.debug(f"Generated memos: {memos}")
        tx = Payment(
            account=wallet.classic_address,
            amount=amount_drops,
            destination=GATEWAY_ADDRESS,
            memos=memos
        )
        tx = await autofill(tx, client)
        signed_tx = sign(tx, wallet)
        result = await submit_and_wait(signed_tx, client)
        logging.debug(f"Transaction result: {result.result}")
        return result.result
    except Exception as e:
        logging.error(f"Bridge XRP failed: {str(e)}")
        raise


def bridge_evm_to_xrpl(private_key: str, xrpl_dest: str, amount_wei: int, 
                      axelar_chain: str = "xrpl-evm", token_address: Optional[str] = None) -> Dict[str, Any]:

    try:
        account = w3.eth.account.from_key(private_key)
        its_contract = w3.eth.contract(address=ITS_CONTRACT_ADDRESS, abi=ITS_ABI)
        token_address = token_address or "0x..."
        logging.debug(f"Bridging to XRPL: xrpl_dest={xrpl_dest}, amount_wei={amount_wei}")
        
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
        logging.debug(f"Transaction receipt: {receipt}")
        return receipt
    except Exception as e:
        logging.error(f"Bridge EVM to XRPL failed: {str(e)}")
        raise


async def main():
    try:
        evm_destination = "0xD29e032D1c8d3d219e1884dE3b9ac5718BB9f2cA" 
        response = await bridge_xrp_to_evm(evm_destination) 
        print("Tx hash:", response.get("hash"))
        print("Response:",response)
    except Exception as e:
        print("Unexpected error:", e)

asyncio.run(main())