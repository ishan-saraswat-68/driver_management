from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Alert threshold is on 0-5 scale (2.5 = neutral midpoint).
# Configurable via ALERT_THRESHOLD env var — read directly in alert_service.py
COOLDOWN_HOURS = int(os.getenv("COOLDOWN_HOURS", 24))
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
