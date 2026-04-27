"""
MCP Tools
=========
Tool definitions for all financial operations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from .protocol import tool_registry, ToolType
from database.db import get_supabase


# ============================================================================
# TRANSACTION TOOLS
# ============================================================================

@tool_registry.register(
    name="get_transactions",
    description="Fetch user's financial transactions with optional filters",
    category=ToolType.TRANSACTION,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of transactions to return",
                "default": 50
            },
            "transaction_type": {
                "type": "string",
                "enum": ["expense", "income", "all"],
                "description": "Filter by transaction type",
                "default": "all"
            },
            "category": {
                "type": "string",
                "description": "Filter by category (optional)"
            },
            "start_date": {
                "type": "string",
                "description": "Start date in ISO format (optional)"
            },
            "end_date": {
                "type": "string",
                "description": "End date in ISO format (optional)"
            }
        },
        "required": ["user_id"]
    }
)
async def get_transactions(
    user_id: str,
    limit: int = 50,
    transaction_type: str = "all",
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Fetch transactions with filters."""
    sb = get_supabase()
    
    query = sb.table("transactions").select("*").eq("user_id", user_id)
    
    if transaction_type != "all":
        query = query.eq("type", transaction_type)
    
    if category:
        query = query.eq("category", category)
    
    if start_date:
        query = query.gte("timestamp", start_date)
    
    if end_date:
        query = query.lte("timestamp", end_date)
    
    query = query.order("timestamp", desc=True).limit(limit)
    
    result = query.execute()
    
    return {
        "transactions": result.data,
        "count": len(result.data),
        "filters_applied": {
            "type": transaction_type,
            "category": category,
            "date_range": f"{start_date or 'any'} to {end_date or 'any'}"
        }
    }


@tool_registry.register(
    name="get_transaction_stats",
    description="Get statistical summary of user's transactions",
    category=ToolType.TRANSACTION,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID"
            },
            "period": {
                "type": "string",
                "enum": ["week", "month", "quarter", "year", "all"],
                "description": "Time period for statistics",
                "default": "month"
            }
        },
        "required": ["user_id"]
    }
)
async def get_transaction_stats(user_id: str, period: str = "month") -> Dict[str, Any]:
    """Calculate transaction statistics."""
    sb = get_supabase()
    
    # Calculate date range
    now = datetime.now(timezone.utc)
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "quarter":
        start_date = now - timedelta(days=90)
    elif period == "year":
        start_date = now - timedelta(days=365)
    else:
        start_date = None
    
    query = sb.table("transactions").select("*").eq("user_id", user_id)
    if start_date:
        query = query.gte("timestamp", start_date.isoformat())
    
    transactions = query.execute().data
    
    # Calculate stats
    total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
    total_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
    balance = total_income - total_expenses
    
    # Category breakdown
    category_spending = {}
    for t in transactions:
        if t["type"] == "expense":
            cat = t.get("category", "Other")
            category_spending[cat] = category_spending.get(cat, 0) + t["amount"]
    
    return {
        "period": period,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "transaction_count": len(transactions),
        "category_breakdown": category_spending,
        "average_transaction": total_expenses / len([t for t in transactions if t["type"] == "expense"]) if transactions else 0
    }


# ============================================================================
# BUDGET TOOLS
# ============================================================================

