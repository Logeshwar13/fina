"""
routers/fraud.py  – supabase-py version
"""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from database.db import get_supabase
from schemas.schemas import FraudDetectRequest, FraudDetectResponse, TransactionOut
from ml.fraud_detector import detector

router = APIRouter(prefix="/fraud", tags=["Fraud Detection"])


@router.post("/detect", response_model=FraudDetectResponse)
def detect_fraud(body: FraudDetectRequest):
    hour = body.hour
    if hour is None and body.timestamp:
        hour = body.timestamp.hour
    elif hour is None:
        hour = datetime.now(timezone.utc).hour

    is_fraud, fraud_score, reasons = detector.detect(
        amount=body.amount, hour=hour, location=body.location
    )
    risk_level = "high" if fraud_score > 0.7 else "medium" if fraud_score > 0.4 else "low"
    return FraudDetectResponse(
        transaction_id=body.transaction_id,
        is_fraud=is_fraud,
        fraud_score=round(fraud_score, 4),
        risk_level=risk_level,
        reasons=reasons,
    )


@router.get("/alerts", response_model=List[TransactionOut])
def fraud_alerts(
    user_id: Optional[str] = Query(None),
    limit:   int = Query(20, le=100),
    sb: Client = Depends(get_supabase),
):
    q = sb.table("transactions").select("*").eq("is_fraud", True).order("timestamp", desc=True).limit(limit)
    if user_id:
        q = q.eq("user_id", user_id)
    return q.execute().data or []


@router.put("/{transaction_id}/resolve", response_model=TransactionOut)
def resolve_fraud(transaction_id: str, sb: Client = Depends(get_supabase)):
    res = sb.table("transactions").update({"is_fraud": False, "fraud_score": 0.0}).eq("id", transaction_id).execute()
    if not res.data:
        raise HTTPException(404, "Transaction not found")
    return res.data[0]
