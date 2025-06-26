from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet,generate_faucet_wallet
from xrpl.models.transactions import Payment, OfferCreate
from xrpl.models.requests import AccountInfo
from xrpl.transaction import autofill, sign, submit_and_wait
from xrpl.account import get_balance

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(JSON_RPC_URL)

wallet = generate_faucet_wallet(client, debug=True)
destination = rGpHxRQaFH4U7PYphioAuafyQgYyZouher

# print("Classic address:",wallet.classic_address)
# print("Public key:",wallet.public_key)
# print("Private key:",wallet.private_key)
# print("Seed:",wallet.seed)

# def send_payment(sender_seed: str, destination: str, amount_drops: str) 

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
