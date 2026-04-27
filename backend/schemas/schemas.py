"""
schemas/schemas.py
──────────────────
Pydantic v2 request/response models for every endpoint.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field


# ── Users ────────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    id:         Optional[str] = None   # set by Supabase Auth; auto-generated if omitted
    name:   str
    email:  EmailStr
    income: float = 0.0
    goals_json: Optional[List[Dict[str, Any]]] = []


class UserOut(BaseModel):
    id:         str
    name:       str
    email:      str
    income:     float
    goals_json: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Transactions ─────────────────────────────────────────────────────────────
class TransactionCreate(BaseModel):
    user_id:     str
    amount:      float = Field(..., gt=0)
    description: str   = ""
    category:    Optional[str] = None     # if None → auto-categorized
    location:    str   = ""
    type:        str   = "expense"        # expense | income
    timestamp:   Optional[datetime] = None

class TransactionUpdate(BaseModel):
    amount:      Optional[float] = None
    description: Optional[str]  = None
    category:    Optional[str]  = None
    location:    Optional[str]  = None
    type:        Optional[str]  = None
    is_fraud:    Optional[bool] = None
    fraud_score: Optional[float] = None

class TransactionOut(BaseModel):
    id:          str
    user_id:     str
    amount:      float
    description: str
    category:    str
    timestamp:   datetime
    location:    str
    type:        str
    is_fraud:    bool
    fraud_score: float

    class Config:
        from_attributes = True


# ── Budgets ──────────────────────────────────────────────────────────────────
class BudgetCreate(BaseModel):
    user_id:      str
    category:     str
    limit_amount: float = Field(..., gt=0)

class BudgetOut(BaseModel):
    id:           str
    user_id:      str
    category:     str
    limit_amount: float
    created_at:   datetime

    class Config:
        from_attributes = True


# ── Categorization ───────────────────────────────────────────────────────────
class CategorizeRequest(BaseModel):
    description: str
    amount:      Optional[float] = None  # context hint for the model

class CategorizeResponse(BaseModel):
    category:    str
    confidence:  float           # 0.0 – 1.0
    alternatives: List[str] = []


# ── Fraud Detection ──────────────────────────────────────────────────────────
class FraudDetectRequest(BaseModel):
    transaction_id: Optional[str] = None
    amount:         float
    description:    str = ""
    category:       str = ""
    location:       str = ""
    hour:           Optional[int] = None   # 0-23, inferred from timestamp if omitted
    timestamp:      Optional[datetime] = None

class FraudDetectResponse(BaseModel):
    transaction_id: Optional[str]
    is_fraud:       bool
    fraud_score:    float          # 0.0 – 1.0
    risk_level:     str            # low | medium | high
    reasons:        List[str]


# ── Risk Score ───────────────────────────────────────────────────────────────
class RiskScoreOut(BaseModel):
    user_id:    str
    score:      int
    grade:      str
    label:      str
    breakdown:  Dict[str, float]
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Insights ─────────────────────────────────────────────────────────────────
class InsightItem(BaseModel):
    type:    str    # info | warning | positive
    title:   str
    message: str
    icon:    str = "💡"

class InsightsResponse(BaseModel):
    user_id:  str
    insights: List[InsightItem]
    generated_at: datetime


# ── Insurance ────────────────────────────────────────────────────────────────
class InsurancePolicyCreate(BaseModel):
    user_id:           str
    policy_type:       str  # health | life | vehicle | home | travel
    provider:          str = ""
    policy_number:     str = ""
    coverage_amount:   float = Field(..., gt=0)
    premium_amount:    float = Field(..., gt=0)
    premium_frequency: str = "annual"
    start_date:        datetime
    end_date:          datetime
    beneficiaries:     List[Dict[str, Any]] = []
    notes:             str = ""

class InsurancePolicyUpdate(BaseModel):
    policy_type:       Optional[str] = None
    provider:          Optional[str] = None
    policy_number:     Optional[str] = None
    coverage_amount:   Optional[float] = None
    premium_amount:    Optional[float] = None
    premium_frequency: Optional[str] = None
    start_date:        Optional[datetime] = None
    end_date:          Optional[datetime] = None
    beneficiaries:     Optional[List[Dict[str, Any]]] = None
    status:            Optional[str] = None
    notes:             Optional[str] = None

class InsurancePolicyOut(BaseModel):
    id:                str
    user_id:           str
    policy_type:       str
    provider:          str
    policy_number:     str
    coverage_amount:   float
    premium_amount:    float
    premium_frequency: str
    start_date:        datetime
    end_date:          datetime
    beneficiaries:     List[Dict[str, Any]]
    status:            str
    notes:             str
    created_at:        datetime
    updated_at:        datetime

    class Config:
        from_attributes = True


class InsuranceRiskAssessmentCreate(BaseModel):
    user_id:           str
    age:               int = Field(..., gt=0, lt=120)
    dependents:        int = Field(default=0, ge=0)
    annual_income:     float = Field(..., gt=0)
    monthly_expenses:  float = Field(..., gt=0)
    existing_loans:    float = Field(default=0.0, ge=0)
    health_conditions: List[str] = []
    lifestyle_factors: Dict[str, Any] = {}

class InsuranceRiskAssessmentOut(BaseModel):
    id:                          str
    user_id:                     str
    age:                         int
    dependents:                  int
    annual_income:               float
    monthly_expenses:            float
    existing_loans:              float
    health_conditions:           List[str]
    lifestyle_factors:           Dict[str, Any]
    recommended_life_coverage:   float
    recommended_health_coverage: float
    current_life_coverage:       float
    current_health_coverage:     float
    coverage_gap_life:           float
    coverage_gap_health:         float
    risk_score:                  int
    risk_level:                  str
    recommendations:             List[str]
    created_at:                  datetime
    updated_at:                  datetime

    class Config:
        from_attributes = True
