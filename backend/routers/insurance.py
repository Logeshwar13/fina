"""
routers/insurance.py
────────────────────
Insurance management and risk assessment endpoints.
Handles health, life, vehicle, home, and travel insurance policies.
Includes intelligent risk calculator to assess coverage adequacy.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import List
from datetime import datetime, timezone

from database.db import get_supabase
from schemas.schemas import (
    InsurancePolicyCreate, InsurancePolicyUpdate, InsurancePolicyOut,
    InsuranceRiskAssessmentCreate, InsuranceRiskAssessmentOut
)

router = APIRouter(prefix="/insurance", tags=["insurance"])


# ── Insurance Policies ────────────────────────────────────────────────────────

@router.post("/policies", response_model=InsurancePolicyOut)
def create_policy(policy: InsurancePolicyCreate, sb: Client = Depends(get_supabase)):
    """Create a new insurance policy."""
    # Use mode='json' to automatically serialize datetime objects
    row = policy.model_dump(mode='json')
    row["id"] = str(uuid.uuid4())
    row["created_at"] = datetime.now(timezone.utc).isoformat()
    row["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    res = sb.table("insurance_policies").insert(row).execute()
    if not res.data:
        raise HTTPException(400, "Failed to create policy")
    return res.data[0]


@router.get("/policies/{user_id}", response_model=List[InsurancePolicyOut])
def get_user_policies(user_id: str, sb: Client = Depends(get_supabase)):
    """Get all insurance policies for a user."""
    res = sb.table("insurance_policies").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return res.data or []


@router.get("/policies/{user_id}/{policy_type}", response_model=List[InsurancePolicyOut])
def get_policies_by_type(user_id: str, policy_type: str, sb: Client = Depends(get_supabase)):
    """Get insurance policies by type (health, life, vehicle, home, travel)."""
    res = sb.table("insurance_policies").select("*").eq("user_id", user_id).eq("policy_type", policy_type).order("created_at", desc=True).execute()
    return res.data or []


@router.put("/policies/{policy_id}", response_model=InsurancePolicyOut)
def update_policy(policy_id: str, updates: InsurancePolicyUpdate, sb: Client = Depends(get_supabase)):
    """Update an insurance policy."""
    row = updates.model_dump(exclude_unset=True, mode='json')
    row["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    res = sb.table("insurance_policies").update(row).eq("id", policy_id).execute()
    if not res.data:
        raise HTTPException(404, "Policy not found")
    return res.data[0]


@router.delete("/policies/{policy_id}")
def delete_policy(policy_id: str, sb: Client = Depends(get_supabase)):
    """Delete an insurance policy."""
    res = sb.table("insurance_policies").delete().eq("id", policy_id).execute()
    if not res.data:
        raise HTTPException(404, "Policy not found")
    return {"message": "Policy deleted successfully"}


# ── Risk Assessment & Calculator ──────────────────────────────────────────────

def calculate_insurance_needs(assessment_data: InsuranceRiskAssessmentCreate, sb: Client):
    """
    Calculate recommended insurance coverage based on user profile.
    
    Life Insurance Formula:
    - Base: 10-15x annual income
    - Add: Outstanding loans
    - Add: Future expenses (education, marriage) = dependents * 500,000
    - Adjust for age and health
    
    Health Insurance Formula:
    - Base: 5-10 lakh minimum
    - Add: Age factor (50k per year after 30)
    - Add: Dependents (3 lakh per dependent)
    - Add: Health conditions (2 lakh per condition)
    - Multiply by city tier (metro = 1.5x)
    """
    
    # Life Insurance Calculation
    base_life_coverage = assessment_data.annual_income * 12  # 12x annual income
    
    # Add loans
    life_coverage = base_life_coverage + assessment_data.existing_loans
    
    # Add dependent expenses (education, marriage, etc.)
    dependent_factor = assessment_data.dependents * 500000  # 5 lakh per dependent
    life_coverage += dependent_factor
    
    # Age adjustment (reduce for older age as earning years decrease)
    age_factor = 1.0
    if assessment_data.age > 50:
        age_factor = 0.7
    elif assessment_data.age > 40:
        age_factor = 0.85
    elif assessment_data.age < 30:
        age_factor = 1.2
    
    life_coverage *= age_factor
    
    # Health Insurance Calculation
    base_health_coverage = 500000  # 5 lakh base
    
    # Age factor
    if assessment_data.age > 30:
        age_years = assessment_data.age - 30
        base_health_coverage += age_years * 50000
    
    # Dependents
    base_health_coverage += assessment_data.dependents * 300000
    
    # Health conditions
    health_condition_count = len(assessment_data.health_conditions)
    base_health_coverage += health_condition_count * 200000
    
    # Lifestyle factors
    lifestyle = assessment_data.lifestyle_factors
    if lifestyle.get("smoking"):
        base_health_coverage *= 1.3
    if lifestyle.get("city_tier") == "metro":
        base_health_coverage *= 1.5
    
    # Get current coverage
    policies_res = sb.table("insurance_policies").select("*").eq("user_id", assessment_data.user_id).eq("status", "active").execute()
    policies = policies_res.data or []
    
    current_life = sum(p["coverage_amount"] for p in policies if p["policy_type"] == "life")
    current_health = sum(p["coverage_amount"] for p in policies if p["policy_type"] == "health")
    
    # Calculate gaps
    life_gap = max(0, life_coverage - current_life)
    health_gap = max(0, base_health_coverage - current_health)
    
    # Risk scoring (0-100, higher = more risk)
    risk_score = 50  # baseline
    
    # Increase risk if coverage gaps exist
    if life_gap > life_coverage * 0.5:
        risk_score += 20
    elif life_gap > life_coverage * 0.25:
        risk_score += 10
    
    if health_gap > base_health_coverage * 0.5:
        risk_score += 20
    elif health_gap > base_health_coverage * 0.25:
        risk_score += 10
    
    # Adjust for health conditions
    risk_score += min(20, health_condition_count * 5)
    
    # Adjust for dependents without coverage
    if assessment_data.dependents > 0 and current_life < assessment_data.annual_income * 5:
        risk_score += 15
    
    # Cap at 100
    risk_score = min(100, risk_score)
    
    # Determine risk level
    if risk_score < 40:
        risk_level = "low"
    elif risk_score < 70:
        risk_level = "moderate"
    else:
        risk_level = "high"
    
    # Generate recommendations
    recommendations = []
    
    if life_gap > 0:
        recommendations.append(
            f"Increase life insurance coverage by ₹{life_gap:,.0f} to adequately protect your dependents."
        )
    else:
        recommendations.append("Your life insurance coverage is adequate for your current needs.")
    
    if health_gap > 0:
        recommendations.append(
            f"Increase health insurance coverage by ₹{health_gap:,.0f} to cover potential medical expenses."
        )
    else:
        recommendations.append("Your health insurance coverage meets recommended levels.")
    
    if assessment_data.dependents > 0 and current_life == 0:
        recommendations.append(
            "Critical: You have dependents but no life insurance. Consider getting term insurance immediately."
        )
    
    if health_condition_count > 0 and current_health < 500000:
        recommendations.append(
            "With existing health conditions, consider increasing health coverage to at least ₹5 lakhs."
        )
    
    if assessment_data.age > 45 and current_health < 1000000:
        recommendations.append(
            "At your age, medical expenses tend to increase. Consider coverage of at least ₹10 lakhs."
        )
    
    # Check for expiring policies
    expiring_soon = [p for p in policies if (datetime.fromisoformat(p["end_date"].replace('Z', '+00:00')) - datetime.now(timezone.utc)).days < 60]
    if expiring_soon:
        recommendations.append(
            f"You have {len(expiring_soon)} policy/policies expiring within 60 days. Renew them to avoid coverage gaps."
        )
    
    return {
        "recommended_life_coverage": round(life_coverage, 2),
        "recommended_health_coverage": round(base_health_coverage, 2),
        "current_life_coverage": round(current_life, 2),
        "current_health_coverage": round(current_health, 2),
        "coverage_gap_life": round(life_gap, 2),
        "coverage_gap_health": round(health_gap, 2),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommendations": recommendations
    }


@router.post("/assessment", response_model=InsuranceRiskAssessmentOut)
def create_assessment(assessment: InsuranceRiskAssessmentCreate, sb: Client = Depends(get_supabase)):
    """
    Create insurance risk assessment and calculate recommended coverage.
    Returns personalized recommendations based on user profile.
    """
    # Calculate insurance needs
    calculated = calculate_insurance_needs(assessment, sb)
    
    # Create assessment record
    row = assessment.model_dump(mode='json')
    row.update(calculated)
    row["id"] = str(uuid.uuid4())
    row["created_at"] = datetime.now(timezone.utc).isoformat()
    row["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    res = sb.table("insurance_risk_assessments").insert(row).execute()
    if not res.data:
        raise HTTPException(400, "Failed to create assessment")
    return res.data[0]


@router.get("/assessment/{user_id}/latest", response_model=InsuranceRiskAssessmentOut)
def get_latest_assessment(user_id: str, sb: Client = Depends(get_supabase)):
    """Get the most recent insurance risk assessment for a user."""
    res = sb.table("insurance_risk_assessments").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="No assessment found for this user")
    
    return res.data[0]


@router.get("/assessment/{user_id}/history", response_model=List[InsuranceRiskAssessmentOut])
def get_assessment_history(user_id: str, sb: Client = Depends(get_supabase)):
    """Get all insurance risk assessments for a user."""
    res = sb.table("insurance_risk_assessments").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return res.data or []


@router.get("/dashboard/{user_id}")
def get_insurance_dashboard(user_id: str, sb: Client = Depends(get_supabase)):
    """
    Get comprehensive insurance dashboard with policies, coverage summary, and recommendations.
    """
    # Get all policies
    policies_res = sb.table("insurance_policies").select("*").eq("user_id", user_id).execute()
    policies = policies_res.data or []
    
    # Get latest assessment
    assessment_res = sb.table("insurance_risk_assessments").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
    assessment = assessment_res.data[0] if assessment_res.data else None
    
    # Calculate total premiums
    annual_premium = 0
    for p in policies:
        if p["status"] == "active":
            if p["premium_frequency"] == "annual":
                annual_premium += p["premium_amount"]
            elif p["premium_frequency"] == "monthly":
                annual_premium += p["premium_amount"] * 12
            else:  # quarterly
                annual_premium += p["premium_amount"] * 4
    
    # Group by type
    by_type = {}
    for policy in policies:
        policy_type = policy["policy_type"]
        if policy_type not in by_type:
            by_type[policy_type] = {
                "count": 0,
                "total_coverage": 0,
                "total_premium": 0,
                "policies": []
            }
        
        premium = policy["premium_amount"]
        if policy["premium_frequency"] == "monthly":
            premium *= 12
        elif policy["premium_frequency"] == "quarterly":
            premium *= 4
        
        by_type[policy_type]["count"] += 1
        by_type[policy_type]["total_coverage"] += policy["coverage_amount"]
        by_type[policy_type]["total_premium"] += premium
        by_type[policy_type]["policies"].append({
            "id": policy["id"],
            "provider": policy["provider"],
            "coverage": policy["coverage_amount"],
            "premium": premium,
            "end_date": policy["end_date"]
        })
    
    # Find expiring policies
    expiring_soon = []
    for p in policies:
        if p["status"] == "active":
            end_date = datetime.fromisoformat(p["end_date"].replace('Z', '+00:00'))
            days_remaining = (end_date - datetime.now(timezone.utc)).days
            if days_remaining < 60:
                expiring_soon.append({
                    "id": p["id"],
                    "type": p["policy_type"],
                    "provider": p["provider"],
                    "end_date": p["end_date"],
                    "days_remaining": days_remaining
                })
    
    return {
        "user_id": user_id,
        "total_policies": len(policies),
        "active_policies": len([p for p in policies if p["status"] == "active"]),
        "total_coverage": sum(p["coverage_amount"] for p in policies if p["status"] == "active"),
        "annual_premium": round(annual_premium, 2),
        "by_type": by_type,
        "assessment": assessment,
        "expiring_soon": expiring_soon
    }
