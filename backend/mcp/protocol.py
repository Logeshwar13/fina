"""
MCP Protocol Layer
==================
Tool-based API interface for agent interactions.
"""

import json
import inspect
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum


class ToolType(Enum):
    """Tool categories for organization."""
    TRANSACTION = "transaction"
    BUDGET = "budget"
    RISK = "risk"
    FRAUD = "fraud"
    INSURANCE = "insurance"
    ANALYTICS = "analytics"


@dataclass
class ToolDefinition:
    """Tool metadata and schema."""
    name: str
    description: str
    category: ToolType
    parameters: Dict[str, Any]
    function: Callable
    requires_auth: bool = True
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def to_anthropic_format(self) -> Dict[str, Any]:
        """Convert to Anthropic tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters
        }


class ToolRegistry:
    """
    Central registry for all available tools.
    Manages tool registration, discovery, and execution.
    """
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.categories: Dict[ToolType, List[str]] = {cat: [] for cat in ToolType}
    
    def register(
        self,
        name: str,
        description: str,
        category: ToolType,
        parameters: Dict[str, Any],
        requires_auth: bool = True
    ):
        """
        Decorator to register a tool function.
        
        Usage:
            @tool_registry.register(
                name="get_transactions",
                description="Fetch user transactions",
                category=ToolType.TRANSACTION,
                parameters={...}
            )
            async def get_transactions(user_id: str, limit: int = 10):
                ...
        """
        def decorator(func: Callable):
            tool = ToolDefinition(
                name=name,
                description=description,
                category=category,
                parameters=parameters,
                function=func,
                requires_auth=requires_auth
            )
            self.tools[name] = tool
            self.categories[category].append(name)
            return func
        return decorator
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get tool by name."""
        return self.tools.get(name)
    
    def get_tools_by_category(self, category: ToolType) -> List[ToolDefinition]:
        """Get all tools in a category."""
        return [self.tools[name] for name in self.categories[category]]
    
    def get_all_tools(self) -> List[ToolDefinition]:
        """Get all registered tools."""
        return list(self.tools.values())
    
    def get_tool_schemas(self, format: str = "openai") -> List[Dict[str, Any]]:
        """
        Get tool schemas for LLM function calling.
        
        Args:
            format: "openai" or "anthropic"
        """
        if format == "openai":
            return [tool.to_openai_format() for tool in self.tools.values()]
        elif format == "anthropic":
            return [tool.to_anthropic_format() for tool in self.tools.values()]
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def execute_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute a tool by name with given arguments.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            context: Optional execution context (user_id, etc.)
            
        Returns:
            Tool execution result
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        
        # Inject context if needed (but filter out non-tool parameters)
        if context:
            # Only inject user_id from context, not conversation_history or other metadata
            if "user_id" in context and "user_id" not in arguments:
                arguments["user_id"] = context["user_id"]
        
        # Execute tool
        if inspect.iscoroutinefunction(tool.function):
            result = await tool.function(**arguments)
        else:
            result = tool.function(**arguments)
        
        return result
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all tools with metadata."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category.value,
                "requires_auth": tool.requires_auth,
                "parameters": tool.parameters
            }
            for tool in self.tools.values()
        ]


class ProtocolLayer:
    """
    Main protocol interface for MCP.
    Handles tool execution, context injection, and response formatting.
    """
    
    def __init__(self, tool_registry: ToolRegistry):
        self.registry = tool_registry
        self.execution_history: List[Dict[str, Any]] = []
    
    async def execute_tool_call(
        self,
        tool_call: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a single tool call from LLM.
        
        Args:
            tool_call: Tool call dict with 'function' containing 'name' and 'arguments'
            context: Execution context
            
        Returns:
            Dict with 'tool_call_id', 'output', 'error'
        """
        tool_call_id = tool_call.get("id", "unknown")
        function = tool_call.get("function", {})
        name = function.get("name")
        arguments_str = function.get("arguments", "{}")
        
        try:
            # Parse arguments
            arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
            
            # Execute tool
            result = await self.registry.execute_tool(name, arguments, context)
            
            # Record execution
            self.execution_history.append({
                "tool_call_id": tool_call_id,
                "tool_name": name,
                "arguments": arguments,
                "result": result,
                "success": True
            })
            
            return {
                "tool_call_id": tool_call_id,
                "output": result,
                "error": None
            }
            
        except Exception as e:
            # Record error
            self.execution_history.append({
                "tool_call_id": tool_call_id,
                "tool_name": name,
                "arguments": arguments_str,
                "error": str(e),
                "success": False
            })
            
            return {
                "tool_call_id": tool_call_id,
                "output": None,
                "error": str(e)
            }
    
    async def execute_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute multiple tool calls in parallel."""
        import asyncio
        tasks = [self.execute_tool_call(tc, context) for tc in tool_calls]
        return await asyncio.gather(*tasks)
    
    def format_tool_results_for_llm(
        self,
        results: List[Dict[str, Any]],
        format: str = "openai"
    ) -> List[Dict[str, Any]]:
        """
        Format tool execution results for LLM continuation.
        
        Args:
            results: List of tool execution results
            format: "openai" or "anthropic"
            
        Returns:
            List of formatted messages
        """
        if format == "openai":
            return [
                {
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": json.dumps(result["output"]) if result["output"] else f"Error: {result['error']}"
                }
                for result in results
            ]
        elif format == "anthropic":
            return [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": result["tool_call_id"],
                            "content": json.dumps(result["output"]) if result["output"] else f"Error: {result['error']}"
                        }
                    ]
                }
                for result in results
            ]
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get tool execution history."""
        return self.execution_history
    
    def clear_history(self):
        """Clear execution history."""
        self.execution_history = []


# Global tool registry instance
tool_registry = ToolRegistry()
