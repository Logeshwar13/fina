"""
data/seed_supabase.py
─────────────────────
Seeds Supabase with synthetic users, budgets, and transactions via supabase-py REST.

Usage:
    cd backend
    python data/seed_supabase.py --users 2 --transactions 80
"""

import sys, os, argparse, uuid, random
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from faker import Faker
from supabase import create_client

load_dotenv()

SUPABASE_URL      = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
fake = Faker(); Faker.seed(42); random.seed(42)

CATEGORIES = [
    "Food & Dining", "Transportation", "Shopping", "Entertainment",
    "Healthcare", "Utilities", "Housing", "Education", "Travel",
]

DESCRIPTIONS = {
    "Food & Dining":    ["Zomato order", "Starbucks coffee", "Swiggy delivery", "Restaurant dinner", "Grocery"],
    "Transportation":   ["Uber ride", "Fuel top-up", "Metro card", "Auto-rickshaw", "Cab booking"],
    "Shopping":         ["Amazon purchase", "Flipkart order", "Clothes shopping", "Electronics", "Books"],
    "Entertainment":    ["Netflix subscription", "Movie tickets", "Spotify premium", "Gaming", "Concert"],
    "Healthcare":       ["Pharmacy", "Doctor visit", "Lab tests", "Hospital bill", "Dental"],
    "Utilities":        ["Electricity bill", "Water bill", "Internet", "Mobile recharge", "Gas"],
    "Housing":          ["Monthly rent", "Maintenance", "Repair", "Cleaning"],
    "Education":        ["Course fee", "Textbooks", "Online class", "Tuition"],
    "Travel":           ["Hotel booking", "Flight ticket", "Travel insurance", "Airbnb"],
}

AMOUNT_RANGES = {
    "Food & Dining": (50, 800), "Transportation": (30, 500),
    "Shopping": (200, 5000), "Entertainment": (100, 2000),
    "Healthcare": (100, 3000), "Utilities": (200, 3000),
    "Housing": (5000, 30000), "Education": (500, 10000), "Travel": (1000, 50000),
}


def seed(n_users=2, n_transactions=80):
    users = []
    for _ in range(n_users):
        u = {
            "id":         str(uuid.uuid4()),
            "name":       fake.name(),
            "email":      fake.unique.email(),
            "income":     random.choice([50000, 60000, 80000, 100000]),
            "goals_json": [
                {"id": "1", "label": "Emergency Fund", "target": 150000, "current": random.randint(20000, 100000), "color": "#3b82f6"},
                {"id": "2", "label": "Vacation",       "target": 50000,  "current": random.randint(0, 40000),      "color": "#8b5cf6"},
            ],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        res = sb.table("users").insert(u).execute()
        users.append(res.data[0])
        print(f"  User created: {u['name']} <{u['email']}>")

    # Budgets
    for u in users:
        budgets = []
        for cat in random.sample(CATEGORIES, k=5):
            lo, hi = AMOUNT_RANGES[cat]
            budgets.append({
                "id": str(uuid.uuid4()), "user_id": u["id"],
                "category": cat, "limit_amount": random.randint(lo, hi * 2),
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
        sb.table("budgets").insert(budgets).execute()
        print(f"  {len(budgets)} budgets created for {u['name']}")

    # Transactions
    for u in users:
        txns = []
        per_user = n_transactions // n_users
        for _ in range(per_user):
            cat = random.choice(CATEGORIES)
            lo, hi = AMOUNT_RANGES[cat]
            days_ago = random.randint(0, 180)
            ts = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=random.randint(0, 23))
            is_fraud = random.random() < 0.05
            txns.append({
                "id":          str(uuid.uuid4()),
                "user_id":     u["id"],
                "amount":      round(random.uniform(lo, hi), 2),
                "description": random.choice(DESCRIPTIONS[cat]),
                "category":    cat,
                "timestamp":   ts.isoformat(),
                "location":    fake.city(),
                "type":        "expense",
                "is_fraud":    is_fraud,
                "fraud_score": round(random.uniform(0.7, 1.0) if is_fraud else random.uniform(0, 0.3), 4),
            })
        # Income entries (6 months salary)
        for month_back in range(6):
            ts = (datetime.now(timezone.utc).replace(day=1) - timedelta(days=30 * month_back))
            txns.append({
                "id": str(uuid.uuid4()), "user_id": u["id"],
                "amount": u["income"], "description": "Monthly salary credit",
                "category": "Income", "timestamp": ts.isoformat(),
                "location": "Bank", "type": "income",
                "is_fraud": False, "fraud_score": 0.0,
            })
        # Insert in batches of 50
        for i in range(0, len(txns), 50):
            sb.table("transactions").insert(txns[i:i+50]).execute()
        print(f"  {len(txns)} transactions created for {u['name']}")

    print("\n✅ Supabase seeded successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", type=int, default=2)
    parser.add_argument("--transactions", type=int, default=80)
    args = parser.parse_args()
    seed(args.users, args.transactions)
