from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet,generate_faucet_wallet
from xrpl.models.transactions import Payment, OfferCreate
from xrpl.models.requests import AccountInfo
from xrpl.transaction import autofill, sign, submit_and_wait, autofill_and_sign
from xrpl.models.transactions import Memo
from xrpl.account import get_balance

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(JSON_RPC_URL)

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
    tx = Payment(
        account=wallet.classic_address,
        amount=amount_drops,
        destination=destination,
    )

    tx = autofill(tx, client)
    signed_tx = sign(tx, wallet)
    result = submit_and_wait(signed_tx, client)
    return result.result

send_payment(destination,"1")


def get_account_balance(address: str):
    return get_balance(address, client)

balance =get_account_balance(wallet.classic_address)
print("Account Balance:",balance)


# def create_offer(sender_seed: str, taker_gets: str, taker_pays: dict):

def create_offer(wallet,taker_gets, taker_pays, flage = None):
    # wallet = Wallet(seed=sender_seed, sequence=0)
    tx = OfferCreate(
        account=wallet.classic_address,
        taker_gets=taker_gets,
        taker_pays=taker_pays,
        flags=flags
    )

    tx = autofill(tx, client)
    signed_tx = sign(tx, wallet)
    result = submit_and_wait(signed_tx, client)
    return result.result

create_offer(
    wallet,
    taker_gets=xrpl.utils.xrp_to_drops(8),
    taker_pays={"currency": "USD", "issuer": "rUSDissuer", "value": "100"},
    flags=OfferCreateFlags.TF_IMMEDIATE_OR_CANCEL
)
