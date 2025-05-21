from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment, OfferCreate
from xrpl.models.requests import AccountInfo
from xrpl.transaction import autofill, sign, submit_and_wait
from xrpl.account import get_balance

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(JSON_RPC_URL)

def send_payment(sender_seed: str, destination: str, amount_drops: str):
    wallet = Wallet(seed=sender_seed, sequence=0)
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


def create_offer(sender_seed: str, taker_gets: str, taker_pays: dict):
    wallet = Wallet(seed=sender_seed, sequence=0)
    tx = OfferCreate(
        account=wallet.classic_address,
        taker_gets=taker_gets,
        taker_pays=taker_pays,
    )

    tx = autofill(tx, client)
    signed_tx = sign(tx, wallet)
    result = submit_and_wait(signed_tx, client)
    return result.result
