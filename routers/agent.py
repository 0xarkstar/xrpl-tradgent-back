# backend/routers/agent.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"message": "Agent router is alive."}
