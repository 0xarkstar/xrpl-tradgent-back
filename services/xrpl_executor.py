from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment, OfferCreate, AMMDeposit
from xrpl.transaction import autofill, sign, submit_and_wait, autofill_and_sign
from xrpl.models.transactions import Memo
from xrpl.account import get_balance
import xrpl.utils
from xrpl.models.amounts import IssuedCurrencyAmount

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(JSON_RPC_URL)

def create_wallet_from_seed(seed: str):
    return Wallet.from_seed(seed=seed)

def send_payment(seed: str, destination: str, amount_drops: str):
    wallet = create_wallet_from_seed(seed)
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