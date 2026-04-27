"""
MCP (Model-Context-Protocol) Package
=====================================
Core architecture for the multi-agent AI system.

Layers:
- Model: LLM + ML models
- Context: Vector DB + structured memory
- Protocol: Tool-based API interface
"""

from .model import ModelLayer
from .context import ContextLayer
from .protocol import ProtocolLayer, ToolRegistry, tool_registry
from .guardrails import GuardrailsEngine, guardrails, PromptConstraints

__all__ = [
    'ModelLayer',
    'ContextLayer', 
    'ProtocolLayer',
    'ToolRegistry',
    'tool_registry',
    'GuardrailsEngine',
    'guardrails',
    'PromptConstraints'
]
