"""
routers/categorize.py
─────────────────────
POST /categorize – classify a transaction description using local ML.
"""

from fastapi import APIRouter
from schemas.schemas import CategorizeRequest, CategorizeResponse
from ml.categorizer import predictor

router = APIRouter(prefix="/categorize", tags=["Categorization"])


@router.post("/", response_model=CategorizeResponse)
def categorize(body: CategorizeRequest):
    """
    Predict expense category from transaction description text.
    Uses TF-IDF + Logistic Regression (or keyword fallback).
    """
    category, confidence, alternatives = predictor.predict(body.description)
    return CategorizeResponse(
        category=category,
        confidence=round(confidence, 4),
        alternatives=alternatives,
    )
