"""
Budget Agent
Specializes in budget planning, tracking, and optimization.
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentRole


class BudgetAgent(BaseAgent):
    """
    Budget planning and tracking specialist.
    Helps users create budgets, track spending, and optimize allocations.
    """
    
    def __init__(self, model_layer, protocol_layer, rag_pipeline=None):
        """Initialize Budget Agent"""
        super().__init__(
            name="Budget Advisor",
            role=AgentRole.BUDGET_ADVISOR,
            model_layer=model_layer,
            protocol_layer=protocol_layer,
            rag_pipeline=rag_pipeline
        )
        
        # Budget-specific tools - ACCESS ALL DATA
        self.tools = [
            "get_budgets",
            "analyze_budget_trends",
            "create_budget",
            "update_budget",
            "delete_budget",
            "get_transactions",
            "get_transaction_stats",
            "get_last_transaction",
            "get_transactions_by_date_range",
            "create_transaction",
            "delete_transaction",
            "update_transaction",
            "get_risk_score",
            "get_fraud_alerts",
            "get_insurance_policies",
            "get_spending_insights"
        ]
    
    async def analyze_spending_patterns(
        self,
        user_id: str,
        category: str = None
    ) -> Dict[str, Any]:
        """
        Analyze spending patterns for budget recommendations.
        
        Args:
            user_id: User ID
            category: Optional category filter
            
        Returns:
            Spending analysis
        """
        context = {"user_id": user_id}
        
        # Get transactions
        txn_result = await self.protocol.registry.execute_tool(
            name="get_transactions",
            arguments={"user_id": user_id, "limit": 100, "type": "expense"},
            context=context
        )
        
        # Get budgets
        budget_result = await self.protocol.registry.execute_tool(
            name="get_budgets",
            arguments={"user_id": user_id},
            context=context
        )
        
        # Analyze with LLM
        analysis_prompt = f"""Analyze the spending patterns and budget status.

Transactions: {len(txn_result.get('transactions', []))} expenses
Budgets: {len(budget_result.get('budgets', []))} categories

Provide:
1. Spending trends by category
2. Budget adherence analysis
3. Areas of overspending
4. Optimization recommendations

Be specific with numbers and percentages."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": analysis_prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.5,
            max_tokens=600
        )
        
        return {
            "analysis": response["content"],
            "transactions_analyzed": len(txn_result.get('transactions', [])),
            "budgets_reviewed": len(budget_result.get('budgets', []))
        }
    
    async def suggest_budget_adjustments(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Suggest budget adjustments based on spending patterns.
        
        Args:
            user_id: User ID
            
        Returns:
            Budget adjustment recommendations
        """
        # Get budget trends
        context = {"user_id": user_id}
        trends = await self.protocol.registry.execute_tool(
            name="analyze_budget_trends",
            arguments={"user_id": user_id, "months": 3},
            context=context
        )
        
        # Generate recommendations
        prompt = f"""Based on 3-month budget trends, suggest adjustments.

Trends Data: {trends}

Provide specific recommendations:
1. Categories to increase/decrease
2. Suggested amounts
3. Reasoning for each change
4. Expected impact

Format as actionable steps."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.6,
            max_tokens=500
        )
        
        return {
            "recommendations": response["content"],
            "based_on_months": 3,
            "trends_analyzed": trends
        }
    
    async def create_budget_plan(
        self,
        user_id: str,
        income: float,
        goals: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive budget plan.
        
        Args:
            user_id: User ID
            income: Monthly income
            goals: Optional financial goals
            
        Returns:
            Budget plan
        """
        # Get historical spending
        context = {"user_id": user_id}
        stats = await self.protocol.registry.execute_tool(
            name="get_transaction_stats",
            arguments={"user_id": user_id, "months": 3},
            context=context
        )
        
        # Create plan
        prompt = f"""Create a comprehensive budget plan.

Monthly Income: ₹{income}
Historical Spending: {stats}
Goals: {goals or 'General financial health'}

Create a budget plan with:
1. Category allocations (with amounts)
2. Savings target
3. Emergency fund recommendation
4. Discretionary spending limit
5. Rationale for each allocation

Use the 50/30/20 rule as a guideline but adjust based on data."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.5,
            max_tokens=700
        )
        
        return {
            "budget_plan": response["content"],
            "income": income,
            "based_on_data": stats
        }
    
    def _prepare_tool_arguments(self, tool_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare budget-specific tool arguments"""
        args = super()._prepare_tool_arguments(tool_name, context)
        
        if tool_name == "get_transactions":
            args["transaction_type"] = "expense"  # Fixed: was "type"
            args["limit"] = 100
        elif tool_name == "analyze_budget_trends":
            args["months"] = 3
        
        return args
