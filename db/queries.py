from db.client import supabase
from models.user import UserInitRequest
from typing import Optional, List


async def insert_user(user: UserInitRequest):
    response = await supabase.table("users").insert({
        "wallet_address": user.wallet_address,
        "risk_profile": user.risk_profile,
        "experience": user.experience,
        "delegated": user.delegated,
        "delegated_at": user.delegated_at,
    }).execute()
    return response

async def update_user_delegate(wallet_address: str, delegated: bool, delegated_at: Optional[str] = None):
    response = await supabase.table("users").update({
        "delegated": delegated,
        "delegated_at": delegated_at
    }).eq("wallet_address", wallet_address).execute()
    return response

async def update_user_risk_profile(wallet_address: str, risk_profile: str, experience: List[str]):
    response = await supabase.table("users").update({
        "risk_profile": risk_profile,
        "experience": experience
    }).eq("wallet_address", wallet_address).execute()
    return response

async def get_user_by_address(wallet_address: str):
    response = await supabase.table("users").select("*", count="exact").eq("wallet_address", wallet_address).execute()
    return response.data[0] if response.data else None

async def clear_table_data(table_name: str):
    """
    지정된 Supabase 테이블의 모든 데이터를 삭제합니다. 테이블 구조는 유지됩니다.
    """
    response = await supabase.table(table_name).delete().gt("id", 0).execute()
    return response