@tool_registry.register(
    name="get_budgets",
    description="Fetch user's budget limits and spending status",
    category=ToolType.BUDGET,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID"
            }
        },
        "required": ["user_id"]
    }
)
async def get_budgets(user_id: str) -> Dict[str, Any]:
    """Fetch budgets with current spending."""
    sb = get_supabase()
    
    try:
        # Get budgets
        budgets = sb.table("budgets").select("*").eq("user_id", user_id).execute().data
        
        # Get current month transactions
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        transactions = sb.table("transactions").select("*").eq("user_id", user_id).eq("type", "expense").gte("timestamp", month_start.isoformat()).execute().data
        
        # Calculate spending per category
        spending = {}
        for t in transactions:
            cat = t.get("category", "Other")
            spending[cat] = spending.get(cat, 0) + t["amount"]
        
        # Combine budgets with spending
        budget_status = []
        for budget in budgets:
            cat = budget.get("category", "Unknown")
            # Handle both 'limit' and 'limit_amount' field names
            limit = budget.get("limit_amount") or budget.get("limit", 0)
            spent = spending.get(cat, 0)
            remaining = limit - spent
            percentage = (spent / limit * 100) if limit > 0 else 0
            
            budget_status.append({
                "category": cat,
                "limit": limit,
                "spent": spent,
                "remaining": remaining,
                "percentage_used": percentage,
                "status": "over_budget" if spent > limit else "warning" if percentage > 80 else "healthy"
            })
        
        return {
            "budgets": budget_status,
            "total_budget": sum(b.get("limit", 0) for b in budgets),
            "total_spent": sum(b["spent"] for b in budget_status),
            "month": now.strftime("%B %Y")
        }
    except Exception as e:
        # Return empty budgets if there's an error
        return {
            "budgets": [],
            "total_budget": 0,
            "total_spent": 0,
            "month": datetime.now(timezone.utc).strftime("%B %Y"),
            "error": str(e)
        }


@tool_registry.register(
    name="analyze_budget_trends",
    description="Analyze budget adherence trends over time",
    category=ToolType.BUDGET,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID"
            },
            "months": {
                "type": "integer",
                "description": "Number of months to analyze",
                "default": 3
            }
        },
        "required": ["user_id"]
    }
)
async def analyze_budget_trends(user_id: str, months: int = 3) -> Dict[str, Any]:
    """Analyze budget trends."""
    sb = get_supabase()
    
    budgets = sb.table("budgets").select("*").eq("user_id", user_id).execute().data
    
    # Get transactions for last N months
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=30 * months)
    
    transactions = sb.table("transactions").select("*").eq("user_id", user_id).eq("type", "expense").gte("timestamp", start_date.isoformat()).execute().data
    
    # Group by month and category
    monthly_spending = {}
    for t in transactions:
        t_date = datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00"))
        month_key = t_date.strftime("%Y-%m")
        cat = t.get("category", "Other")
        
        if month_key not in monthly_spending:
            monthly_spending[month_key] = {}
        
        monthly_spending[month_key][cat] = monthly_spending[month_key].get(cat, 0) + t["amount"]
    
    # Calculate trends
    trends = []
    for budget in budgets:
        cat = budget["category"]
        limit = budget["limit_amount"]
        
        monthly_data = []
        for month_key in sorted(monthly_spending.keys()):
            spent = monthly_spending[month_key].get(cat, 0)
            monthly_data.append({
                "month": month_key,
                "spent": spent,
                "limit": limit,
                "percentage": (spent / limit * 100) if limit > 0 else 0
            })
        
        trends.append({
            "category": cat,
            "monthly_data": monthly_data,
            "average_spending": sum(m["spent"] for m in monthly_data) / len(monthly_data) if monthly_data else 0,
            "trend": "increasing" if len(monthly_data) >= 2 and monthly_data[-1]["spent"] > monthly_data[0]["spent"] else "decreasing"
        })
    
    return {
        "trends": trends,
        "months_analyzed": months,
        "period": f"{start_date.strftime('%B %Y')} to {now.strftime('%B %Y')}"
    }


# ============================================================================
# RISK TOOLS
# ============================================================================

@tool_registry.register(
    name="get_risk_score",
    description="Get user's financial health risk score and breakdown",
    category=ToolType.RISK,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID"
            }
        },
        "required": ["user_id"]
    }
)
async def get_risk_score(user_id: str) -> Dict[str, Any]:
    """Get risk score."""
    from routers.risk import get_risk_score as calculate_risk
    from fastapi import Query
    
    sb = get_supabase()
    result = calculate_risk(user_id=user_id, sb=sb)
    
    return {
        "score": result["score"],
        "grade": result["grade"],
        "label": result["label"],
        "breakdown": result["breakdown"],
        "interpretation": {
            "A": "Excellent financial health",
            "B": "Good financial health",
            "C": "Average financial health",
            "D": "At risk - needs improvement",
            "F": "Poor financial health - urgent action needed"
        }.get(result["grade"], "Unknown")
    }


