from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE

# Use SERVICE key for admin operations (bypasses RLS)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE) if SUPABASE_URL else None
