"""
Simple AI Chat Router - Direct Database Access
This works like your old chatbot - fetches data directly and formats it.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from database.db import get_supabase
from mcp.model import ModelLayer

router = APIRouter(prefix="/ai", tags=["Simple AI Chat"])

class SimpleChatRequest(BaseModel):
    query: str
    user_id: str

class SimpleChatResponse(BaseModel):
    response: str
    data_used: dict
    success: bool
    execution_time: float

@router.post("/simple-chat", response_model=SimpleChatResponse)
async def simple_chat(request: SimpleChatRequest):
    """
    Simple AI chat that directly accesses database and shows real data.
    Like your old chatbot - no complex agent system.
    """
    import time
    start_time = time.time()
    
    query_lower = request.query.lower()
    user_id = request.user_id
    sb = get_supabase()
    
    # Collect data based on query
    data_parts = []
    data_used = {}
    
    try:
        # 1. TRANSACTIONS
        if any(word in query_lower for word in ['transaction', 'spending', 'spent', 'expense', 'food', 'dining', 'last', 'recent', 'show']):
            # Get transactions
            query_builder = sb.table("transactions").select("*").eq("user_id", user_id)
            
            # Filter by category if specified
            if 'food' in query_lower or 'dining' in query_lower:
                query_builder = query_builder.eq("category", "Food & Dining")
            
            # Order and limit
            transactions = query_builder.order("timestamp", desc=True).limit(20).execute()
            
            if transactions.data:
                data_used['transactions'] = transactions.data
                data_parts.append(f"\n📊 TRANSACTIONS ({len(transactions.data)} found):\n")
                
                total = 0
                for i, txn in enumerate(transactions.data, 1):
                    amount = txn.get('amount', 0)
                    desc = txn.get('description', 'N/A')
                    category = txn.get('category', 'N/A')
                    timestamp = txn.get('timestamp', '')[:10]
                    location = txn.get('location', 'N/A')
                    txn_type = txn.get('type', 'expense')
                    
                    data_parts.append(
                        f"{i}. ₹{amount} - {desc} - {timestamp}\n"
                        f"   Category: {category}, Location: {location}, Type: {txn_type}"
                    )
                    total += amount
                
                data_parts.append(f"\n💰 Total: ₹{total}")
        
        # 2. BUDGETS
        if 'budget' in query_lower:
            budgets = sb.table("budgets").select("*").eq("user_id", user_id).execute()
            
            if budgets.data:
                data_used['budgets'] = budgets.data
                data_parts.append(f"\n\n📋 BUDGETS ({len(budgets.data)} found):\n")
                
                for i, budget in enumerate(budgets.data, 1):
                    category = budget.get('category', 'N/A')
                    limit = budget.get('limit_amount', budget.get('limit', 0))
                    period = budget.get('period', 'monthly')
                    
                    # Calculate spent (get transactions for this category)
                    cat_txns = sb.table("transactions").select("amount").eq("user_id", user_id).eq("category", category).eq("type", "expense").execute()
                    spent = sum(t.get('amount', 0) for t in cat_txns.data)
                    remaining = limit - spent
                    percentage = (spent / limit * 100) if limit > 0 else 0
                    
                    status = "🔴 Over" if spent > limit else "🟡 Warning" if percentage > 80 else "🟢 Good"
                    
                    data_parts.append(
                        f"{i}. {category}: ₹{limit}/{period}\n"
                        f"   Spent: ₹{spent}, Remaining: ₹{remaining} ({percentage:.1f}% used) {status}"
                    )
        
        # 3. FRAUD CHECK
        if 'fraud' in query_lower or 'suspicious' in query_lower:
            fraud_txns = sb.table("transactions").select("*").eq("user_id", user_id).eq("is_fraud", True).execute()
            
            data_used['fraud_transactions'] = fraud_txns.data
            data_parts.append(f"\n\n⚠️ FRAUD ALERTS ({len(fraud_txns.data)} found):\n")
            
            if fraud_txns.data:
                for i, txn in enumerate(fraud_txns.data, 1):
                    amount = txn.get('amount', 0)
                    desc = txn.get('description', 'N/A')
                    timestamp = txn.get('timestamp', '')[:10]
                    fraud_score = txn.get('fraud_score', 0)
                    
                    data_parts.append(
                        f"{i}. ₹{amount} - {desc} - {timestamp}\n"
                        f"   Fraud Score: {fraud_score}, ID: {txn.get('id')}"
                    )
            else:
                data_parts.append("✅ No fraudulent transactions detected!")
        
        # 4. RISK SCORE
        if 'risk' in query_lower or 'score' in query_lower:
            # Calculate simple risk score
            all_txns = sb.table("transactions").select("*").eq("user_id", user_id).execute()
            budgets = sb.table("budgets").select("*").eq("user_id", user_id).execute()
            
            total_expenses = sum(t.get('amount', 0) for t in all_txns.data if t.get('type') == 'expense')
            total_income = sum(t.get('amount', 0) for t in all_txns.data if t.get('type') == 'income')
            
            risk_score = 50  # Base score
            if total_income > 0:
                expense_ratio = total_expenses / total_income
                if expense_ratio > 0.9:
                    risk_score = 75
                elif expense_ratio > 0.7:
                    risk_score = 60
                else:
                    risk_score = 40
            
            data_used['risk_score'] = risk_score
            data_parts.append(f"\n\n📈 RISK SCORE: {risk_score}/100\n")
            data_parts.append(f"Total Income: ₹{total_income}\n")
            data_parts.append(f"Total Expenses: ₹{total_expenses}\n")
            data_parts.append(f"Savings: ₹{total_income - total_expenses}")
        
        # 5. CREATE BUDGET (Action)
        if 'create budget' in query_lower or 'add budget' in query_lower:
            # Extract category and amount from query (simple parsing)
            # This is a placeholder - in real implementation, use LLM to extract params
            data_parts.append("\n\n✅ To create a budget, please specify:\n")
            data_parts.append("- Category (e.g., Food & Dining, Transportation)\n")
            data_parts.append("- Limit amount (e.g., ₹5000)\n")
            data_parts.append("- Period (monthly/weekly/yearly)\n")
            data_parts.append("\nExample: 'Create a budget for Food & Dining with ₹5000 monthly limit'")
        
        # Combine all data
        if not data_parts:
            data_text = "I couldn't find specific data for your query. Please ask about transactions, budgets, fraud, or risk score."
        else:
            data_text = "\n".join(data_parts)
        
        # Use LLM to make response conversational
        model = ModelLayer()
        
        llm_prompt = f"""User asked: "{request.query}"