# ============================================================================
# FRAUD TOOLS
# ============================================================================

@tool_registry.register(
    name="get_fraud_alerts",
    description="Get flagged fraudulent transactions",
    category=ToolType.FRAUD,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of alerts",
                "default": 10
            }
        },
        "required": ["user_id"]
    }
)
async def get_fraud_alerts(user_id: str, limit: int = 10) -> Dict[str, Any]:
    """Get fraud alerts."""
    sb = get_supabase()
    
    fraudulent = sb.table("transactions").select("*").eq("user_id", user_id).eq("is_fraud", True).order("timestamp", desc=True).limit(limit).execute().data
    
    return {
        "fraud_count": len(fraudulent),
        "flagged_transactions": fraudulent,
        "total_amount_at_risk": sum(t["amount"] for t in fraudulent),
        "recommendation": "Review these transactions immediately and mark as safe if legitimate" if fraudulent else "No fraudulent transactions detected"
    }


# ============================================================================
# INSURANCE TOOLS
# ============================================================================

@tool_registry.register(
    name="get_insurance_policies",
    description="Get user's insurance policies",
    category=ToolType.INSURANCE,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID"
            }
        },
        "required": ["user_id"]
    }
)
async def get_insurance_policies(user_id: str) -> Dict[str, Any]:
    """Get insurance policies."""
    sb = get_supabase()
    
    policies = sb.table("insurance_policies").select("*").eq("user_id", user_id).execute().data
    
    # Calculate totals by type
    by_type = {}
    for p in policies:
        ptype = p["policy_type"]
        if ptype not in by_type:
            by_type[ptype] = {"count": 0, "total_coverage": 0, "total_premium": 0}
        
        by_type[ptype]["count"] += 1
        by_type[ptype]["total_coverage"] += p["coverage_amount"]
        by_type[ptype]["total_premium"] += p["premium_amount"]
    
    return {
        "policies": policies,
        "total_policies": len(policies),
        "by_type": by_type,
        "total_coverage": sum(p["coverage_amount"] for p in policies),
        "total_annual_premium": sum(p["premium_amount"] for p in policies if p.get("premium_frequency") == "annual")
    }


# ============================================================================
# ANALYTICS TOOLS
# ============================================================================

@tool_registry.register(
    name="get_spending_insights",
    description="Get AI-powered spending insights and recommendations",
    category=ToolType.ANALYTICS,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID"
            }
        },
        "required": ["user_id"]
    }
)
async def get_spending_insights(user_id: str) -> Dict[str, Any]:
    """Generate spending insights."""
    sb = get_supabase()
    
    # Get last 30 days transactions
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=30)
    
    transactions = sb.table("transactions").select("*").eq("user_id", user_id).eq("type", "expense").gte("timestamp", start_date.isoformat()).execute().data
    
    if not transactions:
        return {"insights": [], "message": "Not enough transaction data"}
    
    # Calculate insights
    total_spent = sum(t["amount"] for t in transactions)
    avg_transaction = total_spent / len(transactions)
    
    # Category analysis
    by_category = {}
    for t in transactions:
        cat = t.get("category", "Other")
        by_category[cat] = by_category.get(cat, 0) + t["amount"]
    
    top_category = max(by_category.items(), key=lambda x: x[1])
    
    insights = [
        {
            "type": "spending_summary",
            "message": f"You spent ₹{total_spent:,.0f} in the last 30 days across {len(transactions)} transactions"
        },
        {
            "type": "top_category",
            "message": f"Your highest spending category is {top_category[0]} at ₹{top_category[1]:,.0f} ({top_category[1]/total_spent*100:.1f}% of total)"
        },
        {
            "type": "average_transaction",
            "message": f"Your average transaction is ₹{avg_transaction:,.0f}"
        }
    ]
    
    return {
        "insights": insights,
        "period": "last_30_days",
        "total_spent": total_spent,
        "category_breakdown": by_category
    }


