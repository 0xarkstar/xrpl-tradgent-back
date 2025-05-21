import base64
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment
from xrpl.transaction import autofill, sign, submit_and_wait
from xrpl.clients import JsonRpcClient

client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
ITS_ADDRESS = "rGAbJZEzU6WaYv5y1LfyN7LBBcQJ3TxsKC"  # 예시 Devnet ITS 주소

def bridge_xrp_to_evm(sender_seed: str, evm_dest: str, amount_drops: str):
    wallet = Wallet(seed=sender_seed, sequence=0)
    memo1 = {
        "Memo": {
            "MemoData": base64.b16encode(bytes.fromhex(evm_dest[2:])).decode(),
            "MemoType": base64.b16encode(b"destination_address").decode(),
        }
    }
    memo2 = {
        "Memo": {
            "MemoData": base64.b16encode(b"xrpl-evm-devnet").decode(),
            "MemoType": base64.b16encode(b"destination_chain").decode(),
        }
    }

    tx = Payment(
        account=wallet.classic_address,
        amount=amount_drops,
        destination=ITS_ADDRESS,
        memos=[memo1, memo2]
    )

    tx = autofill(tx, client)
    signed_tx = sign(tx, wallet)
    result = submit_and_wait(signed_tx, client)
    return result.result
