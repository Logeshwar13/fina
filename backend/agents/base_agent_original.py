"""
Base Agent Class
Implements the core agent interface with plan-act-observe-reflect-respond loop.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json


class AgentRole(Enum):
    """Agent role types"""
    BUDGET_ADVISOR = "budget_advisor"
    FRAUD_DETECTOR = "fraud_detector"
    RISK_ANALYST = "risk_analyst"
    INVESTMENT_ADVISOR = "investment_advisor"
    INSURANCE_ADVISOR = "insurance_advisor"


@dataclass
class AgentMemory:
    """Represents an agent's memory entry"""
    timestamp: str
    query: str
    plan: Dict[str, Any]
    actions: List[Dict[str, Any]]
    observations: List[Dict[str, Any]]
    reflection: str
    response: str


class BaseAgent:
    """
    Base class for all financial agents.
    Implements the agentic loop: Plan → Act → Observe → Reflect → Respond
    """
    
    def __init__(
        self,
        name: str,
        role: AgentRole,
        model_layer,
        protocol_layer,
        rag_pipeline=None,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize agent.
        
        Args:
            name: Agent name
            role: Agent role
            model_layer: ModelLayer for LLM access
            protocol_layer: ProtocolLayer for tool access
            rag_pipeline: Optional RAGPipeline for context retrieval
            system_prompt: Optional custom system prompt
        """
        self.name = name
        self.role = role
        self.model = model_layer
        self.protocol = protocol_layer
        self.rag = rag_pipeline
        self.memory: List[AgentMemory] = []
        
        # Set system prompt
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = self._get_default_system_prompt()
        
        # Agent capabilities
        self.tools = []
        self.max_iterations = 5
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt based on role"""
        prompts = {
            AgentRole.BUDGET_ADVISOR: """You are a Budget Advisor AI agent specializing in personal finance management.
Your role is to help users plan budgets, track spending, and optimize their financial allocations.
You have access to transaction data, budget information, and spending patterns.
Always provide actionable, specific advice based on the user's actual financial data.""",
            
            AgentRole.FRAUD_DETECTOR: """You are a Fraud Detection AI agent specializing in financial security.
Your role is to identify suspicious transactions, detect patterns of fraud, and protect users' finances.
You analyze transaction patterns, flag anomalies, and provide security recommendations.
Always prioritize user safety and explain your reasoning clearly.""",
            
            AgentRole.RISK_ANALYST: """You are a Risk Analysis AI agent specializing in financial health assessment.
Your role is to evaluate users' financial risk profiles, identify vulnerabilities, and suggest improvements.
You analyze spending patterns, savings rates, debt levels, and overall financial stability.
Always provide balanced, realistic assessments with actionable recommendations.""",
            
            AgentRole.INVESTMENT_ADVISOR: """You are an Investment Advisor AI agent specializing in portfolio management.
Your role is to analyze investment opportunities, suggest asset allocations, and optimize returns.
You consider risk tolerance, financial goals, and market conditions.
Always provide balanced advice and clearly state assumptions and risks.""",
            
            AgentRole.INSURANCE_ADVISOR: """You are an Insurance Advisor AI agent specializing in coverage planning.
Your role is to assess insurance needs, recommend appropriate coverage, and optimize premiums.
You analyze users' financial situations, dependents, assets, and risk factors.
Always provide comprehensive coverage recommendations with clear explanations."""
        }
        return prompts.get(self.role, "You are a helpful financial AI agent.")
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a query through the agentic loop.
        
        Args:
            query: User query
            context: Context dictionary (user_id, etc.)
            
        Returns:
            Agent response with reasoning
        """
        # Step 1: Plan
        plan = await self.plan(query, context)
        
        # Step 2: Act (execute tools)
        actions = await self.act(plan, context)
        
        # Step 3: Observe (process results)
        observations = await self.observe(actions)
        
        # Step 4: Reflect (analyze and learn)
        reflection = await self.reflect(query, observations, context)
        
        # Step 5: Respond (generate final answer)
        response = await self.respond(query, reflection, observations, context)
        
        # Store in memory
        memory_entry = AgentMemory(
            timestamp=datetime.now().isoformat(),
            query=query,
            plan=plan,
            actions=actions,
            observations=observations,
            reflection=reflection,
            response=response
        )
        self.memory.append(memory_entry)
        
        return {
            "agent": self.name,
            "role": self.role.value,
            "query": query,
            "plan": plan,
            "actions": actions,
            "observations": observations,
            "reflection": reflection,
            "response": response,
            "timestamp": memory_entry.timestamp
        }
    
    async def plan(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an execution plan for the query.
        
        Args:
            query: User query
            context: Context dictionary
            
        Returns:
            Execution plan
        """
        # Get relevant context from RAG if available
        rag_context = ""
        if self.rag:
            rag_result = await self.rag.query(
                query=query,
                user_id=context.get("user_id", ""),
                top_k=3,
                include_context=True
            )
            rag_context = rag_result.get("context", "")
        
        # Generate plan using LLM
        planning_prompt = f"""Given the user query and available context, create an execution plan.

User Query: {query}

Available Context:
{rag_context}

Available Tools: {', '.join(self.tools)}

Create a step-by-step plan to answer the query. For each step, specify:
1. What tool to use (if any)
2. What information to gather
3. How it contributes to the answer

Respond in JSON format:
{{
    "steps": [
        {{"step": 1, "action": "tool_name", "purpose": "why this step"}},
        ...
    ],
    "reasoning": "overall strategy"
}}"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": planning_prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )
        
        # Parse plan
        try:
            plan = json.loads(response["content"])
        except:
            # Fallback plan
            plan = {
                "steps": [{"step": 1, "action": "analyze", "purpose": "answer query"}],
                "reasoning": "Direct analysis"
            }
        
        return plan
    
    async def act(self, plan: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute the plan by calling tools.
        
        Args:
            plan: Execution plan
            context: Context dictionary
            
        Returns:
            List of action results
        """
        actions = []
        
        for step in plan.get("steps", []):
            action_name = step.get("action", "")
            
            # Check if action is a tool
            if action_name in self.tools:
                try:
                    # Execute tool
                    result = await self.protocol.registry.execute_tool(
                        name=action_name,
                        arguments=self._prepare_tool_arguments(action_name, context),
                        context=context
                    )
                    
                    actions.append({
                        "step": step.get("step"),
                        "action": action_name,
                        "status": "success",
                        "result": result
                    })
                except Exception as e:
                    actions.append({
                        "step": step.get("step"),
                        "action": action_name,
                        "status": "error",
                        "error": str(e)
                    })
            else:
                # Non-tool action (analysis, reasoning, etc.)
                actions.append({
                    "step": step.get("step"),
                    "action": action_name,
                    "status": "skipped",
                    "reason": "Not a tool action"
                })
        
        return actions
    
    def _prepare_tool_arguments(self, tool_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare arguments for tool execution"""
        # Base arguments
        args = {
            "user_id": context.get("user_id", "")
        }
        
        # Add tool-specific arguments
        if "transaction" in tool_name:
            args["limit"] = 50
        elif "budget" in tool_name:
            args["month"] = context.get("month", "")
        
        return args
    
    async def observe(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process and structure action results.
        
        Args:
            actions: List of action results
            
        Returns:
            Structured observations
        """
        observations = []
        
        for action in actions:
            if action["status"] == "success":
                observation = {
                    "action": action["action"],
                    "data": action["result"],
                    "summary": self._summarize_result(action["result"])
                }
                observations.append(observation)
        
        return observations
    
    def _summarize_result(self, result: Any) -> str:
        """Create a summary of tool result"""
        if isinstance(result, dict):
            if "transactions" in result:
                return f"Found {len(result['transactions'])} transactions"
            elif "budgets" in result:
                return f"Found {len(result['budgets'])} budgets"
            elif "risk_score" in result:
                return f"Risk score: {result['risk_score']}"
        return "Data retrieved successfully"
    
    async def reflect(
        self,
        query: str,
        observations: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> str:
        """
        Analyze observations and generate insights.
        
        Args:
            query: Original query
            observations: Structured observations
            context: Context dictionary
            
        Returns:
            Reflection text
        """
        # Format observations for LLM
        obs_text = "\n".join([
            f"- {obs['action']}: {obs['summary']}"
            for obs in observations
        ])
        
        reflection_prompt = f"""Analyze the following observations and generate insights.

Original Query: {query}

Observations:
{obs_text}

Provide:
1. Key findings from the data
2. Patterns or trends identified
3. Potential concerns or opportunities
4. Recommendations

Be specific and reference actual data points."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": reflection_prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.5,
            max_tokens=400
        )
        
        return response["content"]
    
    async def respond(
        self,
        query: str,
        reflection: str,
        observations: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> str:
        """
        Generate final response to user.
        
        Args:
            query: Original query
            reflection: Reflection text
            observations: Structured observations
            context: Context dictionary
            
        Returns:
            Final response
        """
        # Format data for response
        data_summary = "\n".join([
            f"- {obs['summary']}"
            for obs in observations
        ])
        
        response_prompt = f"""Generate a helpful response to the user's query.

User Query: {query}

Data Summary:
{data_summary}

Analysis:
{reflection}

Provide a clear, actionable response that:
1. Directly answers the query
2. References specific data points
3. Provides actionable recommendations
4. Is easy to understand

Keep the response concise but comprehensive."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": response_prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response["content"]
    
    def get_memory(self, limit: int = 10) -> List[AgentMemory]:
        """Get recent memory entries"""
        return self.memory[-limit:]
    
    def clear_memory(self):
        """Clear agent memory"""
        self.memory = []
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        return {
            "name": self.name,
            "role": self.role.value,
            "tools": self.tools,
            "has_rag": self.rag is not None,
            "memory_size": len(self.memory)
        }