# ============================================================================
# DETAILED TRANSACTION TOOLS
# ============================================================================

@tool_registry.register(
    name="get_last_transaction",
    description="Get the most recent transaction for a user, optionally filtered by month",
    category=ToolType.TRANSACTION,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID"
            },
            "month": {
                "type": "string",
                "description": "Month in YYYY-MM format (optional, defaults to current month)"
            },
            "transaction_type": {
                "type": "string",
                "enum": ["expense", "income", "all"],
                "description": "Filter by transaction type",
                "default": "all"
            }
        },
        "required": ["user_id"]
    }
)
async def get_last_transaction(
    user_id: str,
    month: Optional[str] = None,
    transaction_type: str = "all"
) -> Dict[str, Any]:
    """Get the last/most recent transaction."""
    sb = get_supabase()
    
    # If no month specified, use current month
    if not month:
        now = datetime.now(timezone.utc)
        month = now.strftime("%Y-%m")
    
    # Parse month to get date range
    year, month_num = month.split("-")
    start_date = f"{year}-{month_num}-01T00:00:00Z"
    
    # Calculate end date (last day of month)
    if int(month_num) == 12:
        end_date = f"{int(year)+1}-01-01T00:00:00Z"
    else:
        end_date = f"{year}-{int(month_num)+1:02d}-01T00:00:00Z"
    
    query = sb.table("transactions").select("*").eq("user_id", user_id)
    
    if transaction_type != "all":
        query = query.eq("type", transaction_type)
    
    query = query.gte("timestamp", start_date).lt("timestamp", end_date)
    query = query.order("timestamp", desc=True).limit(1)
    
    result = query.execute()
    
    if result.data:
        transaction = result.data[0]
        return {
            "found": True,
            "transaction": transaction,
            "details": {
                "id": transaction.get("id"),
                "description": transaction.get("description"),
                "amount": transaction.get("amount"),
                "type": transaction.get("type"),
                "category": transaction.get("category"),
                "timestamp": transaction.get("timestamp"),
                "merchant": transaction.get("merchant", "N/A")
            },
            "month": month
        }
    else:
        return {
            "found": False,
            "message": f"No transactions found for {month}",
            "month": month
        }


