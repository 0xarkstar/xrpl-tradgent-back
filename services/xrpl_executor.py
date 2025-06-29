from xrpl.clients import JsonRpcClient
<<<<<<< Updated upstream
from xrpl.wallet import Wallet,generate_faucet_wallet
from xrpl.models.transactions import Payment, OfferCreate
from xrpl.models.requests import AccountInfo
from xrpl.transaction import autofill, sign, submit_and_wait, autofill_and_sign
from xrpl.models.transactions import Memo
=======
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment, OfferCreate, AMMDeposit
from xrpl.transaction import autofill, sign, submit_and_wait
>>>>>>> Stashed changes
from xrpl.account import get_balance
import xrpl.utils
from xrpl.models.amounts import IssuedCurrencyAmount

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(JSON_RPC_URL)

<<<<<<< Updated upstream
wallet = generate_faucet_wallet(client, debug=True)  # 테스트넷 지갑주소 생성 및 faucet 받기
destination = "rGpHxRQaFH4U7PYphioAuafyQgYyZouher" # 임의로 생성한 테스트넷 주소, 트랜잭션 전송 확인 목적

bridge_address = "rsCPY4vwEiGogSraV9FeRZXca6gUBWZkhg" # xrpl 체인 위 axelar Multisig 주소
#evm_destination="7859556BF9E1E3F47E6AA195C4F85FFF230C0A50" 

memo_data = "6A7Ecde149D7Df2e0dda2e94b327393A8be694bd" # xrpl evm 테스트넷 주소소
memo = [
    Memo(
        memo_data= memo_data,
        memo_type="64657374696E6174696F6E5F61646472657373" #hex("destination_address")
        
        
    )
]

def xrpl_to_axelar_bridge(bridge_address,amount_drops:str,memo): # xrpl를 axelar Multisig주소로 전송, memo를 변경함으로써 목표 xrpl evm 주소를 변경가능능
    # wallet = Wallet(seed = sender_seed, sequence = 0)
    tx = Payment(
        account = wallet.classic_address,
        destination = bridge_address,
        amount = amount_drops,
        memos = memo
    )

    tx = autofill(tx, client)
    signed_tx = sign(tx, wallet)
    response = submit_and_wait(signed_tx, client)
    print("Tx Hash:", response.result.get("hash"))
    print("Result:",response.result.get("meta", {}).get("TransactionResult"))
    return response.result

xrpl_to_axelar_bridge(bridge_address,"8000000",memo)

print("Classic address:",wallet.classic_address)
print("Public key:",wallet.public_key)
print("Private key:",wallet.private_key)
print("Seed:",wallet.seed)

def send_payment(sender_seed: str, destination: str, amount_drops: str) 

def send_payment(wallet,destination: str, amount_drops: str):
    # wallet = Wallet(seed=sender_seed, sequence=0)
=======
def create_wallet_from_seed(seed: str):
    return Wallet.from_seed(seed=seed)

def send_payment(seed: str, destination: str, amount_drops: str):
    wallet = create_wallet_from_seed(seed)
>>>>>>> Stashed changes
    tx = Payment(
        account=wallet.classic_address,
        amount=amount_drops,
        destination=destination,
    )
    tx = autofill(tx, client)
    signed_tx = sign(tx, wallet)
    result = submit_and_wait(signed_tx, client)
    return result.result

def get_account_balance(address: str):
    return get_balance(address, client)

def create_offer(seed: str, taker_gets: str, taker_pays: dict, flags: int = None):
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

def deposit_to_amm(seed: str, asset1: dict, asset2: dict, amount1: str = None, amount2: str = None, flags: int = None):
    wallet = create_wallet_from_seed(seed)
    tx_fields = {
        "account": wallet.classic_address,
        "asset": asset1,
        "asset2": asset2,
    }
    if amount1:
        if asset1.get("currency") == "XRP":
            tx_fields["amount"] = amount1
        else:
            tx_fields["amount"] = IssuedCurrencyAmount(
                currency=asset1["currency"],
                issuer=asset1["issuer"],
                value=amount1
            )
    if amount2:
        if asset2.get("currency") == "XRP":
            tx_fields["amount2"] = amount2
        else:
            tx_fields["amount2"] = IssuedCurrencyAmount(
                currency=asset2["currency"],
                issuer=asset2["issuer"],
                value=amount2
            )
    if flags:
        tx_fields["flags"] = flags
    tx = AMMDeposit(**tx_fields)
    tx = autofill(tx, client)
    signed_tx = sign(tx, wallet)
    result = submit_and_wait(signed_tx, client)
    return result.result