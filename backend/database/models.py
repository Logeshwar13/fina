"""
database/models.py
──────────────────
ORM table definitions.
Tables:
  - users
  - transactions
  - budgets
  - risk_scores
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Float, Boolean, Integer,
    DateTime, ForeignKey, JSON, Text
)
from sqlalchemy.orm import relationship
from .db import Base


def _now():
    return datetime.now(timezone.utc)


def _uuid():
    return str(uuid.uuid4())


# ── Users ────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id          = Column(String, primary_key=True, default=_uuid)
    name        = Column(String(120), nullable=False)
    email       = Column(String(200), unique=True, nullable=False, index=True)
    income      = Column(Float, default=0.0)       # monthly income
    goals_json  = Column(JSON, default=list)        # [{label, target, current}]
    created_at  = Column(DateTime, default=_now)

    transactions = relationship("Transaction", back_populates="user", cascade="all, delete")
    budgets      = relationship("Budget",      back_populates="user", cascade="all, delete")
    risk_scores  = relationship("RiskScore",   back_populates="user", cascade="all, delete")
    insurance_policies = relationship("InsurancePolicy", back_populates="user", cascade="all, delete")
    insurance_assessments = relationship("InsuranceRiskAssessment", back_populates="user", cascade="all, delete")


# ── Transactions ─────────────────────────────────────────────────────────────
class Transaction(Base):
    __tablename__ = "transactions"

    id          = Column(String, primary_key=True, default=_uuid)
    user_id     = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    amount      = Column(Float, nullable=False)
    description = Column(String(300), nullable=False, default="")
    category    = Column(String(80), default="Uncategorized")
    timestamp   = Column(DateTime, default=_now, index=True)
    location    = Column(String(200), default="")
    type        = Column(String(20), default="expense")  # expense | income
    is_fraud    = Column(Boolean, default=False)
    fraud_score = Column(Float, default=0.0)  # 0.0 – 1.0 anomaly probability

    user = relationship("User", back_populates="transactions")


# ── Budgets ──────────────────────────────────────────────────────────────────
class Budget(Base):
    __tablename__ = "budgets"

    id           = Column(String, primary_key=True, default=_uuid)
    user_id      = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    category     = Column(String(80), nullable=False)
    limit_amount = Column(Float, nullable=False)
    created_at   = Column(DateTime, default=_now)

    user = relationship("User", back_populates="budgets")


# ── Risk Scores ───────────────────────────────────────────────────────────────
class RiskScore(Base):
    __tablename__ = "risk_scores"

    id             = Column(String, primary_key=True, default=_uuid)
    user_id        = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    score          = Column(Integer, default=50)      # 0 – 100
    grade          = Column(String(2), default="C")   # A B C D F
    label          = Column(String(50), default="Moderate Risk")
    breakdown_json = Column(JSON, default=dict)        # {category: score}
    updated_at     = Column(DateTime, default=_now, onupdate=_now)

    user = relationship("User", back_populates="risk_scores")


# ── Insurance Policies ────────────────────────────────────────────────────────
class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"

    id              = Column(String, primary_key=True, default=_uuid)
    user_id         = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    policy_type     = Column(String(50), nullable=False)  # health | life | vehicle | home | travel
    provider        = Column(String(200), default="")
    policy_number   = Column(String(100), default="")
    coverage_amount = Column(Float, nullable=False)       # sum insured
    premium_amount  = Column(Float, nullable=False)       # annual/monthly premium
    premium_frequency = Column(String(20), default="annual")  # annual | monthly | quarterly
    start_date      = Column(DateTime, nullable=False)
    end_date        = Column(DateTime, nullable=False)
    beneficiaries   = Column(JSON, default=list)          # [{name, relation, percentage}]
    status          = Column(String(20), default="active") # active | expired | cancelled
    notes           = Column(Text, default="")
    created_at      = Column(DateTime, default=_now)
    updated_at      = Column(DateTime, default=_now, onupdate=_now)

    user = relationship("User", back_populates="insurance_policies")


# ── Insurance Risk Assessment ─────────────────────────────────────────────────
class InsuranceRiskAssessment(Base):
    __tablename__ = "insurance_risk_assessments"

    id                  = Column(String, primary_key=True, default=_uuid)
    user_id             = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    age                 = Column(Integer, nullable=False)
    dependents          = Column(Integer, default=0)
    annual_income       = Column(Float, nullable=False)
    monthly_expenses    = Column(Float, nullable=False)
    existing_loans      = Column(Float, default=0.0)
    health_conditions   = Column(JSON, default=list)      # ["diabetes", "hypertension"]
    lifestyle_factors   = Column(JSON, default=dict)      # {smoking: bool, exercise: str}
    
    # Calculated fields
    recommended_life_coverage    = Column(Float, default=0.0)
    recommended_health_coverage  = Column(Float, default=0.0)
    current_life_coverage        = Column(Float, default=0.0)
    current_health_coverage      = Column(Float, default=0.0)
    coverage_gap_life            = Column(Float, default=0.0)
    coverage_gap_health          = Column(Float, default=0.0)
    risk_score                   = Column(Integer, default=50)  # 0-100
    risk_level                   = Column(String(20), default="moderate")  # low | moderate | high
    recommendations              = Column(JSON, default=list)
    
    created_at      = Column(DateTime, default=_now)
    updated_at      = Column(DateTime, default=_now, onupdate=_now)

    user = relationship("User", back_populates="insurance_assessments")
