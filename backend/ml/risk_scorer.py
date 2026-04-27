"""
ml/risk_scorer.py
─────────────────
Composite financial risk scoring.

Score (0–100) built from 5 weighted sub-scores:
  1. Savings Rate          (25%) — income vs. expenses
  2. Debt / Budget ratio   (20%) — how often budgets are exceeded
  3. Spending Consistency  (20%) — stddev of monthly spending
  4. Fraud Exposure        (20%) — flagged transaction ratio
  5. Emergency Fund Proxy  (15%) — months of expenses covered by balance

Grade mapping:
  90-100 → A (Excellent)
  75-89  → B (Good)
  60-74  → C (Average)
  40-59  → D (At Risk)
   0-39  → F (Poor)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Tuple


GRADE_TABLE = [(90, "A", "Excellent"), (75, "B", "Good"),
               (60, "C", "Average"),  (40, "D", "At Risk"), (0, "F", "Poor")]

WEIGHTS = {
    "Savings Rate":         0.25,
    "Budget Adherence":     0.20,
    "Spending Consistency": 0.20,
    "Fraud Exposure":       0.20,
    "Emergency Fund":       0.15,
}


@dataclass
class RiskInput:
    monthly_income:    float
    monthly_expenses:  float
    balance:           float             = 0.0
    total_transactions: int              = 0
    fraud_count:       int               = 0
    budget_overruns:   int               = 0
    total_budgets:     int               = 1
    monthly_amounts:   List[float]       = field(default_factory=list)   # last 6 months


def _savings_rate_score(income: float, expenses: float) -> float:
    """Higher savings rate → higher score."""
    if income <= 0:
        return 50.0
    rate = max(0.0, (income - expenses) / income)
    # 0% savings → 0, 20% → 60, 40%+ → 100
    return float(min(100.0, rate * 250))


def _budget_adherence_score(overruns: int, total_budgets: int) -> float:
    """0 overruns → 100, every overrun costs points."""
    if total_budgets <= 0:
        return 70.0
    adherence = 1 - (overruns / max(1, total_budgets))
    return float(max(0.0, adherence * 100))


def _spending_consistency_score(monthly_amounts: List[float]) -> float:
    """Low standard deviation relative to mean → more consistent → higher score."""
    if len(monthly_amounts) < 2:
        return 70.0
    import statistics
    mean = statistics.mean(monthly_amounts)
    stdev = statistics.stdev(monthly_amounts)
    if mean == 0:
        return 70.0
    cv = stdev / mean          # coefficient of variation
    # cv close to 0 → score 100; cv ≥ 1 → score 0
    return float(max(0.0, min(100.0, (1 - cv) * 100)))


def _fraud_exposure_score(fraud_count: int, total_transactions: int) -> float:
    """Fewer fraudulent transactions → better score."""
    if total_transactions <= 0:
        return 80.0
    ratio = fraud_count / total_transactions
    # 0% fraud → 100, 5%+ → 0
    return float(max(0.0, min(100.0, (1 - ratio * 20) * 100)))


def _emergency_fund_score(balance: float, monthly_expenses: float) -> float:
    """Target: 6 months of expenses in reserve."""
    if monthly_expenses <= 0:
        return 50.0
    months_covered = balance / monthly_expenses
    # 0 months → 0, 3 months → 50, 6+ months → 100
    return float(min(100.0, (months_covered / 6) * 100))


def compute_risk_score(data: RiskInput) -> Tuple[int, str, str, Dict[str, float]]:
    """
    Returns (score, grade, label, breakdown_dict).
    breakdown_dict maps sub-category → sub-score (0-100).
    """
    sub_scores = {
        "Savings Rate":         _savings_rate_score(data.monthly_income, data.monthly_expenses),
        "Budget Adherence":     _budget_adherence_score(data.budget_overruns, data.total_budgets),
        "Spending Consistency": _spending_consistency_score(data.monthly_amounts),
        "Fraud Exposure":       _fraud_exposure_score(data.fraud_count, data.total_transactions),
        "Emergency Fund":       _emergency_fund_score(data.balance, data.monthly_expenses),
    }

    # Weighted composite
    composite = sum(sub_scores[k] * WEIGHTS[k] for k in sub_scores)
    score = int(round(composite))

    grade, label = "F", "Poor"
    for threshold, g, l in GRADE_TABLE:
        if score >= threshold:
            grade, label = g, l
            break

    return score, grade, label, sub_scores
