"""
Investment Advisory Agent
Specializes in portfolio management and investment strategy.
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentRole


class InvestmentAgent(BaseAgent):
    """
    Investment advisory specialist.
    Analyzes portfolios, suggests allocations, and optimizes returns.
    """
    
    def __init__(self, model_layer, protocol_layer, rag_pipeline=None):
        """Initialize Investment Agent"""
        super().__init__(
            name="Investment Advisor",
            role=AgentRole.INVESTMENT_ADVISOR,
            model_layer=model_layer,
            protocol_layer=protocol_layer,
            rag_pipeline=rag_pipeline
        )
        
        # Investment-specific tools - ACCESS ALL DATA
        self.tools = [
            "get_transactions",
            "get_transaction_stats",
            "get_budgets",
            "get_risk_score",
            "get_last_transaction",
            "create_transaction",
            "get_transactions_by_date_range",
            "analyze_budget_trends",
            "get_fraud_alerts",
            "get_insurance_policies",
            "get_spending_insights",
            "create_budget",
            "update_budget",
            "delete_budget",
            "delete_transaction"
        ]
        
        # Investment guidelines
        self.asset_classes = {
            "equity": {"risk": "high", "return": "high", "horizon": "long"},
            "debt": {"risk": "low", "return": "moderate", "horizon": "short"},
            "gold": {"risk": "moderate", "return": "moderate", "horizon": "medium"},
            "real_estate": {"risk": "moderate", "return": "high", "horizon": "long"},
            "cash": {"risk": "very_low", "return": "low", "horizon": "immediate"}
        }
    
    async def analyze_investment_capacity(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Analyze user's capacity to invest.
        
        Args:
            user_id: User ID
            
        Returns:
            Investment capacity analysis
        """
        context = {"user_id": user_id}
        
        # Get financial data
        stats = await self.protocol.registry.execute_tool(
            name="get_transaction_stats",
            arguments={"user_id": user_id, "months": 3},
            context=context
        )
        
        budgets = await self.protocol.registry.execute_tool(
            name="get_budgets",
            arguments={"user_id": user_id},
            context=context
        )
        
        risk_score = await self.protocol.registry.execute_tool(
            name="get_risk_score",
            arguments={"user_id": user_id},
            context=context
        )
        
        # Analyze capacity
        prompt = f"""Analyze investment capacity and readiness.

Financial Stats: {stats}
Budget Status: {len(budgets.get('budgets', []))} budgets
Risk Score: {risk_score.get('risk_score', 0)}

Provide:
1. Monthly investable surplus (estimate)
2. Investment readiness score (1-10)
3. Prerequisites before investing
4. Recommended emergency fund size
5. Debt clearance priority
6. Timeline to start investing

Be conservative and prioritize financial stability."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.4,
            max_tokens=600
        )
        
        return {
            "capacity_analysis": response["content"],
            "risk_score": risk_score.get("risk_score", 0)
        }
    
    async def suggest_asset_allocation(
        self,
        user_id: str,
        investment_amount: float,
        time_horizon: str = "medium",
        risk_tolerance: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Suggest asset allocation strategy.
        
        Args:
            user_id: User ID
            investment_amount: Amount to invest
            time_horizon: short/medium/long
            risk_tolerance: low/moderate/high
            
        Returns:
            Asset allocation recommendation
        """
        # Get user's risk profile
        context = {"user_id": user_id}
        risk_result = await self.protocol.registry.execute_tool(
            name="get_risk_score",
            arguments={"user_id": user_id},
            context=context
        )
        
        # Generate allocation
        prompt = f"""Suggest asset allocation strategy.

Investment Amount: ₹{investment_amount}
Time Horizon: {time_horizon}
Risk Tolerance: {risk_tolerance}
User Risk Score: {risk_result.get('risk_score', 0)}

Available Asset Classes:
{self.asset_classes}

Provide:
1. Recommended allocation percentages
2. Specific asset class breakdown
3. Rationale for each allocation
4. Expected returns (realistic range)
5. Risk considerations
6. Rebalancing frequency
7. Specific investment instruments for each class

Use modern portfolio theory principles."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.5,
            max_tokens=800
        )
        
        return {
            "allocation_strategy": response["content"],
            "investment_amount": investment_amount,
            "time_horizon": time_horizon,
            "risk_tolerance": risk_tolerance
        }
    
    async def evaluate_investment_goals(
        self,
        user_id: str,
        goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate and plan for investment goals.
        
        Args:
            user_id: User ID
            goals: Investment goals (retirement, house, education, etc.)
            
        Returns:
            Goal evaluation and plan
        """
        # Get capacity
        capacity = await self.analyze_investment_capacity(user_id)
        
        # Evaluate goals
        prompt = f"""Evaluate investment goals and create a plan.

Investment Goals: {goals}
Investment Capacity: {capacity['capacity_analysis']}

For each goal, provide:
1. Required corpus calculation
2. Monthly SIP amount needed
3. Recommended investment mix
4. Timeline feasibility
5. Risk factors
6. Milestone tracking

Prioritize goals and suggest phased approach if needed."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.5,
            max_tokens=900
        )
        
        return {
            "goal_evaluation": response["content"],
            "goals": goals
        }
    
    async def generate_investment_strategy(
        self,
        user_id: str,
        age: int,
        income: float,
        goals: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive investment strategy.
        
        Args:
            user_id: User ID
            age: User age
            income: Monthly income
            goals: Optional investment goals
            
        Returns:
            Complete investment strategy
        """
        # Get financial profile
        capacity = await self.analyze_investment_capacity(user_id)
        
        # Generate strategy
        prompt = f"""Create a comprehensive investment strategy.

Age: {age}
Monthly Income: ₹{income}
Investment Capacity: {capacity['capacity_analysis']}
Goals: {goals or 'Wealth creation and retirement'}

Create a strategy covering:
1. Investment philosophy (based on age and goals)
2. Asset allocation framework
3. Product recommendations (mutual funds, stocks, bonds, etc.)
4. Tax optimization strategies
5. Risk management approach
6. Review and rebalancing schedule
7. Do's and Don'ts
8. Common mistakes to avoid

Make it age-appropriate and goal-aligned."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.6,
            max_tokens=1000
        )
        
        return {
            "investment_strategy": response["content"],
            "age": age,
            "income": income
        }
    
    async def analyze_market_timing(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Provide guidance on market timing and entry strategy.
        
        Args:
            user_id: User ID
            
        Returns:
            Market timing guidance
        """
        prompt = f"""Provide guidance on market timing and investment entry.

Discuss:
1. Why timing the market is difficult
2. Benefits of systematic investment (SIP/DCA)
3. Current market considerations (general)
4. Entry strategies for different market conditions
5. Psychological aspects of investing
6. Long-term vs short-term perspective

Emphasize evidence-based investing principles."""
        
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
            "market_timing_guidance": response["content"]
        }
