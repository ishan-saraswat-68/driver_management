from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("Loaded URL:", SUPABASE_URL)
print("Loaded KEY:", SUPABASE_KEY)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)