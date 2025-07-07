from db.client import get_supabase_client
from models.user import UserInitRequest
from typing import Optional, List


async def insert_user(user: UserInitRequest):
    supabase = await get_supabase_client()
    response = await supabase.table("users").insert({
        "xrpl_wallet_address": user.xrpl_wallet_address,
        "evm_wallet_address": user.evm_wallet_address,
        "risk_profile": user.risk_profile,
        "experience": user.experience,
        "delegated": user.delegated,
        "delegated_at": user.delegated_at,
    }).execute()
    return response

async def update_user_delegate(xrpl_wallet_address: str, delegated: bool, delegated_at: Optional[str] = None):
    supabase = await get_supabase_client()
    response = await supabase.table("users").update({
        "delegated": delegated,
        "delegated_at": delegated_at
    }).eq("xrpl_wallet_address", xrpl_wallet_address).execute()
    return response

async def update_user_risk_profile(xrpl_wallet_address: str, risk_profile: str, experience: List[str]):
    supabase = await get_supabase_client()
    response = await supabase.table("users").update({
        "risk_profile": risk_profile,
        "experience": experience
    }).eq("xrpl_wallet_address", xrpl_wallet_address).execute()
    return response

async def get_user_by_xrpl_address(xrpl_wallet_address: str):
    supabase = await get_supabase_client()
    response = await supabase.table("users").select("*", count="exact").eq("xrpl_wallet_address", xrpl_wallet_address).execute()
    return response.data[0] if response.data else None

async def get_user_by_evm_address(evm_wallet_address: str):
    supabase = await get_supabase_client()
    response = await supabase.table("users").select("*", count="exact").eq("evm_wallet_address", evm_wallet_address).execute()
    return response.data[0] if response.data else None

async def clear_table_data(table_name: str):
    """
    지정된 Supabase 테이블의 모든 데이터를 삭제합니다. 테이블 구조는 유지됩니다.
    """
    supabase = await get_supabase_client()
    response = await supabase.table(table_name).delete().gt("id", 0).execute()
    return response