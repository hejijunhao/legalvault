# core/supabase_client.py

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from core.config import settings

load_dotenv()

# Get Supabase credentials from settings or environment variables
SUPABASE_URL = settings.SUPABASE_URL or os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = settings.SUPABASE_ANON_KEY or os.getenv("SUPABASE_ANON_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and key must be set in environment variables")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client() -> Client:
    """Return the Supabase client instance."""
    return supabase