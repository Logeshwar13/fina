"""
routers/transactions.py  – supabase-py version
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from database.db import get_supabase
from schemas.schemas import TransactionCreate, TransactionOut, TransactionUpdate
from ml.categorizer import predictor
from ml.fraud_detector import detector

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def _get_hour(ts: Optional[datetime]) -> int:
    return (ts or datetime.now(timezone.utc)).hour


@router.get("/stats")
def get_transaction_stats(user_id: str = Query(...), sb: Client = Depends(get_supabase)):
    """Get aggregated transaction statistics for a user"""
    txns = sb.table("transactions").select("*").eq("user_id", user_id).execute().data or []
    
    income = sum(t["amount"] for t in txns if t.get("type") == "income")
    expenses = sum(t["amount"] for t in txns if t.get("type") == "expense")
    balance = income - expenses
    
    return {
        "income": income,
        "expenses": expenses,
        "balance": balance,
        "total_transactions": len(txns),
        "fraud_count": sum(1 for t in txns if t.get("is_fraud"))
    }


@router.get("", response_model=List[TransactionOut])
def list_transactions(
    user_id:  Optional[str]  = Query(None),
    category: Optional[str]  = Query(None),
    is_fraud: Optional[bool] = Query(None),
    limit:    int = Query(50, le=500),
    offset:   int = Query(0, ge=0),
    sb: Client = Depends(get_supabase),
):
    q = sb.table("transactions").select("*").order("timestamp", desc=True)
    if user_id:
        q = q.eq("user_id", user_id)
    if category:
        q = q.eq("category", category)
    if is_fraud is not None:
        q = q.eq("is_fraud", is_fraud)
    res = q.range(offset, offset + limit - 1).execute()
    return res.data or []


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: str, sb: Client = Depends(get_supabase)):
    res = sb.table("transactions").select("*").eq("id", transaction_id).execute()
    if not res.data:
        raise HTTPException(404, "Transaction not found")
    return res.data[0]


@router.post("", response_model=TransactionOut, status_code=201)
def create_transaction(body: TransactionCreate, sb: Client = Depends(get_supabase)):
    # Validate user
    user_res = sb.table("users").select("id").eq("id", body.user_id).execute()
    if not user_res.data:
        raise HTTPException(404, f"User '{body.user_id}' not found")

    # Auto-categorize
    category = body.category
    if not category:
        category, _, _ = predictor.predict(body.description)

    # Fraud detection
    ts = body.timestamp or datetime.now(timezone.utc)
    is_fraud, fraud_score, _ = detector.detect(
        amount=body.amount, hour=_get_hour(body.timestamp), location=body.location
    )

    row = {
        "id":          str(uuid.uuid4()),
        "user_id":     body.user_id,
        "amount":      body.amount,
        "description": body.description,
        "category":    category,
        "timestamp":   ts.isoformat(),
        "location":    body.location,
        "type":        body.type,
        "is_fraud":    is_fraud,
        "fraud_score": round(fraud_score, 4),
    }
    res = sb.table("transactions").insert(row).execute()
    return res.data[0]


@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: str, body: TransactionUpdate, sb: Client = Depends(get_supabase)
):
    updates = body.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(400, "No fields to update")
    res = sb.table("transactions").update(updates).eq("id", transaction_id).execute()
    if not res.data:
        raise HTTPException(404, "Transaction not found")
    return res.data[0]


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: str, sb: Client = Depends(get_supabase)):
    res = sb.table("transactions").delete().eq("id", transaction_id).execute()
    if not res.data:
        raise HTTPException(404, "Transaction not found")