@tool_registry.register(
    name="create_transaction",
    description="Create a new transaction (expense or income) for a user",
    category=ToolType.TRANSACTION,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID"
            },
            "amount": {
                "type": "number",
                "description": "Transaction amount (positive number)"
            },
            "type": {
                "type": "string",
                "enum": ["expense", "income"],
                "description": "Transaction type"
            },
            "category": {
                "type": "string",
                "description": "Transaction category (e.g., 'Investment', 'Gold', 'Stocks', 'Savings')"
            },
            "description": {
                "type": "string",
                "description": "Transaction description"
            },
            "location": {
                "type": "string",
                "description": "Transaction location (optional)"
            }
        },
        "required": ["user_id", "amount", "type", "category", "description"]
    }
)
async def create_transaction(
    user_id: str,
    amount: float,
    type: str,
    category: str,
    description: str,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new transaction."""
    sb = get_supabase()
    
    # Validate amount
    if amount <= 0:
        return {
            "success": False,
            "error": "Amount must be positive"
        }
    
    # Create transaction record
    transaction_data = {
        "user_id": user_id,
        "amount": amount,
        "type": type,
        "category": category,
        "description": description,
        "location": location or "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_fraud": False,
        "fraud_score": 0.0
    }
    
    try:
        result = sb.table("transactions").insert(transaction_data).execute()
        
        if result.data:
            created_transaction = result.data[0]
            return {
                "success": True,
                "transaction": created_transaction,
                "message": f"Successfully created {type} transaction of ₹{amount} for {category}",
                "details": {
                    "id": created_transaction.get("id"),
                    "amount": amount,
                    "type": type,
                    "category": category,
                    "description": description,
                    "timestamp": created_transaction.get("timestamp")
                }
            }
        else:
            return {
                "success": False,
                "error": "Failed to create transaction"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error creating transaction: {str(e)}"
        }


@tool_registry.register(
    name="get_transactions_by_date_range",
    description="Get transactions within a specific date range with detailed information",
    category=ToolType.TRANSACTION,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID"
            },
            "start_date": {
                "type": "string",
                "description": "Start date in YYYY-MM-DD format"
            },
            "end_date": {
                "type": "string",
                "description": "End date in YYYY-MM-DD format"
            },
            "transaction_type": {
                "type": "string",
                "enum": ["expense", "income", "all"],
                "description": "Filter by transaction type",
                "default": "all"
            }
        },
        "required": ["user_id", "start_date", "end_date"]
    }
)
async def get_transactions_by_date_range(
    user_id: str,
    start_date: str,
    end_date: str,
    transaction_type: str = "all"
) -> Dict[str, Any]:
    """Get transactions in a date range."""
    sb = get_supabase()
    
    query = sb.table("transactions").select("*").eq("user_id", user_id)
    
    if transaction_type != "all":
        query = query.eq("type", transaction_type)
    
    query = query.gte("timestamp", f"{start_date}T00:00:00Z").lte("timestamp", f"{end_date}T23:59:59Z")
    query = query.order("timestamp", desc=True)
    
    result = query.execute()
    
    transactions = result.data
    
    # Calculate summary
    total_amount = sum(t["amount"] for t in transactions)
    by_category = {}
    for t in transactions:
        cat = t.get("category", "Other")
        by_category[cat] = by_category.get(cat, 0) + t["amount"]
    
    return {
        "transactions": transactions,
        "count": len(transactions),
        "date_range": f"{start_date} to {end_date}",
        "summary": {
            "total_amount": total_amount,
            "by_category": by_category,
            "average_transaction": total_amount / len(transactions) if transactions else 0
        }
    }


# ============================================================================
# ACTION TOOLS - Create, Update, Flag
# ============================================================================

@tool_registry.register(
    name="create_budget",
    description="Create a new budget for a category",
    category=ToolType.BUDGET,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID"
            },
            "category": {
                "type": "string",
                "description": "Budget category (e.g., 'Food & Dining', 'Transportation', 'Healthcare')"
            },
            "limit_amount": {
                "type": "number",
                "description": "Budget limit amount"
            }
        },
        "required": ["user_id", "category", "limit_amount"]
    }
)
async def create_budget(
    user_id: str,
    category: str,
    limit_amount: float
) -> Dict[str, Any]:
    """Create a new budget."""
    sb = get_supabase()
    
    if limit_amount <= 0:
        return {
            "success": False,
            "error": "Budget limit must be positive"
        }
    
    # Check if budget already exists for this category
    existing = sb.table("budgets").select("*").eq("user_id", user_id).eq("category", category).execute()
    
    if existing.data:
        return {
            "success": False,
            "error": f"Budget already exists for {category}. Use update_budget to modify it.",
            "existing_budget": existing.data[0]
        }
    
    # Create budget
    budget_data = {
        "user_id": user_id,
        "category": category,
        "limit_amount": limit_amount,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        result = sb.table("budgets").insert(budget_data).execute()
        
        if result.data:
            created_budget = result.data[0]
            return {
                "success": True,
                "budget": created_budget,
                "message": f"✅ Budget created successfully! {category}: ₹{limit_amount}/month",
                "details": {
                    "id": created_budget.get("id"),
                    "category": category,
                    "limit": limit_amount
                }
            }
        else:
            return {
                "success": False,
                "error": "Failed to create budget"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error creating budget: {str(e)}"
        }


@tool_registry.register(
    name="update_budget",
    description="Update an existing budget",
    category=ToolType.BUDGET,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID"
            },
            "category": {
                "type": "string",
                "description": "Budget category to update"
            },
            "limit_amount": {
                "type": "number",
                "description": "New budget limit amount"
            }
        },
        "required": ["user_id", "category", "limit_amount"]
    }
)
async def update_budget(
    user_id: str,
    category: str,
    limit_amount: float
) -> Dict[str, Any]:
    """Update an existing budget."""
    sb = get_supabase()
    
    if limit_amount <= 0:
        return {
            "success": False,
            "error": "Budget limit must be positive"
        }
    
    try:
        result = sb.table("budgets").update({
            "limit_amount": limit_amount
        }).eq("user_id", user_id).eq("category", category).execute()
        
        if result.data:
            updated_budget = result.data[0]
            return {
                "success": True,
                "budget": updated_budget,
                "message": f"✅ Budget updated! {category}: ₹{limit_amount}",
                "details": {
                    "category": category,
                    "new_limit": limit_amount
                }
            }
        else:
            return {
                "success": False,
                "error": f"Budget not found for category: {category}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error updating budget: {str(e)}"
        }


@tool_registry.register(
    name="flag_transaction_safe",
    description="Mark a transaction as safe (not fraudulent)",
    category=ToolType.FRAUD,
    parameters={
        "type": "object",
        "properties": {
            "transaction_id": {
                "type": "string",
                "description": "Transaction ID to mark as safe"
            }
        },
        "required": ["transaction_id"]
    }
)
async def flag_transaction_safe(transaction_id: str) -> Dict[str, Any]:
    """Mark transaction as safe."""
    sb = get_supabase()
    
    try:
        result = sb.table("transactions").update({
            "is_fraud": False
        }).eq("id", transaction_id).execute()
        
        if result.data:
            transaction = result.data[0]
            return {
                "success": True,
                "transaction": transaction,
                "message": f"✅ Transaction #{transaction_id} marked as safe",
                "details": {
                    "id": transaction_id,
                    "amount": transaction.get("amount"),
                    "description": transaction.get("description"),
                    "is_fraud": False
                }
            }
        else:
            return {
                "success": False,
                "error": f"Transaction not found: {transaction_id}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error flagging transaction: {str(e)}"
        }


@tool_registry.register(
    name="flag_transaction_fraud",
    description="Mark a transaction as fraudulent",
    category=ToolType.FRAUD,
    parameters={
        "type": "object",
        "properties": {
            "transaction_id": {
                "type": "string",
                "description": "Transaction ID to mark as fraud"
            }
        },
        "required": ["transaction_id"]
    }
)
async def flag_transaction_fraud(transaction_id: str) -> Dict[str, Any]:
    """Mark transaction as fraudulent."""
    sb = get_supabase()
    
    try:
        result = sb.table("transactions").update({
            "is_fraud": True
        }).eq("id", transaction_id).execute()
        
        if result.data:
            transaction = result.data[0]
            return {
                "success": True,
                "transaction": transaction,
                "message": f"⚠️ Transaction #{transaction_id} marked as fraudulent",
                "details": {
                    "id": transaction_id,
                    "amount": transaction.get("amount"),
                    "description": transaction.get("description"),
                    "is_fraud": True
                },
                "recommendation": "Contact your bank immediately to report this transaction"
            }
        else:
            return {
                "success": False,
                "error": f"Transaction not found: {transaction_id}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error flagging transaction: {str(e)}"
        }


@tool_registry.register(
    name="delete_budget",
    description="Delete a budget for a specific category",
    category=ToolType.BUDGET,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID"
            },
            "category": {
                "type": "string",
                "description": "Budget category to delete"
            }
        },
        "required": ["user_id", "category"]
    }
)
async def delete_budget(user_id: str, category: str) -> Dict[str, Any]:
    """Delete a budget."""
    sb = get_supabase()
    
    try:
        # Check if budget exists
        existing = sb.table("budgets").select("*").eq("user_id", user_id).eq("category", category).execute()
        
        if not existing.data:
            return {
                "success": False,
                "error": f"Budget not found for category: {category}"
            }
        
        # Delete budget
        result = sb.table("budgets").delete().eq("user_id", user_id).eq("category", category).execute()
        
        return {
            "success": True,
            "message": f"✅ Budget deleted successfully! Category: {category}",
            "details": {
                "category": category,
                "deleted": True
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error deleting budget: {str(e)}"
        }


@tool_registry.register(
    name="delete_transaction",
    description="Delete a transaction by ID",
    category=ToolType.TRANSACTION,
    parameters={
        "type": "object",
        "properties": {
            "transaction_id": {
                "type": "string",
                "description": "Transaction ID to delete"
            }
        },
        "required": ["transaction_id"]
    }
)
async def delete_transaction(transaction_id: str) -> Dict[str, Any]:
    """Delete a transaction."""
    sb = get_supabase()
    
    try:
        # Check if transaction exists
        existing = sb.table("transactions").select("*").eq("id", transaction_id).execute()
        
        if not existing.data:
            return {
                "success": False,
                "error": f"Transaction not found: {transaction_id}"
            }
        
        transaction = existing.data[0]
        
        # Delete transaction
        result = sb.table("transactions").delete().eq("id", transaction_id).execute()
        
        return {
            "success": True,
            "message": f"✅ Transaction deleted successfully!",
            "details": {
                "id": transaction_id,
                "amount": transaction.get("amount"),
                "description": transaction.get("description"),
                "deleted": True
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error deleting transaction: {str(e)}"
        }


@tool_registry.register(
    name="update_transaction",
    description="Update a transaction's details (type, amount, category, description, etc.). Can find transaction by ID, description, or get the last transaction.",
    category=ToolType.TRANSACTION,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID (required to find transactions)"
            },
            "transaction_id": {
                "type": "string",
                "description": "Transaction ID to update (optional if using description or last)"
            },
            "find_by_description": {
                "type": "string",
                "description": "Find transaction by description (e.g., 'Food at Alzyd')"
            },
            "use_last": {
                "type": "boolean",
                "description": "If true, update the most recent transaction",
                "default": False
            },
            "type": {
                "type": "string",
                "enum": ["expense", "income"],
                "description": "Transaction type (optional)"
            },
            "amount": {
                "type": "number",
                "description": "Transaction amount (optional)"
            },
            "category": {
                "type": "string",
                "description": "Transaction category (optional)"
            },
            "description": {
                "type": "string",
                "description": "Transaction description (optional)"
            },
            "location": {
                "type": "string",
                "description": "Transaction location (optional)"
            }
        },
        "required": ["user_id"]
    }
)
async def update_transaction(
    user_id: str,
    transaction_id: Optional[str] = None,
    find_by_description: Optional[str] = None,
    use_last: bool = False,
    type: Optional[str] = None,
    amount: Optional[float] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """Update a transaction's details."""
    sb = get_supabase()
    
    try:
        # Find the transaction to update
        if transaction_id:
            # Use provided ID
            existing = sb.table("transactions").select("*").eq("id", transaction_id).execute()
        elif find_by_description:
            # Find by description
            existing = sb.table("transactions").select("*").eq("user_id", user_id).ilike("description", f"%{find_by_description}%").order("timestamp", desc=True).limit(1).execute()
        elif use_last:
            # Get last transaction
            existing = sb.table("transactions").select("*").eq("user_id", user_id).order("timestamp", desc=True).limit(1).execute()
        else:
            return {
                "success": False,
                "error": "Must provide transaction_id, find_by_description, or use_last=True"
            }
        
        if not existing.data:
            return {
                "success": False,
                "error": f"Transaction not found"
            }
        
        transaction = existing.data[0]
        actual_transaction_id = transaction["id"]
        
        # Build update data
        update_data = {}
        if type is not None:
            update_data["type"] = type
        if amount is not None:
            update_data["amount"] = amount
        if category is not None:
            update_data["category"] = category
        if description is not None:
            update_data["description"] = description
        if location is not None:
            update_data["location"] = location
        
        if not update_data:
            return {
                "success": False,
                "error": "No fields to update"
            }
        
        # Update transaction
        result = sb.table("transactions").update(update_data).eq("id", actual_transaction_id).execute()
        
        updated_transaction = result.data[0] if result.data else {}
        
        return {
            "success": True,
            "message": f"✅ Transaction updated successfully!",
            "transaction": updated_transaction,
            "details": {
                "id": actual_transaction_id,
                "old_values": {k: transaction.get(k) for k in update_data.keys()},
                "new_values": update_data
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error updating transaction: {str(e)}"
        }
