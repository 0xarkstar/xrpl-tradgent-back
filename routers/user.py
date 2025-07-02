from fastapi import APIRouter, HTTPException
from models.user import UserInitRequest
from db.queries import insert_user, get_user_by_address

router = APIRouter()


@router.post("/api/user/register")
def register_user(user: UserInitRequest):
    # 중복 지갑주소 체크
    existing = get_user_by_address(user.wallet_address)
    if existing:
        raise HTTPException(status_code=400, detail="이미 등록된 지갑주소입니다.")
    result = insert_user(user)
    return {"success": True, "data": result.data}

@router.get("/api/user/profile")
def get_user_profile(wallet_address: str):
    user = get_user_by_address(wallet_address)
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return {"success": True, "data": user}
