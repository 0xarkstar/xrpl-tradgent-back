from supabase import create_client, create_async_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def get_supabase_client():
    return await create_async_client(SUPABASE_URL, SUPABASE_KEY)
