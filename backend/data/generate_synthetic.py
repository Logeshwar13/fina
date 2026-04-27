"""
data/generate_synthetic.py
──────────────────────────
Generates synthetic users + transactions and inserts them into the DB.
Useful for demoing the app without real banking data.

Usage:
    cd backend
    python data/generate_synthetic.py --users 3 --transactions 100
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import argparse
import random
from datetime import datetime, timezone, timedelta
from faker import Faker

from database.db import SessionLocal, engine
from database.models import Base, User, Transaction, Budget, RiskScore

fake = Faker()
Faker.seed(42)
random.seed(42)

CATEGORIES = [
    "Food & Dining", "Transportation", "Shopping", "Entertainment",
    "Healthcare", "Insurance", "Utilities", "Housing", "Education", "Travel",
]

DESCRIPTIONS = {
    "Food & Dining":    ["Zomato order", "Coffee at Starbucks", "Swiggy delivery", "Restaurant dinner", "Grocery store"],
    "Transportation":   ["Uber ride", "Fuel top-up", "Metro card", "Auto-rickshaw", "Cab booking"],
    "Shopping":         ["Amazon purchase", "Flipkart order", "Clothes shopping", "Electronics", "Book purchase"],
    "Entertainment":    ["Netflix subscription", "Movie tickets", "Spotify premium", "Gaming top-up", "Concert tickets"],
    "Healthcare":       ["Pharmacy", "Doctor consultation", "Lab tests", "Hospital bill", "Dental checkup", "Heart operation", "Medical checkup"],
    "Insurance":        ["Health insurance premium", "Life insurance premium", "Car insurance renewal", "Policy payment", "Insurance premium"],
    "Utilities":        ["Electricity bill", "Water bill", "Internet bill", "Mobile recharge", "Gas cylinder"],
    "Housing":          ["Monthly rent", "House maintenance", "Repair work", "Cleaning service"],
    "Education":        ["Course subscription", "Textbooks", "Online class", "Tuition fee"],
    "Travel":           ["Hotel booking", "Flight ticket", "Travel insurance", "Airbnb"],
}

AMOUNT_RANGES = {
    "Food & Dining":    (50,  800),
    "Transportation":   (30,  500),
    "Shopping":         (200, 5000),
    "Entertainment":    (100, 2000),
    "Healthcare":       (100, 3000),
    "Insurance":        (5000, 50000),
    "Utilities":        (200, 3000),
    "Housing":          (5000, 30000),
    "Education":        (500, 10000),
    "Travel":           (1000, 50000),
}


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("[DB] Tables created ✓")


def seed(n_users: int = 2, n_transactions: int = 80):
    db = SessionLocal()
    try:
        # ── Users ─────────────────────────────────────────────────────────────
        users = []
        for _ in range(n_users):
            u = User(
                name   = fake.name(),
                email  = fake.unique.email(),
                income = random.choice([50000, 60000, 80000, 100000, 120000]),
                goals_json=[
                    {"id": "1", "label": "Emergency Fund", "target": 150000, "current": random.randint(20000, 100000), "color": "#3b82f6"},
                    {"id": "2", "label": "Vacation",       "target": 50000,  "current": random.randint(0, 40000),      "color": "#8b5cf6"},
                ],
            )
            db.add(u)
            users.append(u)
        db.flush()
        print(f"[Seed] Created {n_users} users")

        # ── Budgets ───────────────────────────────────────────────────────────
        for u in users:
            for cat in random.sample(CATEGORIES, k=5):
                low, high = AMOUNT_RANGES[cat]
                db.add(Budget(
                    user_id      = u.id,
                    category     = cat,
                    limit_amount = random.randint(low, high * 2),
                ))
        db.flush()

        # ── Transactions ──────────────────────────────────────────────────────
        txn_count = 0
        for u in users:
            per_user = n_transactions // n_users
            for i in range(per_user):
                cat     = random.choice(CATEGORIES)
                lo, hi  = AMOUNT_RANGES[cat]
                amount  = round(random.uniform(lo, hi), 2)
                days_ago = random.randint(0, 180)
                ts = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=random.randint(0, 23))

                # ~5% fraud
                is_fraud    = random.random() < 0.05
                fraud_score = round(random.uniform(0.7, 1.0), 4) if is_fraud else round(random.uniform(0, 0.3), 4)

                db.add(Transaction(
                    user_id     = u.id,
                    amount      = amount,
                    description = random.choice(DESCRIPTIONS[cat]),
                    category    = cat,
                    timestamp   = ts,
                    location    = fake.city(),
                    type        = "expense",
                    is_fraud    = is_fraud,
                    fraud_score = fraud_score,
                ))
                txn_count += 1

            # 1 income transaction per month
            for month_back in range(6):
                ts = datetime.now(timezone.utc).replace(day=1) - timedelta(days=30 * month_back)
                db.add(Transaction(
                    user_id     = u.id,
                    amount      = u.income,
                    description = "Monthly salary credit",
                    category    = "Income",
                    timestamp   = ts,
                    location    = "Bank",
                    type        = "income",
                    is_fraud    = False,
                    fraud_score = 0.0,
                ))

        db.commit()
        print(f"[Seed] Created {txn_count} transactions  ({n_users * 6} income entries)")
        print("[Seed] ✅  Database seeded successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--users",        type=int, default=2)
    parser.add_argument("--transactions", type=int, default=80)
    args = parser.parse_args()

    create_tables()
    seed(args.users, args.transactions)
