"""
Agent Coordinator
Main orchestration layer that coordinates planning, execution, and synthesis.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .planner import QueryPlanner
from .executor import AgentExecutor
from .synthesizer import ResponseSynthesizer


class AgentCoordinator:
    """
    Coordinates the entire multi-agent workflow.
    Handles planning, execution, and synthesis.
    """
    
    def __init__(
        self,
        agents: Dict[str, Any],
        model_layer=None,
        use_llm_planning: bool = False,
        use_llm_synthesis: bool = True
    ):
        """
        Initialize coordinator.
        
        Args:
            agents: Dictionary of agent instances
            model_layer: Optional ModelLayer for LLM features
            use_llm_planning: Whether to use LLM for query planning
            use_llm_synthesis: Whether to use LLM for response synthesis
        """
        self.agents = agents
        self.model = model_layer
        
        # Initialize components
        self.planner = QueryPlanner(model_layer if use_llm_planning else None)
        self.executor = AgentExecutor(agents)
        self.synthesizer = ResponseSynthesizer(model_layer if use_llm_synthesis else None)
        
        # Conversation history - stores last 10 turns per user
        self.conversation_history = []
        self.conversation_memory = {}  # user_id -> list of conversation turns
    
    async def process_query(
        self,
        query: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the complete orchestration pipeline.
        
        Args:
            query: User query
            context: Optional context (user_id, etc.)
            
        Returns:
            Complete response with plan, execution, and synthesis
        """
        start_time = datetime.now()
        context = context or {}
        user_id = context.get("user_id", "default")
        
        # Get conversation history for this user
        user_history = self.conversation_memory.get(user_id, [])
        if user_history:
            context["conversation_history"] = user_history[-5:]  # Last 5 turns
        
        try:
            # Step 1: Plan
            plan = await self.planner.plan(query, context)
            
            # Step 2: Execute
            execution_result = await self.executor.execute(plan, context)
            
            # Step 3: Synthesize
            synthesis_result = await self.synthesizer.synthesize(query, execution_result)
            
            # Calculate total time
            total_time = (datetime.now() - start_time).total_seconds()
            
            # Build complete response
            response = {
                "query": query,
                "response": synthesis_result.get("response", ""),
                "success": synthesis_result.get("success", False),
                "plan": plan,
                "execution": {
                    "strategy": execution_result.get("strategy"),
                    "execution_time": execution_result.get("execution_time"),
                    "agents_used": [r.get("agent") for r in execution_result.get("results", [])]
                },
                "synthesis": {
                    "method": synthesis_result.get("synthesis_method", "unknown"),
                    "sources": len(synthesis_result.get("sources", []))
                },
                "total_time": total_time,
                "timestamp": start_time.isoformat()
            }
            
            # Store in conversation history (global)
            self.conversation_history.append(response)
            
            # Store in user-specific memory
            if user_id not in self.conversation_memory:
                self.conversation_memory[user_id] = []
            
            self.conversation_memory[user_id].append({
                "query": query,
                "response": response["response"],
                "timestamp": start_time.isoformat(),
                "agents_used": response["execution"]["agents_used"]
            })
            
            # Keep only last 10 turns per user
            if len(self.conversation_memory[user_id]) > 10:
                self.conversation_memory[user_id] = self.conversation_memory[user_id][-10:]
            
            return response
            
        except Exception as e:
            return {
                "query": query,
                "response": f"I encountered an error processing your request: {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": start_time.isoformat()
            }
    
    async def process_conversation(
        self,
        messages: list,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a multi-turn conversation.
        
        Args:
            messages: List of conversation messages
            context: Optional context
            
        Returns:
            Response to latest message
        """
        # Get latest user message
        latest_message = messages[-1] if messages else {"content": ""}
        query = latest_message.get("content", "")
        
        # Add conversation history to context
        context = context or {}
        context["conversation_history"] = self.conversation_history[-5:]  # Last 5 turns
        
        # Process query
        return await self.process_query(query, context)
    
    def get_conversation_history(self, limit: int = 10) -> list:
        """Get recent conversation history"""
        return self.conversation_history[-limit:]
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get coordinator statistics"""
        if not self.conversation_history:
            return {
                "total_queries": 0,
                "avg_response_time": 0,
                "success_rate": 0
            }
        
        total = len(self.conversation_history)
        total_time = sum(q.get("total_time", 0) for q in self.conversation_history)
        successful = sum(1 for q in self.conversation_history if q.get("success", False))
        
        # Get executor statistics
        executor_stats = self.executor.get_statistics()
        
        return {
            "total_queries": total,
            "avg_response_time": total_time / total if total > 0 else 0,
            "success_rate": successful / total if total > 0 else 0,
            "executor_stats": executor_stats,
            "agents_available": list(self.agents.keys())
        }
    
    def explain_last_response(self) -> str:
        """Generate explanation of last response"""
        if not self.conversation_history:
            return "No queries processed yet."
        
        last = self.conversation_history[-1]
        
        explanation = f"""Query: {last['query']}

Plan:
- Agents selected: {', '.join(last['plan']['agents'])}
- Strategy: {last['plan']['strategy']}
- Priority: {last['plan']['priority']}

Execution:
- Agents used: {', '.join(last['execution']['agents_used'])}
- Execution time: {last['execution']['execution_time']:.2f}s

Synthesis:
- Method: {last['synthesis']['method']}
- Sources: {last['synthesis']['sources']} agent(s)

Total time: {last['total_time']:.2f}s
Success: {last['success']}"""
        
        return explanation
    
    async def get_agent_recommendations(
        self,
        query: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Get recommendations without full execution (planning only).
        
        Args:
            query: User query
            context: Optional context
            
        Returns:
            Recommended agents and strategy
        """
        plan = await self.planner.plan(query, context)
        explanation = self.planner.explain_plan(plan)
        
        return {
            "query": query,
            "recommended_agents": plan["agents"],
            "strategy": plan["strategy"],
            "priority": plan["priority"],
            "explanation": explanation
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {}
        
        for name, agent in self.agents.items():
            capabilities = agent.get_capabilities()
            status[name] = {
                "available": True,
                "role": capabilities.get("role"),
                "tools": capabilities.get("tools", []),
                "has_rag": capabilities.get("has_rag", False),
                "memory_size": capabilities.get("memory_size", 0)
            }
        
        return status


class ConversationManager:
    """
    Manages multi-turn conversations with context.
    """
    
    def __init__(self, coordinator: AgentCoordinator):
        """
        Initialize conversation manager.
        
        Args:
            coordinator: AgentCoordinator instance
        """
        self.coordinator = coordinator
        self.sessions = {}  # session_id -> conversation data
    
    def create_session(self, user_id: str) -> str:
        """Create new conversation session"""
        import uuid
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "user_id": user_id,
            "messages": [],
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        return session_id
    
    async def send_message(
        self,
        session_id: str,
        message: str
    ) -> Dict[str, Any]:
        """Send message in session"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        
        # Add user message
        session["messages"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process with coordinator
        context = {"user_id": session["user_id"]}
        response = await self.coordinator.process_conversation(
            session["messages"],
            context
        )
        
        # Add assistant response
        session["messages"].append({
            "role": "assistant",
            "content": response.get("response", ""),
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "agents_used": response.get("execution", {}).get("agents_used", []),
                "total_time": response.get("total_time", 0)
            }
        })
        
        session["last_activity"] = datetime.now().isoformat()
        
        return response
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return self.sessions.get(session_id)
    
    def delete_session(self, session_id: str):
        """Delete session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
