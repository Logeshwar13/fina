"""
routers/insights.py  – supabase-py version
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from database.db import get_supabase
from schemas.schemas import InsightsResponse, InsightItem

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("", response_model=InsightsResponse)
def get_insights(user_id: str = Query(...), sb: Client = Depends(get_supabase)):
    user_res = sb.table("users").select("*").eq("id", user_id).execute()
    if not user_res.data:
        raise HTTPException(404, f"User '{user_id}' not found")
    user = user_res.data[0]

    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()

    all_txns    = sb.table("transactions").select("*").eq("user_id", user_id).execute().data or []
    this_month  = [t for t in all_txns if t.get("type") == "expense" and (t.get("timestamp") or "") >= month_start]
    budgets     = sb.table("budgets").select("*").eq("user_id", user_id).execute().data or []

    income        = user.get("income") or 1
    total_expense = sum(t["amount"] for t in this_month)
    insights: list[InsightItem] = []

    # 1. Savings rate
    savings_rate = max(0, (income - total_expense) / income * 100)
    if savings_rate >= 30:
        insights.append(InsightItem(type="positive", icon="✅", title="Great Savings Rate",
            message=f"You're saving {savings_rate:.0f}% of income this month. Keep it up!"))
    elif savings_rate < 10:
        insights.append(InsightItem(type="warning", icon="⚠️", title="Low Savings Rate",
            message=f"Saving only {savings_rate:.0f}% this month. Target 20%+."))

    # 2. Top spending category
    if this_month:
        cat_totals: dict[str, float] = {}
        for t in this_month:
            cat_totals[t["category"]] = cat_totals.get(t["category"], 0) + t["amount"]
        top_cat, top_amt = max(cat_totals.items(), key=lambda x: x[1])
        pct = top_amt / total_expense * 100 if total_expense else 0
        insights.append(InsightItem(type="info", icon="📊", title=f"Top Spending: {top_cat}",
            message=f"'{top_cat}' accounts for {pct:.0f}% (₹{top_amt:,.0f}) of expenses this month."))

    # 3. Budget overruns
    overrun_cats = []
    for b in budgets:
        spent = sum(t["amount"] for t in this_month if t.get("category") == b.get("category"))
        if spent > b.get("limit_amount", 0):
            overrun_cats.append(b["category"])
    if overrun_cats:
        insights.append(InsightItem(type="warning", icon="🔴", title="Budget Exceeded",
            message=f"Over budget in: {', '.join(overrun_cats)}."))
    elif budgets:
        insights.append(InsightItem(type="positive", icon="🟢", title="Budgets on Track",
            message="All budgets within limits this month!"))

    # 4. Fraud alerts
    fraud_count = sum(1 for t in this_month if t.get("is_fraud"))
    if fraud_count > 0:
        insights.append(InsightItem(type="warning", icon="🚨",
            title=f"{fraud_count} Suspicious Transaction{'s' if fraud_count > 1 else ''} Detected",
            message="AI flagged unusual activity. Review your fraud alerts."))

    if not insights:
        insights.append(InsightItem(type="info", icon="💡", title="No Transactions Yet",
            message="Add transactions to get personalised financial insights."))

    return InsightsResponse(user_id=user_id, insights=insights, generated_at=now)
