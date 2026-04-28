"""
Query Planner
Routes queries to appropriate agents based on intent analysis.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
import re


class QueryIntent(Enum):
    """Query intent types"""
    BUDGET = "budget"
    FRAUD = "fraud"
    RISK = "risk"
    INVESTMENT = "investment"
    INSURANCE = "insurance"
    GENERAL = "general"
    MULTI_DOMAIN = "multi_domain"


class QueryPlanner:
    """
    Analyzes queries and determines which agents should handle them.
    """
    
    def __init__(self, model_layer=None):
        """
        Initialize query planner.
        
        Args:
            model_layer: Optional ModelLayer for LLM-based intent detection
        """
        self.model = model_layer
        
        # Intent keywords for rule-based routing
        self.intent_keywords = {
            QueryIntent.BUDGET: [
                "budget", "spending", "expense", "spend", "cost", "save", "savings",
                "allocate", "allocation", "overspend", "underspend", "track",
                "transaction", "transactions", "edit", "update", "change", "modify",
                "create", "add", "delete", "remove"
            ],
            QueryIntent.FRAUD: [
                "fraud", "suspicious", "security", "hack", "unauthorized", "scam",
                "alert", "flag", "unusual", "anomaly", "investigate"
            ],
            QueryIntent.RISK: [
                "risk", "health", "score", "assessment", "financial health",
                "vulnerability", "stability", "safe", "danger", "concern"
            ],
            QueryIntent.INVESTMENT: [
                "invest", "investment", "portfolio", "stock", "bond", "mutual fund",
                "sip", "asset", "allocation", "return", "roi", "equity", "debt"
            ],
            QueryIntent.INSURANCE: [
                "insurance", "policy", "coverage", "premium", "claim", "life insurance",
                "health insurance", "term insurance", "protect", "insure"
            ]
        }
        
        # Multi-domain keywords (only for truly comprehensive queries)
        self.multi_domain_keywords = [
            "complete analysis", "full review", "comprehensive review",
            "overall financial", "everything about", "entire financial"
        ]
    
    async def plan(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create execution plan for query.
        
        Args:
            query: User query
            context: Optional context dictionary
            
        Returns:
            Execution plan with agents and priorities
        """
        # Detect intent
        intents = self._detect_intent(query)
        
        # Determine agents needed
        agents = self._select_agents(intents)
        
        # Determine execution strategy
        strategy = self._determine_strategy(intents, agents)
        
        # Create plan
        plan = {
            "query": query,
            "intents": [intent.value for intent in intents],
            "agents": agents,
            "strategy": strategy,
            "priority": self._calculate_priority(intents),
            "parallel": len(agents) > 1 and strategy == "parallel"
        }
        
        return plan
    
    def _detect_intent(self, query: str) -> List[QueryIntent]:
        """
        Detect query intent using keyword matching.
        
        Args:
            query: User query
            
        Returns:
            List of detected intents
        """
        query_lower = query.lower()
        detected_intents = []
        
        # Check for multi-domain query
        if any(keyword in query_lower for keyword in self.multi_domain_keywords):
            return [QueryIntent.MULTI_DOMAIN]
        
        # Check each intent
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_intents.append(intent)
        
        # Default to general if no specific intent
        if not detected_intents:
            detected_intents.append(QueryIntent.GENERAL)
        
        return detected_intents
    
    def _select_agents(self, intents: List[QueryIntent]) -> List[str]:
        """
        Select agents based on detected intents.
        
        Args:
            intents: List of query intents
            
        Returns:
            List of agent names
        """
        agent_mapping = {
            QueryIntent.BUDGET: "budget",
            QueryIntent.FRAUD: "fraud",
            QueryIntent.RISK: "risk",
            QueryIntent.INVESTMENT: "investment",
            QueryIntent.INSURANCE: "insurance"
        }
        
        # Multi-domain queries need all agents
        if QueryIntent.MULTI_DOMAIN in intents:
            return list(agent_mapping.values())
        
        # General queries go to risk agent (financial health overview)
        if QueryIntent.GENERAL in intents:
            return ["risk"]
        
        # Map intents to agents
        agents = []
        for intent in intents:
            if intent in agent_mapping:
                agent_name = agent_mapping[intent]
                if agent_name not in agents:
                    agents.append(agent_name)
        
        return agents
    
    def _determine_strategy(
        self,
        intents: List[QueryIntent],
        agents: List[str]
    ) -> str:
        """
        Determine execution strategy.
        
        Args:
            intents: List of query intents
            agents: List of selected agents
            
        Returns:
            Strategy: "sequential", "parallel", or "single"
        """
        if len(agents) == 1:
            return "single"
        elif QueryIntent.MULTI_DOMAIN in intents:
            return "parallel"
        elif len(agents) > 2:
            return "parallel"
        else:
            return "sequential"
    
    def _calculate_priority(self, intents: List[QueryIntent]) -> str:
        """
        Calculate query priority.
        
        Args:
            intents: List of query intents
            
        Returns:
            Priority: "high", "medium", or "low"
        """
        # Fraud queries are high priority
        if QueryIntent.FRAUD in intents:
            return "high"
        
        # Multi-domain queries are medium priority
        if QueryIntent.MULTI_DOMAIN in intents:
            return "medium"
        
        # Risk queries are medium priority
        if QueryIntent.RISK in intents:
            return "medium"
        
        # Others are low priority
        return "low"
    
    async def plan_with_llm(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Use LLM for more sophisticated intent detection.
        
        Args:
            query: User query
            context: Optional context dictionary
            
        Returns:
            Execution plan
        """
        if not self.model:
            # Fall back to rule-based planning
            return await self.plan(query, context)
        
        # Use LLM to analyze query
        prompt = f"""Analyze this financial query and determine which agents should handle it.

Query: {query}

Available agents:
- budget: Budget planning and spending analysis
- fraud: Fraud detection and security
- risk: Financial health and risk assessment
- investment: Investment advice and portfolio management
- insurance: Insurance planning and coverage

Respond in JSON format:
{{
    "intents": ["intent1", "intent2"],
    "agents": ["agent1", "agent2"],
    "strategy": "parallel" or "sequential",
    "reasoning": "why these agents"
}}"""
        
        try:
            messages = [
                {"role": "system", "content": "You are a query routing expert."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.model.generate(
                messages=messages,
                temperature=0.1,
                max_tokens=200
            )
            
            # Parse LLM response
            import json
            plan_data = json.loads(response["content"])
            
            return {
                "query": query,
                "intents": plan_data.get("intents", []),
                "agents": plan_data.get("agents", []),
                "strategy": plan_data.get("strategy", "sequential"),
                "reasoning": plan_data.get("reasoning", ""),
                "priority": "medium",
                "parallel": plan_data.get("strategy") == "parallel"
            }
        except Exception:
            # Fall back to rule-based on error
            return await self.plan(query, context)
    
    def explain_plan(self, plan: Dict[str, Any]) -> str:
        """
        Generate human-readable explanation of the plan.
        
        Args:
            plan: Execution plan
            
        Returns:
            Explanation string
        """
        agents_str = ", ".join(plan["agents"])
        strategy_str = plan["strategy"]
        
        explanation = f"Query will be handled by: {agents_str}\n"
        explanation += f"Execution strategy: {strategy_str}\n"
        explanation += f"Priority: {plan['priority']}"
        
        if "reasoning" in plan:
            explanation += f"\nReasoning: {plan['reasoning']}"
        
        return explanation
