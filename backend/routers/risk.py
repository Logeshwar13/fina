"""
routers/risk.py  – supabase-py version
"""
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from database.db import get_supabase
from schemas.schemas import RiskScoreOut
from ml.risk_scorer import compute_risk_score, RiskInput

router = APIRouter(prefix="/risk", tags=["Risk Scoring"])


def _build_risk_input(user_id: str, sb: Client) -> RiskInput:
    user_res = sb.table("users").select("*").eq("id", user_id).execute()
    if not user_res.data:
        raise HTTPException(404, f"User '{user_id}' not found")
    user = user_res.data[0]

    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()

    all_txns = sb.table("transactions").select("*").eq("user_id", user_id).execute().data or []
    this_month = [t for t in all_txns if t.get("type") == "expense" and t.get("timestamp", "") >= month_start]

    monthly_expenses  = sum(t["amount"] for t in this_month)
    fraud_count       = sum(1 for t in all_txns if t.get("is_fraud"))

    user_income = user.get("income", 0)
    txns_income = sum(t["amount"] for t in all_txns if t.get("type") == "income")
    total_monthly_income = user_income + txns_income

    # Last 6 months amounts
    monthly_amounts = []
    for offset in range(6):
        m = (now.month - offset - 1) % 12 + 1
        y = now.year if now.month > offset else now.year - 1
        total = sum(
            t["amount"] for t in all_txns
            if t.get("type") == "expense"
            and str(m).zfill(2) in (t.get("timestamp") or "")[:7]
            and str(y) in (t.get("timestamp") or "")[:7]
        )
        monthly_amounts.append(total)

    budgets = sb.table("budgets").select("*").eq("user_id", user_id).execute().data or []
    budget_overruns = 0
    for b in budgets:
        spent = sum(t["amount"] for t in this_month if t.get("category") == b.get("category"))
        if spent > b.get("limit_amount", 0):
            budget_overruns += 1

    return RiskInput(
        monthly_income     = total_monthly_income,
        monthly_expenses   = monthly_expenses,
        balance            = total_monthly_income - monthly_expenses,
        total_transactions = len(all_txns),
        fraud_count        = fraud_count,
        budget_overruns    = budget_overruns,
        total_budgets      = max(1, len(budgets)),
        monthly_amounts    = monthly_amounts,
    )


@router.get("/score", response_model=RiskScoreOut)
def get_risk_score(user_id: str = Query(...), sb: Client = Depends(get_supabase)):
    risk_input = _build_risk_input(user_id, sb)
    score, grade, label, breakdown = compute_risk_score(risk_input)
    now = datetime.now(timezone.utc)

    # Upsert risk score
    existing = sb.table("risk_scores").select("id").eq("user_id", user_id).execute()
    row = {
        "user_id":        user_id,
        "score":          score,
        "grade":          grade,
        "label":          label,
        "breakdown_json": breakdown,
        "updated_at":     now.isoformat(),
    }
    if existing.data:
        sb.table("risk_scores").update(row).eq("user_id", user_id).execute()
    else:
        row["id"] = str(uuid.uuid4())
        sb.table("risk_scores").insert(row).execute()

    return {
        "user_id":    user_id,
        "score":      score,
        "grade":      grade,
        "label":      label,
        "breakdown":  breakdown,
        "updated_at": now,
    }
