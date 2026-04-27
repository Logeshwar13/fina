"""
database/db.py
──────────────
Supabase client provider.
Uses SUPABASE_SERVICE_KEY (service_role) which bypasses RLS — correct
for a trusted backend server.
Falls back to SUPABASE_ANON_KEY if service key not set.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL  = os.getenv("SUPABASE_URL", "")
# Service role key bypasses RLS — ideal for backend servers
SERVICE_KEY   = os.getenv("SUPABASE_SERVICE_KEY", "")
ANON_KEY      = os.getenv("SUPABASE_ANON_KEY", "")
_key          = SERVICE_KEY or ANON_KEY

if not SUPABASE_URL or not _key:
    raise RuntimeError(
        "Set SUPABASE_URL and SUPABASE_SERVICE_KEY (or SUPABASE_ANON_KEY) in backend/.env"
    )

_client: Client = create_client(SUPABASE_URL, _key)
_using = "service_role" if SERVICE_KEY else "anon"
print(f"[DB] Supabase client initialised with {_using} key")


def get_supabase() -> Client:
    """FastAPI dependency – returns the singleton Supabase client."""
    return _client
