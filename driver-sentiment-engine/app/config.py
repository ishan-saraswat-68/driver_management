from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
THRESHOLD = float(os.getenv("THRESHOLD", -0.5))
COOLDOWN_HOURS = int(os.getenv("COOLDOWN_HOURS", 24))
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

print("Loaded URL:", SUPABASE_URL)
print("Loaded KEY:", SUPABASE_KEY)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)










