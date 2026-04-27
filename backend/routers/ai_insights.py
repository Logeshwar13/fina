"""
routers/ai_insights.py  — Groq LLM-powered financial insights
"""
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase import Client
from database.db import get_supabase

router = APIRouter(prefix="/ai-insights", tags=["AI Insights"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

class AIInsightRequest(BaseModel):
    user_id: str
    context: str = ""   # optional extra context from frontend

@router.post("/insights")
async def groq_insights(body: AIInsightRequest, sb: Client = Depends(get_supabase)):
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    if not groq_api_key:
        raise HTTPException(503, "GROQ_API_KEY not configured")

    # Pull user data for context
    user_res = sb.table("users").select("*").eq("id", body.user_id).execute()
    if not user_res.data:
        raise HTTPException(404, "User not found")
    user = user_res.data[0]

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0).isoformat()

    txns = sb.table("transactions").select("*").eq("user_id", body.user_id).execute().data or []
    this_month = [t for t in txns if t.get("type") == "expense" and (t.get("timestamp","")) >= month_start]
    income  = user.get("income", 0)
    spent   = sum(t["amount"] for t in this_month)
    savings = max(0, income - spent)
    fraud_n = sum(1 for t in txns if t.get("is_fraud"))
    budgets = sb.table("budgets").select("*").eq("user_id", body.user_id).execute().data or []

    cat_totals: dict = {}
    for t in this_month:
        cat_totals[t["category"]] = cat_totals.get(t["category"], 0) + t["amount"]
    top_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)[:3]

    # Get insurance data for insights
    insurance_policies = sb.table("insurance_policies").select("*").eq("user_id", body.user_id).execute().data or []
    insurance_assessments = sb.table("insurance_risk_assessments").select("*").eq("user_id", body.user_id).order("created_at", desc=True).limit(1).execute().data or []
    
    # Calculate insurance metrics
    total_coverage = sum(p.get('coverage_amount', 0) for p in insurance_policies)
    total_annual_premium = 0
    expiring_soon = 0
    
    for policy in insurance_policies:
        premium = policy.get('premium_amount', 0)
        frequency = policy.get('premium_frequency', 'annual')
        if frequency == 'monthly':
            total_annual_premium += premium * 12
        elif frequency == 'quarterly':
            total_annual_premium += premium * 4
        else:
            total_annual_premium += premium
            
        # Check expiry
        try:
            end_date = datetime.fromisoformat(policy.get('end_date', '').replace('Z', '+00:00'))
            days_left = (end_date - datetime.now(timezone.utc)).days
            if 0 < days_left <= 60:
                expiring_soon += 1
        except:
            pass
    
    # Insurance assessment data
    assessment_data = ""
    if insurance_assessments:
        assessment = insurance_assessments[0]
        life_gap = assessment.get('coverage_gap_life', 0)
        health_gap = assessment.get('coverage_gap_health', 0)
        risk_score = assessment.get('risk_score', 50)
        assessment_data = f"Insurance risk score: {risk_score}/100, Life coverage gap: ₹{life_gap:,.0f}, Health coverage gap: ₹{health_gap:,.0f}"

    prompt = f"""You are a concise personal finance advisor AI with insurance expertise.

User profile:
- Monthly income: ₹{income:,.0f}
- This month's expenses: ₹{spent:,.0f}
- Savings this month: ₹{savings:,.0f}
- Savings rate: {(savings/income*100) if income else 0:.0f}%
- Fraud flags: {fraud_n}
- Top spending categories: {', '.join(f'{c} ₹{a:,.0f}' for c,a in top_cats) or 'No data'}
- Active budgets: {len(budgets)}
- Insurance policies: {len(insurance_policies)}
- Total insurance coverage: ₹{total_coverage:,.0f}
- Annual insurance premiums: ₹{total_annual_premium:,.0f}
- Policies expiring soon: {expiring_soon}
{assessment_data}
{body.context}

Give 3 short, actionable and personalized financial insights for this user. Include insurance-related insights when relevant (coverage gaps, expiring policies, premium optimization, etc.).
Format as a JSON array of objects with keys: "icon" (emoji), "title" (short), "message" (1-2 sentences), "type" (positive/warning/info).
Only return the JSON array, nothing else."""

    from groq import Groq
    import json
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_completion_tokens=512,
        stream=False,
    )
    raw = completion.choices[0].message.content.strip()
    # Extract JSON array
    start = raw.find("[")
    end   = raw.rfind("]") + 1
    insights = json.loads(raw[start:end]) if start != -1 else []
    return {"insights": insights, "powered_by": "Groq llama-3.3-70b"}


