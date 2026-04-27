"""
data/create_tables_supabase.py
──────────────────────────────
Creates all application tables in Supabase via the REST SQL API.
Run once:
    cd backend
    python data/create_tables_supabase.py
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

SUPABASE_URL      = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# We'll create tables by inserting a dummy row and letting Supabase
# auto-create — actually we use the supabase admin SQL edge function.
# Instead, we output the SQL for the user to run in Supabase SQL Editor.

SQL = """
-- Personal Finance Advisor – Table Definitions
-- Run this in: Supabase Dashboard → SQL Editor → New Query

CREATE TABLE IF NOT EXISTS users (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name        TEXT NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    income      FLOAT DEFAULT 0,
    goals_json  JSONB DEFAULT '[]',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transactions (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id     TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount      FLOAT NOT NULL,
    description TEXT DEFAULT '',
    category    TEXT DEFAULT 'Uncategorized',
    timestamp   TIMESTAMPTZ DEFAULT NOW(),
    location    TEXT DEFAULT '',
    type        TEXT DEFAULT 'expense',
    is_fraud    BOOLEAN DEFAULT FALSE,
    fraud_score FLOAT DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS budgets (
    id           TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id      TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category     TEXT NOT NULL,
    limit_amount FLOAT NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS risk_scores (
    id             TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id        TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score          INTEGER DEFAULT 50,
    grade          TEXT DEFAULT 'C',
    label          TEXT DEFAULT 'Moderate Risk',
    breakdown_json JSONB DEFAULT '{}',
    updated_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Disable RLS (for development — enable and add policies in production)
ALTER TABLE users        DISABLE ROW LEVEL SECURITY;
ALTER TABLE transactions DISABLE ROW LEVEL SECURITY;
ALTER TABLE budgets      DISABLE ROW LEVEL SECURITY;
ALTER TABLE risk_scores  DISABLE ROW LEVEL SECURITY;
"""

print("=" * 60)
print("PASTE THE FOLLOWING SQL INTO SUPABASE SQL EDITOR:")
print("https://supabase.com/dashboard/project/tvxstddevrwdllswrxog/sql/new")
print("=" * 60)
print(SQL)
print("=" * 60)
print("\nAfter running the SQL, run:")
print("  python data/seed_supabase.py")