Here is their ACTUAL DATA from the database:
{data_text}

Provide a helpful, conversational response that:
1. Uses the ACTUAL DATA above (amounts, dates, descriptions)
2. Answers their specific question
3. Provides actionable insights
4. Is friendly and clear

IMPORTANT: Use the real data shown above. Don't say "I don't have access" - the data is right there!"""
        
        response = await model.generate(
            messages=[
                {"role": "system", "content": "You are a helpful financial advisor. Use the actual data provided to answer questions. Always reference specific amounts, dates, and details from the data."},
                {"role": "user", "content": llm_prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        execution_time = time.time() - start_time
        
        return SimpleChatResponse(
            response=response["content"],
            data_used={"summary": f"Used {len(data_used)} data sources"},
            success=True,
            execution_time=execution_time
        )
    
    except Exception as e:
        execution_time = time.time() - start_time
        return SimpleChatResponse(
            response=f"Error: {str(e)}",
            data_used={},
            success=False,
            execution_time=execution_time
        )


@router.post("/create-budget-action")
async def create_budget_action(
    user_id: str,
    category: str,
    limit_amount: float,
    period: str = "monthly"
):
    """Create a budget directly"""
    sb = get_supabase()
    
    try:
        result = sb.table("budgets").insert({
            "user_id": user_id,
            "category": category,
            "limit_amount": limit_amount,
            "period": period,
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        
        return {
            "success": True,
            "message": f"✅ Budget created: {category} - ₹{limit_amount}/{period}",
            "budget": result.data[0] if result.data else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/flag-transaction-action")
async def flag_transaction_action(
    transaction_id: str,
    is_fraud: bool
):
    """Flag a transaction as safe or fraudulent"""
    sb = get_supabase()
    
    try:
        result = sb.table("transactions").update({
            "is_fraud": is_fraud
        }).eq("id", transaction_id).execute()
        
        status = "fraudulent" if is_fraud else "safe"
        return {
            "success": True,
            "message": f"✅ Transaction marked as {status}",
            "transaction": result.data[0] if result.data else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