# ── AI Chat endpoint ─────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    user_id: str
    message: str
    history: list = []   # [{"role":"user"|"assistant","content":"..."}]

@router.post("/chat")
async def groq_chat(body: ChatRequest, sb: Client = Depends(get_supabase)):
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    if not groq_api_key:
        raise HTTPException(503, "GROQ_API_KEY not configured")

    user_res = sb.table("users").select("*").eq("id", body.user_id).execute()
    user = user_res.data[0] if user_res.data else {}
    income = user.get("income", 0)

    # Get transaction data
    txns = sb.table("transactions").select("*").eq("user_id", body.user_id).execute().data or []
    total_exp = sum(t["amount"] for t in txns if t.get("type") == "expense")
    total_inc = sum(t["amount"] for t in txns if t.get("type") == "income")
    
    cat_totals = {}
    for t in txns:
        if t.get("type") == "expense":
            cat = t.get("category") or "Other"
            cat_totals[cat] = cat_totals.get(cat, 0) + float(t["amount"])
            
    cat_str = ", ".join(f"{k}: ₹{v:,.0f}" for k, v in cat_totals.items())

    recent_txns = sorted(txns, key=lambda x: x.get("timestamp", ""), reverse=True)[:50]
    txns_str = "\n".join([f"- {t.get('timestamp','')} | {t.get('description', 'Item')} ({t.get('category','Other')}) -> {t.get('type')} ₹{t.get('amount')}" for t in recent_txns])
    if not txns_str:
        txns_str = "No recent transactions found."

    # Get insurance data
    insurance_policies = sb.table("insurance_policies").select("*").eq("user_id", body.user_id).execute().data or []
    insurance_assessments = sb.table("insurance_risk_assessments").select("*").eq("user_id", body.user_id).order("created_at", desc=True).limit(1).execute().data or []
    
    # Format insurance policies
    if insurance_policies:
        policies_by_type = {}
        total_coverage = 0
        total_annual_premium = 0
        
        for policy in insurance_policies:
            policy_type = policy.get('policy_type', 'Unknown')
            if policy_type not in policies_by_type:
                policies_by_type[policy_type] = []
            
            # Calculate annual premium
            premium = policy.get('premium_amount', 0)
            frequency = policy.get('premium_frequency', 'annual')
            if frequency == 'monthly':
                annual_premium = premium * 12
            elif frequency == 'quarterly':
                annual_premium = premium * 4
            else:
                annual_premium = premium
            
            total_coverage += policy.get('coverage_amount', 0)
            total_annual_premium += annual_premium
            
            # Calculate days until expiry
            from datetime import datetime, timezone
            try:
                end_date = datetime.fromisoformat(policy.get('end_date', '').replace('Z', '+00:00'))
                days_left = (end_date - datetime.now(timezone.utc)).days
                status = "Active" if days_left > 30 else "Expiring Soon" if days_left > 0 else "Expired"
            except:
                days_left = 0
                status = "Unknown"
            
            policies_by_type[policy_type].append({
                'provider': policy.get('provider', 'Unknown'),
                'policy_number': policy.get('policy_number', 'N/A'),
                'coverage': policy.get('coverage_amount', 0),
                'premium': annual_premium,
                'status': status,
                'days_left': days_left,
                'notes': policy.get('notes', '')
            })
        
        insurance_str = f"Total Insurance Coverage: ₹{total_coverage:,.0f}, Annual Premiums: ₹{total_annual_premium:,.0f}\n"
        for policy_type, policies in policies_by_type.items():
            insurance_str += f"\n{policy_type.title()} Insurance:\n"
            for policy in policies:
                insurance_str += f"  - {policy['provider']} (#{policy['policy_number'][:8]}...): ₹{policy['coverage']:,.0f} coverage, ₹{policy['premium']:,.0f}/year, {policy['status']}"
                if policy['days_left'] > 0:
                    insurance_str += f" ({policy['days_left']} days left)"
                if policy['notes']:
                    insurance_str += f" | Notes: {policy['notes'][:50]}..."
                insurance_str += "\n"
    else:
        insurance_str = "No insurance policies found. User should consider getting health and life insurance."
    
    # Format insurance assessment
    assessment_str = ""
    if insurance_assessments:
        assessment = insurance_assessments[0]
        assessment_str = f"""
Latest Insurance Risk Assessment:
- Risk Score: {assessment.get('risk_score', 'N/A')}/100 ({assessment.get('risk_level', 'Unknown')} risk)
- Recommended Life Coverage: ₹{assessment.get('recommended_life_coverage', 0):,.0f}
- Recommended Health Coverage: ₹{assessment.get('recommended_health_coverage', 0):,.0f}
- Current Life Coverage: ₹{assessment.get('current_life_coverage', 0):,.0f}
- Current Health Coverage: ₹{assessment.get('current_health_coverage', 0):,.0f}
- Life Coverage Gap: ₹{assessment.get('coverage_gap_life', 0):,.0f}
- Health Coverage Gap: ₹{assessment.get('coverage_gap_health', 0):,.0f}
- Age: {assessment.get('age', 'N/A')}, Dependents: {assessment.get('dependents', 0)}
- Annual Income: ₹{assessment.get('annual_income', 0):,.0f}
- Existing Loans: ₹{assessment.get('existing_loans', 0):,.0f}
- Health Conditions: {', '.join(assessment.get('health_conditions', [])) or 'None reported'}"""
    else:
        assessment_str = "No insurance risk assessment found. Recommend user to complete insurance needs assessment."

    system = f"""You are FinA AI, a comprehensive personal financial advisor with expertise in insurance planning. 
You act as a RAG (Retrieval-Augmented Generation) system with access to complete financial and insurance data.

User profile: name={user.get('name','User')}, monthly_income=₹{income:,.0f}, total_expenses=₹{total_exp:,.0f}, total_income=₹{total_inc:,.0f}, transaction_count={len(txns)}.
Expense breakdown by category: {cat_str}

Recent Transactions (RAG Context):
{txns_str}

Insurance Portfolio (RAG Context):
{insurance_str}

{assessment_str}

CRITICAL RULES:
1. STRICT DOMAIN: You MUST ONLY answer questions related to personal finance, budgeting, expenses, investments, and INSURANCE (health, life, vehicle, home, travel insurance). 
2. If asked ANYTHING outside of finance, investments, or insurance, firmly reply: "I am a financial advisor. I only assist with finance, investment, and insurance questions."
3. INSURANCE EXPERTISE: You are now an expert in insurance planning. Use the insurance data above to:
   - Analyze coverage gaps and recommend improvements
   - Explain policy details, premiums, and coverage amounts
   - Suggest optimal insurance strategies based on user's profile
   - Alert about expiring policies and renewal needs
   - Compare different insurance types and their benefits
4. RAG DATA USAGE: Use the transaction, insurance, and assessment data above to provide precise, data-driven answers.
5. INSURANCE RECOMMENDATIONS: When discussing insurance:
   - Reference specific coverage gaps from assessments
   - Mention current policies and their adequacy
   - Suggest improvements based on age, dependents, income, and risk factors
   - Explain insurance terminology clearly
6. FORMATTING: ALWAYS format answers as bullet points or numbered lists. Use clear sections for different topics.
7. Use ₹ for currency. Keep responses professional, structured, and actionable.

INSURANCE KNOWLEDGE BASE:
- Health Insurance: Covers medical expenses, hospitalization. Recommended: ₹5-10 lakhs minimum, higher for metros
- Life Insurance: Financial protection for dependents. Recommended: 10-15x annual income
- Vehicle Insurance: Mandatory comprehensive coverage for vehicles
- Home Insurance: Protects property and belongings
- Travel Insurance: Coverage for trips and emergencies abroad

When users ask about insurance, provide specific recommendations based on their data above."""

    from groq import Groq
    client = Groq(api_key=groq_api_key)
    messages = [{"role": "system", "content": system}]
    for h in (body.history or [])[-6:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": body.message})

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        stream=False
    )
    
    reply = completion.choices[0].message.content.strip()
    return {"reply": reply, "model": "llama-3.3-70b"}

