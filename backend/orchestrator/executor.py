"""
Agent Executor
Executes agents in parallel or sequential mode.
"""

from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime


class AgentExecutor:
    """
    Executes multiple agents according to the execution plan.
    """
    
    def __init__(self, agents: Dict[str, Any]):
        """
        Initialize executor with available agents.
        
        Args:
            agents: Dictionary mapping agent names to agent instances
        """
        self.agents = agents
        self.execution_history = []
    
    async def execute(
        self,
        plan: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute agents according to plan.
        
        Args:
            plan: Execution plan from QueryPlanner
            context: Execution context (user_id, etc.)
            
        Returns:
            Execution results
        """
        start_time = datetime.now()
        
        # Get strategy
        strategy = plan.get("strategy", "single")
        agent_names = plan.get("agents", [])
        
        # Execute based on strategy
        if strategy == "single":
            results = await self._execute_single(agent_names[0], plan["query"], context)
        elif strategy == "parallel":
            results = await self._execute_parallel(agent_names, plan["query"], context)
        else:  # sequential
            results = await self._execute_sequential(agent_names, plan["query"], context)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Store in history
        execution_record = {
            "plan": plan,
            "results": results,
            "execution_time": execution_time,
            "timestamp": start_time.isoformat()
        }
        self.execution_history.append(execution_record)
        
        return {
            "plan": plan,
            "results": results,
            "execution_time": execution_time,
            "strategy": strategy
        }
    
    async def _execute_single(
        self,
        agent_name: str,
        query: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute single agent"""
        agent = self.agents.get(agent_name)
        if not agent:
            return [{
                "agent": agent_name,
                "error": f"Agent '{agent_name}' not found",
                "success": False
            }]
        
        try:
            result = await agent.process(query, context)
            result["success"] = True
            return [result]
        except Exception as e:
            return [{
                "agent": agent_name,
                "error": str(e),
                "success": False
            }]
    
    async def _execute_parallel(
        self,
        agent_names: List[str],
        query: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute multiple agents in parallel"""
        tasks = []
        
        for agent_name in agent_names:
            agent = self.agents.get(agent_name)
            if agent:
                task = self._execute_agent_safe(agent, agent_name, query, context)
                tasks.append(task)
        
        # Execute all in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    "error": str(result),
                    "success": False
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_sequential(
        self,
        agent_names: List[str],
        query: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute multiple agents sequentially"""
        results = []
        
        for agent_name in agent_names:
            agent = self.agents.get(agent_name)
            if not agent:
                results.append({
                    "agent": agent_name,
                    "error": f"Agent '{agent_name}' not found",
                    "success": False
                })
                continue
            
            try:
                result = await agent.process(query, context)
                result["success"] = True
                results.append(result)
                
                # Add previous results to context for next agent
                context["previous_results"] = results
            except Exception as e:
                results.append({
                    "agent": agent_name,
                    "error": str(e),
                    "success": False
                })
        
        return results
    
    async def _execute_agent_safe(
        self,
        agent: Any,
        agent_name: str,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agent with error handling"""
        try:
            result = await agent.process(query, context)
            result["success"] = True
            return result
        except Exception as e:
            return {
                "agent": agent_name,
                "error": str(e),
                "success": False
            }
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return self.execution_history[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "avg_execution_time": 0,
                "success_rate": 0
            }
        
        total = len(self.execution_history)
        total_time = sum(e["execution_time"] for e in self.execution_history)
        
        # Count successful executions
        successful = sum(
            1 for e in self.execution_history
            if all(r.get("success", False) for r in e["results"])
        )
        
        return {
            "total_executions": total,
            "avg_execution_time": total_time / total,
            "success_rate": successful / total if total > 0 else 0,
            "strategies_used": self._count_strategies()
        }
    
    def _count_strategies(self) -> Dict[str, int]:
        """Count usage of each strategy"""
        strategies = {}
        for execution in self.execution_history:
            strategy = execution["plan"].get("strategy", "unknown")
            strategies[strategy] = strategies.get(strategy, 0) + 1
        return strategies
