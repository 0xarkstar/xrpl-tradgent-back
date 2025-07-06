

from db.client import supabase
from models.user import UserInitRequest
from typing import Optional, List


def insert_user(user: UserInitRequest):
    response = supabase.table("users").insert({
        "wallet_address": user.wallet_address,
        "risk_profile": user.risk_profile,
        "experience": user.experience,
        "delegated": user.delegated,
        "delegated_at": user.delegated_at,
    }).execute()
    return response

def update_user_delegate(wallet_address: str, delegated: bool, delegated_at: Optional[str] = None):
    response = supabase.table("users").update({
        "delegated": delegated,
        "delegated_at": delegated_at
    }).eq("wallet_address", wallet_address).execute()
    return response

def update_user_risk_profile(wallet_address: str, risk_profile: str, experience: List[str]):
    response = supabase.table("users").update({
        "risk_profile": risk_profile,
        "experience": experience
    }).eq("wallet_address", wallet_address).execute()
    return response

async def get_user_by_address(wallet_address: str):
    response = await supabase.table("users").select("*").eq("wallet_address", wallet_address).execute()
    return response.data[0] if response.data else None