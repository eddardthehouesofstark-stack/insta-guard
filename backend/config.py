import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL     = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY     = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE = os.getenv("SUPABASE_SERVICE_KEY", "")
GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")  # leave blank to use mock
JWT_SECRET       = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM    = "HS256"
JWT_EXPIRE_HOURS = 24

# Threshold defaults (overridden by DB values at runtime)
DEFAULT_AUTO_APPROVE_MAX  = 49
DEFAULT_MANUAL_REVIEW_MIN = 50
DEFAULT_AUTO_REJECT_MIN   = 80
