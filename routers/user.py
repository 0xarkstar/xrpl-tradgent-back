from fastapi import APIRouter, HTTPException
from models.user import UserInitRequest
from db.queries import insert_user, get_user_by_address

router = APIRouter()

@router.post("/init")
async def init_user(request: UserInitRequest):
    existing = get_user_by_address(request.wallet_address)
    if existing:
        return {"message": "User already exists.", "user": existing}
    insert_user(request)
    return {"message": "User initialized successfully."}
