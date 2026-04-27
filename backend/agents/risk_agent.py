"""
Risk Analysis Agent
Specializes in financial health assessment and risk management.
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentRole


class RiskAgent(BaseAgent):
    """
    Financial risk analysis specialist.
    Evaluates financial health, identifies vulnerabilities, and suggests improvements.
    """
    
    def __init__(self, model_layer, protocol_layer, rag_pipeline=None):
        """Initialize Risk Agent"""
        super().__init__(
            name="Risk Analyst",
            role=AgentRole.RISK_ANALYST,
            model_layer=model_layer,
            protocol_layer=protocol_layer,
            rag_pipeline=rag_pipeline
        )
        
        # Risk-specific tools - ACCESS ALL DATA
        self.tools = [
            "get_risk_score",
            "get_transactions",
            "get_transaction_stats",
            "get_budgets",
            "analyze_budget_trends",
            "get_fraud_alerts",
            "get_insurance_policies",
            "get_spending_insights",
            "get_last_transaction",
            "get_transactions_by_date_range",
            "create_budget",
            "create_transaction",
            "update_budget",
            "delete_budget",
            "delete_transaction"
        ]
        
        # Risk thresholds
        self.risk_levels = {
            "low": (0, 30),
            "medium": (31, 60),
            "high": (61, 100)
        }
    
    async def assess_financial_health(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Comprehensive financial health assessment.
        
        Args:
            user_id: User ID
            
        Returns:
            Health assessment
        """
        context = {"user_id": user_id}
        
        # Get risk score
        risk_result = await self.protocol.registry.execute_tool(
            name="get_risk_score",
            arguments={"user_id": user_id},
            context=context
        )
        
        # Get transaction stats
        stats_result = await self.protocol.registry.execute_tool(
            name="get_transaction_stats",
            arguments={"user_id": user_id, "months": 3},
            context=context
        )
        
        # Get budgets
        budget_result = await self.protocol.registry.execute_tool(
            name="get_budgets",
            arguments={"user_id": user_id},
            context=context
        )
        
        risk_score = risk_result.get("risk_score", 0)
        risk_level = self._get_risk_level(risk_score)
        
        # Generate assessment
        prompt = f"""Provide a comprehensive financial health assessment.

Risk Score: {risk_score}/100 ({risk_level})
Risk Breakdown: {risk_result.get('breakdown', {})}
Transaction Stats: {stats_result}
Budget Status: {len(budget_result.get('budgets', []))} budgets

Provide:
1. Overall health rating (Excellent/Good/Fair/Poor)
2. Key strengths in financial management
3. Critical vulnerabilities
4. Risk factors breakdown analysis
5. Priority improvements (top 3)
6. Long-term health outlook

Be specific with numbers and actionable advice."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.4,
            max_tokens=700
        )
        
        return {
            "assessment": response["content"],
            "risk_score": risk_score,
            "risk_level": risk_level,
            "breakdown": risk_result.get("breakdown", {})
        }
    
    def _get_risk_level(self, score: float) -> str:
        """Determine risk level from score"""
        for level, (min_score, max_score) in self.risk_levels.items():
            if min_score <= score <= max_score:
                return level
        return "unknown"
    
    async def analyze_risk_factors(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Detailed analysis of individual risk factors.
        
        Args:
            user_id: User ID
            
        Returns:
            Risk factor analysis
        """
        context = {"user_id": user_id}
        
        # Get risk score with breakdown
        risk_result = await self.protocol.registry.execute_tool(
            name="get_risk_score",
            arguments={"user_id": user_id},
            context=context
        )
        
        breakdown = risk_result.get("breakdown", {})
        
        # Analyze each factor
        prompt = f"""Analyze each risk factor in detail.

Risk Factors:
{breakdown}

For each factor, provide:
1. What it measures
2. Current status (good/concerning/critical)
3. Why it matters
4. How to improve it
5. Target value

Be educational and actionable."""
        
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
            "factor_analysis": response["content"],
            "factors": breakdown
        }
    
    async def create_risk_mitigation_plan(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Create a plan to reduce financial risk.
        
        Args:
            user_id: User ID
            
        Returns:
            Mitigation plan
        """
        # Get health assessment
        assessment = await self.assess_financial_health(user_id)
        
        # Create mitigation plan
        prompt = f"""Create a risk mitigation plan.

Current Assessment: {assessment['assessment']}
Risk Score: {assessment['risk_score']}
Risk Level: {assessment['risk_level']}

Create a 90-day plan with:
1. Week 1-2: Immediate actions
2. Week 3-4: Short-term improvements
3. Month 2: Medium-term goals
4. Month 3: Long-term foundations

For each phase:
- Specific actions to take
- Expected impact on risk score
- Success metrics
- Resources needed

Make it realistic and achievable."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.6,
            max_tokens=900
        )
        
        return {
            "mitigation_plan": response["content"],
            "current_risk": assessment["risk_score"],
            "target_risk": max(0, assessment["risk_score"] - 20)
        }
    
    async def predict_risk_trajectory(
        self,
        user_id: str,
        months: int = 6
    ) -> Dict[str, Any]:
        """
        Predict future risk trajectory based on current patterns.
        
        Args:
            user_id: User ID
            months: Months to predict
            
        Returns:
            Risk trajectory prediction
        """
        # Get current assessment
        assessment = await self.assess_financial_health(user_id)
        
        # Get transaction trends
        context = {"user_id": user_id}
        stats = await self.protocol.registry.execute_tool(
            name="get_transaction_stats",
            arguments={"user_id": user_id, "months": 3},
            context=context
        )
        
        # Predict trajectory
        prompt = f"""Predict financial risk trajectory for next {months} months.

Current Risk: {assessment['risk_score']}
Recent Trends: {stats}

Provide:
1. Best case scenario (if improvements made)
2. Most likely scenario (current trajectory)
3. Worst case scenario (if issues worsen)
4. Key factors that will influence trajectory
5. Early warning signs to watch for
6. Recommended monitoring frequency

Include estimated risk scores for each scenario."""
        
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
            "trajectory": response["content"],
            "current_risk": assessment["risk_score"],
            "prediction_months": months
        }
