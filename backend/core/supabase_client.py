# core/supabase_client.py

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from core.config import settings

load_dotenv()

# Get Supabase credentials from settings or environment variables
SUPABASE_URL = settings.SUPABASE_URL or os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")

# For backend operations, we should use the service role key
SUPABASE_SERVICE_KEY = settings.SUPABASE_SERVICE_ROLE_KEY or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Fallback to anon key only if service key is not available (not recommended for production)
SUPABASE_KEY = SUPABASE_SERVICE_KEY or settings.SUPABASE_ANON_KEY or os.getenv("SUPABASE_ANON_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and key must be set in environment variables")

if not SUPABASE_SERVICE_KEY:
    import warnings
    warnings.warn("SUPABASE_SERVICE_ROLE_KEY is not set. Using anon key which may have limited permissions.", RuntimeWarning)

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client() -> Client:
    """Return the Supabase client instance."""
    return supabase