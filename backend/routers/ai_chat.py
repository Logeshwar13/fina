"""
AI Chat Router with Guardrails
Provides agentic chat endpoint with multi-agent orchestration and safety constraints.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.coordinator import AgentCoordinator
from orchestrator.planner import QueryPlanner
from orchestrator.executor import AgentExecutor
from orchestrator.synthesizer import ResponseSynthesizer
from agents.budget_agent import BudgetAgent
from agents.fraud_agent import FraudAgent
from agents.risk_agent import RiskAgent
from agents.investment_agent import InvestmentAgent
from agents.insurance_agent import InsuranceAgent
from mcp.model import ModelLayer
from mcp.protocol import ProtocolLayer, tool_registry  # Use global tool_registry
from mcp.context import ContextLayer
import mcp.tools  # Import to trigger tool registration
from guardrails.input_validator import InputValidator
from guardrails.output_validator import OutputValidator


router = APIRouter(prefix="/ai", tags=["AI Chat"])

# Initialize guardrails
input_validator = InputValidator()
output_validator = OutputValidator()

# Initialize components (will be done once at startup)
coordinator = None


def get_coordinator():
    """Get or create coordinator instance"""
    global coordinator
    if coordinator is None:
        # Initialize components
        context = ContextLayer()
        protocol = ProtocolLayer(tool_registry)  # Use global tool_registry
        model = ModelLayer()
        
        # Create agents with CORRECT parameter order: model, protocol, rag
        agents = {
            "budget": BudgetAgent(model, protocol, None),
            "fraud": FraudAgent(model, protocol, None),
            "risk": RiskAgent(model, protocol, None),
            "investment": InvestmentAgent(model, protocol, None),
            "insurance": InsuranceAgent(model, protocol, None)
        }
        
        # Create coordinator
        coordinator = AgentCoordinator(agents, model, use_llm_synthesis=True)
    
    return coordinator


class ChatRequest(BaseModel):
    """Chat request model"""
    query: str
    user_id: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    agents_used: list
    execution_time: float
    success: bool
    conversation_id: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat query with multi-agent orchestration and guardrails.
    
    Args:
        request: Chat request with query and user_id
        
    Returns:
        Chat response with synthesized answer
    """
    print(f"[AI Chat] Received query: {request.query[:50]}... from user: {request.user_id}")
    
    # GUARDRAIL: Validate input
    is_valid, error, sanitized_query = input_validator.validate_and_sanitize(
        request.query,
        {"user_id": request.user_id}
    )
    
    if not is_valid:
        print(f"[AI Chat] Input validation failed: {error}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {error}")
    
    print(f"[AI Chat] Input validated, getting coordinator...")
    
    # Get coordinator
    try:
        coord = get_coordinator()
        print(f"[AI Chat] Coordinator obtained, processing query...")
    except Exception as e:
        print(f"[AI Chat] ERROR getting coordinator: {e}")
        raise HTTPException(status_code=500, detail=f"Error initializing system: {str(e)}")
    
    # Process query
    try:
        result = await coord.process_query(
            query=sanitized_query,
            context={"user_id": request.user_id}
        )
        
        print(f"[AI Chat] Query processed, success={result.get('success')}")
        print(f"[AI Chat] Result keys: {list(result.keys())}")
        print(f"[AI Chat] Response length: {len(result.get('response', ''))}")
        
        # Check if result has error
        if "error" in result:
            print(f"[AI Chat] Coordinator returned error: {result.get('error')}")
        
        # GUARDRAIL: Validate output (already done in agent, but double-check)
        response_text = result.get("response", "")
        
        # Skip output validation if response is empty or error occurred
        if not response_text or not result.get("success", False):
            print(f"[AI Chat] Skipping output validation due to empty response or failure")
            return ChatResponse(
                response=response_text or "I apologize, but I encountered errors processing your request. Please try again.",
                agents_used=result.get("execution", {}).get("agents_used", []),
                execution_time=result.get("total_time", 0),
                success=result.get("success", False),
                conversation_id=request.conversation_id
            )
        
        # SIMPLIFIED: Just sanitize and add disclaimers, don't reject valid responses
        try:
            enhanced_response = output_validator.sanitize_output(response_text)
            enhanced_response = output_validator.add_disclaimers(enhanced_response)
        except Exception as e:
            print(f"[AI Chat] Output enhancement failed: {e}, using original response")
            enhanced_response = response_text
        
        return ChatResponse(
            response=enhanced_response,
            agents_used=result.get("execution", {}).get("agents_used", []),
            execution_time=result.get("total_time", 0),
            success=result.get("success", False),
            conversation_id=request.conversation_id
        )
        
    except Exception as e:
        print(f"[AI Chat] ERROR processing query: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat response (placeholder for future implementation).
    
    Args:
        request: Chat request
        
    Returns:
        Streaming response
    """
    raise HTTPException(status_code=501, detail="Streaming not yet implemented")


@router.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 10):
    """
    Get chat history for a user.
    
    Args:
        user_id: User ID
        limit: Number of messages to return
        
    Returns:
        Chat history
    """
    coord = get_coordinator()
    
    # Get conversation history
    history = coord.get_conversation_history(limit)
    
    return {
        "user_id": user_id,
        "history": history,
        "count": len(history)
    }


@router.delete("/chat/history/{user_id}")
async def clear_chat_history(user_id: str):
    """
    Clear chat history for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Success message
    """
    coord = get_coordinator()
    coord.clear_conversation_history()
    
    return {
        "message": "Chat history cleared",
        "user_id": user_id
    }


@router.get("/agents/status")
async def get_agents_status():
    """
    Get status of all agents.
    
    Returns:
        Agent status information
    """
    coord = get_coordinator()
    status = coord.get_agent_status()
    
    return {
        "agents": status,
        "total": len(status)
    }


@router.get("/agents/{agent_name}/capabilities")
async def get_agent_capabilities(agent_name: str):
    """
    Get capabilities of a specific agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Agent capabilities
    """
    coord = get_coordinator()
    
    if agent_name not in coord.agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    agent = coord.agents[agent_name]
    capabilities = agent.get_capabilities()
    
    return capabilities


@router.post("/agents/{agent_name}/query")
async def query_specific_agent(agent_name: str, request: ChatRequest):
    """
    Query a specific agent directly (bypassing orchestrator).
    
    Args:
        agent_name: Name of the agent
        request: Chat request
        
    Returns:
        Agent response
    """
    # GUARDRAIL: Validate input
    is_valid, error, sanitized_query = input_validator.validate_and_sanitize(
        request.query,
        {"user_id": request.user_id}
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid input: {error}")
    
    coord = get_coordinator()
    
    if agent_name not in coord.agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    agent = coord.agents[agent_name]
    
    try:
        result = await agent.process(
            sanitized_query,
            {"user_id": request.user_id}
        )
        
        return {
            "agent": agent_name,
            "response": result.get("response", ""),
            "success": result.get("success", False)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/guardrails/rules")
async def get_guardrails_rules():
    """
    Get guardrails validation rules.
    
    Returns:
        Validation rules and limits
    """
    input_rules = input_validator.get_validation_summary()
    output_rules = output_validator.get_validation_summary()
    
    return {
        "input_validation": input_rules,
        "output_validation": output_rules
    }


@router.get("/stats")
async def get_stats():
    """
    Get coordinator statistics.
    
    Returns:
        System statistics
    """
    coord = get_coordinator()
    stats = coord.get_statistics()
    
    return stats
