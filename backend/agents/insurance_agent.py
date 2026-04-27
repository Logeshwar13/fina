"""
Insurance Advisory Agent
Specializes in insurance planning and coverage optimization.
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentRole


class InsuranceAgent(BaseAgent):
    """
    Insurance planning specialist.
    Assesses insurance needs, recommends coverage, and optimizes premiums.
    """
    
    def __init__(self, model_layer, protocol_layer, rag_pipeline=None):
        """Initialize Insurance Agent"""
        super().__init__(
            name="Insurance Advisor",
            role=AgentRole.INSURANCE_ADVISOR,
            model_layer=model_layer,
            protocol_layer=protocol_layer,
            rag_pipeline=rag_pipeline
        )
        
        # Insurance-specific tools - ACCESS ALL DATA
        self.tools = [
            "get_insurance_policies",
            "get_transactions",
            "get_risk_score",
            "get_transaction_stats",
            "get_budgets",
            "analyze_budget_trends",
            "get_fraud_alerts",
            "get_spending_insights",
            "get_last_transaction",
            "get_transactions_by_date_range",
            "create_budget",
            "create_transaction",
            "update_budget",
            "delete_budget",
            "delete_transaction"
        ]
        
        # Insurance guidelines
        self.coverage_multipliers = {
            "life": 10,  # 10x annual income
            "health": 5,  # 5 lakh minimum
            "term": 15,  # 15x annual income for term insurance
        }
        
        self.policy_types = {
            "life": "Life Insurance",
            "health": "Health Insurance",
            "term": "Term Insurance",
            "critical_illness": "Critical Illness",
            "disability": "Disability Insurance",
            "vehicle": "Vehicle Insurance",
            "home": "Home Insurance"
        }
    
    async def assess_insurance_needs(
        self,
        user_id: str,
        age: int,
        income: float,
        dependents: int = 0,
        liabilities: float = 0
    ) -> Dict[str, Any]:
        """
        Assess comprehensive insurance needs.
        
        Args:
            user_id: User ID
            age: User age
            income: Annual income
            dependents: Number of dependents
            liabilities: Total liabilities (loans, etc.)
            
        Returns:
            Insurance needs assessment
        """
        context = {"user_id": user_id}
        
        # Get existing policies
        policies_result = await self.protocol.registry.execute_tool(
            name="get_insurance_policies",
            arguments={"user_id": user_id},
            context=context
        )
        
        # Get risk profile
        risk_result = await self.protocol.registry.execute_tool(
            name="get_risk_score",
            arguments={"user_id": user_id},
            context=context
        )
        
        existing_policies = policies_result.get("policies", [])
        
        # Calculate recommended coverage
        life_coverage = income * self.coverage_multipliers["life"]
        term_coverage = income * self.coverage_multipliers["term"] + liabilities
        health_coverage = max(500000, income * 0.5)  # Min 5 lakh or 50% of income
        
        # Generate assessment
        prompt = f"""Assess comprehensive insurance needs.

User Profile:
- Age: {age}
- Annual Income: ₹{income}
- Dependents: {dependents}
- Liabilities: ₹{liabilities}
- Risk Score: {risk_result.get('risk_score', 0)}

Existing Coverage:
{len(existing_policies)} policies

Recommended Coverage:
- Life Insurance: ₹{life_coverage:,.0f}
- Term Insurance: ₹{term_coverage:,.0f}
- Health Insurance: ₹{health_coverage:,.0f}

Provide:
1. Coverage gap analysis
2. Priority insurance needs
3. Recommended policy types
4. Coverage amounts for each type
5. Estimated premium budget
6. Timeline for implementation
7. Special considerations based on age/dependents

