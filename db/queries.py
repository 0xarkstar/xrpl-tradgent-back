from db.client import supabase
from models.user import UserInitRequest

def insert_user(user: UserInitRequest):
    response = supabase.table("users").insert({
        "wallet_address": user.wallet_address,
        "risk_profile": user.risk_profile,
        "experience": user.experience,
    }).execute()
    return response

def get_user_by_address(wallet_address: str):
    response = supabase.table("users").select("*").eq("wallet_address", wallet_address).execute()
    return response.data[0] if response.data else None