Be specific with amounts and reasoning."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.4,
            max_tokens=800
        )
        
        return {
            "needs_assessment": response["content"],
            "recommended_coverage": {
                "life": life_coverage,
                "term": term_coverage,
                "health": health_coverage
            },
            "existing_policies": len(existing_policies)
        }
    
    async def analyze_existing_coverage(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Analyze existing insurance coverage.
        
        Args:
            user_id: User ID
            
        Returns:
            Coverage analysis
        """
        context = {"user_id": user_id}
        
        # Get policies
        policies_result = await self.protocol.registry.execute_tool(
            name="get_insurance_policies",
            arguments={"user_id": user_id},
            context=context
        )
        
        policies = policies_result.get("policies", [])
        
        if not policies:
            return {
                "analysis": "No existing insurance coverage found. Immediate action needed.",
                "policies_count": 0
            }
        
        # Analyze coverage
        prompt = f"""Analyze existing insurance coverage.

Policies: {policies}

Provide:
1. Coverage adequacy assessment
2. Policy-wise evaluation
3. Gaps in coverage
4. Overlapping coverage (if any)
5. Premium optimization opportunities
6. Policy renewal priorities
7. Recommended additions/modifications

Be specific about each policy."""
        
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
            "coverage_analysis": response["content"],
            "policies_count": len(policies),
            "policies": policies
        }
    
    async def recommend_policy_improvements(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Recommend improvements to insurance portfolio.
        
        Args:
            user_id: User ID
            
        Returns:
            Improvement recommendations
        """
        # Get coverage analysis
        analysis = await self.analyze_existing_coverage(user_id)
        
        # Generate recommendations
        prompt = f"""Recommend insurance portfolio improvements.

Current Analysis: {analysis['coverage_analysis']}

Provide:
1. Top 3 priority improvements
2. Cost-benefit analysis for each
3. Implementation steps
4. Expected premium impact
5. Timeline for changes
6. Provider recommendations (general criteria)
7. Red flags to avoid

Focus on practical, actionable improvements."""
        
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
            "recommendations": response["content"],
            "based_on_analysis": analysis
        }
    
    async def calculate_optimal_premium_budget(
        self,
        user_id: str,
        income: float
    ) -> Dict[str, Any]:
        """
        Calculate optimal insurance premium budget.
        
        Args:
            user_id: User ID
            income: Annual income
            
        Returns:
            Premium budget recommendation
        """
        # Get existing policies
        context = {"user_id": user_id}
        policies_result = await self.protocol.registry.execute_tool(
            name="get_insurance_policies",
            arguments={"user_id": user_id},
            context=context
        )
        
        policies = policies_result.get("policies", [])
        current_premium = sum(p.get("premium", 0) for p in policies)
        
        # Calculate optimal budget (typically 10-15% of income)
        optimal_budget = income * 0.12  # 12% of annual income
        
        # Generate budget plan
        prompt = f"""Calculate optimal insurance premium budget.

Annual Income: ₹{income}
Current Premium: ₹{current_premium}
Recommended Budget: ₹{optimal_budget} (12% of income)

Provide:
1. Budget allocation by policy type
2. Current vs optimal comparison
3. Adjustment recommendations
4. Premium optimization strategies
5. Tax benefits consideration
6. Payment frequency optimization

Include specific amounts for each category."""
        
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
            "premium_budget": response["content"],
            "optimal_budget": optimal_budget,
            "current_premium": current_premium,
            "gap": optimal_budget - current_premium
        }
    
    async def create_insurance_roadmap(
        self,
        user_id: str,
        age: int,
        income: float,
        life_stage: str = "young_professional"
    ) -> Dict[str, Any]:
        """
        Create age-appropriate insurance roadmap.
        
        Args:
            user_id: User ID
            age: User age
            income: Annual income
            life_stage: Life stage (young_professional, married, parent, pre_retirement)
            
        Returns:
            Insurance roadmap
        """
        # Get needs assessment
        needs = await self.assess_insurance_needs(user_id, age, income)
        
        # Create roadmap
        prompt = f"""Create an insurance roadmap.

Age: {age}
Life Stage: {life_stage}
Income: ₹{income}
Needs Assessment: {needs['needs_assessment']}

Create a phased roadmap:

Phase 1 (Immediate - 0-3 months):
- Essential coverage to buy
- Priority and reasoning
- Estimated cost

Phase 2 (Short-term - 3-12 months):
- Additional coverage
- Enhancements to existing
- Cost considerations

Phase 3 (Medium-term - 1-3 years):
- Comprehensive coverage
- Specialized policies
- Review and optimization

Phase 4 (Long-term - 3+ years):
- Life stage adjustments
- Coverage updates
- Retirement planning integration

Make it specific and actionable for the life stage."""
        
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
            "insurance_roadmap": response["content"],
            "age": age,
            "life_stage": life_stage
        }
