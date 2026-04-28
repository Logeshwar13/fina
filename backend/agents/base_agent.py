"""
Base Agent Class with Guardrails Integration
Implements the core agent interface with plan-act-observe-reflect-respond loop.
Includes input validation, output filtering, and safety constraints.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json

# Import guardrails
from guardrails.input_validator import InputValidator
from guardrails.output_validator import OutputValidator
from guardrails.prompt_constraints import PromptConstraints


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
    Base class for all financial agents with guardrails.
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
        Initialize agent with guardrails.
        
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
        
        # Initialize guardrails
        self.input_validator = InputValidator()
        self.output_validator = OutputValidator()
        self.prompt_constraints = PromptConstraints()
        
        # Set system prompt with safety constraints
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            # Get agent-specific prompt with guardrails
            agent_type_map = {
                AgentRole.BUDGET_ADVISOR: "budget",
                AgentRole.FRAUD_DETECTOR: "fraud",
                AgentRole.RISK_ANALYST: "risk",
                AgentRole.INVESTMENT_ADVISOR: "investment",
                AgentRole.INSURANCE_ADVISOR: "insurance"
            }
            agent_type = agent_type_map.get(self.role, "general")
            self.system_prompt = self.prompt_constraints.get_complete_prompt(
                agent_type=agent_type,
                include_tools=True,
                include_rag=(rag_pipeline is not None)
            )
        
        # Agent capabilities
        self.tools = []
        self.max_iterations = 5
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a query through the agentic loop with guardrails.
        
        Args:
            query: User query
            context: Context dictionary (user_id, etc.)
            
        Returns:
            Agent response with reasoning
        """
        try:
            # GUARDRAIL: Validate and sanitize input
            is_valid, error, sanitized_query = self.input_validator.validate_and_sanitize(
                query, context
            )
            
            if not is_valid:
                print(f"[{self.name}] Input validation failed: {error}")
                return {
                    "agent": self.name,
                    "role": self.role.value,
                    "query": query,
                    "error": error,
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Use sanitized query
            query = sanitized_query
            
            # Add query to context for parameter extraction
            context["query"] = query
            
            # CRITICAL FIX: ALWAYS force tool execution for data queries
            print(f"[{self.name}] FORCING TOOL EXECUTION - Bypassing LLM planning")
            forced_actions = await self._force_tool_execution_if_needed(query, context)
            
            if forced_actions and len(forced_actions) > 0:
                # Use forced tool execution (skip planning)
                print(f"[{self.name}] ✅ Using {len(forced_actions)} forced tool calls")
                actions = forced_actions
                plan = {"steps": [{"step": i+1, "action": a.get("action", "unknown"), "purpose": "fetch data"} for i, a in enumerate(actions)], "reasoning": "Direct tool execution"}
            else:
                # Fallback: Use planning (but this should rarely happen)
                print(f"[{self.name}] ⚠️ No forced tools, using LLM planning (may not access data)")
                # Step 1: Plan
                print(f"[{self.name}] Planning...")
                plan = await self.plan(query, context)
                
                # Step 2: Act (execute tools)
                print(f"[{self.name}] Acting...")
                actions = await self.act(plan, context)
            
            # Step 3: Observe (process results)
            print(f"[{self.name}] Observing...")
            observations = await self.observe(actions)
            
            # OPTIMIZATION: Skip reflection for simple data queries
            query_lower = query.lower()
            is_simple_query = any(phrase in query_lower for phrase in [
                'how much', 'what is', 'show me', 'give me', 'tell me'
            ]) and not any(phrase in query_lower for phrase in [
                'analyze', 'recommend', 'suggest', 'advice', 'should i'
            ])
            
            if is_simple_query:
                print(f"[{self.name}] ⚡ Simple query detected - skipping reflection for speed")
                reflection = "Simple data retrieval query - no analysis needed."
            else:
                # Step 4: Reflect (analyze and learn)
                print(f"[{self.name}] Reflecting...")
                reflection = await self.reflect(query, observations, context)
            
            # Step 5: Respond (generate final answer)
            print(f"[{self.name}] Responding...")
            response = await self.respond(query, reflection, observations, context)
            
            # GUARDRAIL: Validate and enhance output (SKIP for simple queries to save time)
            if is_simple_query:
                print(f"[{self.name}] ⚡ Skipping output validation for speed")
                enhanced_response = response
            else:
                response_type_map = {
                    AgentRole.BUDGET_ADVISOR: "budget",
                    AgentRole.FRAUD_DETECTOR: "fraud",
                    AgentRole.RISK_ANALYST: "risk",
                    AgentRole.INVESTMENT_ADVISOR: "financial",
                    AgentRole.INSURANCE_ADVISOR: "financial"
                }
                response_type = response_type_map.get(self.role, "general")
                
                is_valid, error, enhanced_response = self.output_validator.validate_and_enhance(
                    response,
                    response_type=response_type,
                    context={"has_data": len(observations) > 0}
                )
                
                if not is_valid:
                    print(f"[{self.name}] Output validation failed: {error}")
                    # Fallback to safe response
                    enhanced_response = "I apologize, but I encountered an issue generating a safe response. Please try rephrasing your question."
            
            # Store in memory
            memory_entry = AgentMemory(
                timestamp=datetime.now().isoformat(),
                query=query,
                plan=plan,
                actions=actions,
                observations=observations,
                reflection=reflection,
                response=enhanced_response
            )
            self.memory.append(memory_entry)
            
            print(f"[{self.name}] Success!")
            return {
                "agent": self.name,
                "role": self.role.value,
                "query": query,
                "plan": plan,
                "actions": actions,
                "observations": observations,
                "reflection": reflection,
                "response": enhanced_response,
                "success": True,
                "timestamp": memory_entry.timestamp
            }
        except Exception as e:
            print(f"[{self.name}] ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "agent": self.name,
                "role": self.role.value,
                "query": query,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _force_tool_execution_if_needed(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Force tool execution for ALL queries - bypasses LLM planning completely.
        This is like the old chatbot - directly call tools based on keywords.
        
        Args:
            query: User query
            context: Context dictionary
            
        Returns:
            List of action results (always returns tools for this agent)
        """
        query_lower = query.lower()
        
        print(f"[{self.name}] 🔍 Analyzing query for tool selection...")
        print(f"[{self.name}] 📝 Query: {query}")
        
        # Determine which tools to call based on agent type and query
        tools_to_call = []
        
        # CHECK FOR CREATE/ACTION OPERATIONS FIRST (before read operations)
        
        # DELETE BUDGET if asking to delete/remove budget
        if any(phrase in query_lower for phrase in ['delete', 'remove']) and 'budget' in query_lower:
            if 'delete_budget' in self.tools:
                tools_to_call.append('delete_budget')
                print(f"[{self.name}] 🎯 Detected DELETE BUDGET request!")
        
        # DELETE TRANSACTION if asking to delete/remove transaction
        if any(phrase in query_lower for phrase in ['delete', 'remove']) and 'transaction' in query_lower:
            if 'delete_transaction' in self.tools:
                tools_to_call.append('delete_transaction')
                print(f"[{self.name}] 🎯 Detected DELETE TRANSACTION request!")
        
        # UPDATE BUDGET if asking to update/change/modify budget
        if any(phrase in query_lower for phrase in ['update', 'change', 'modify', 'edit']) and 'budget' in query_lower:
            if 'update_budget' in self.tools:
                tools_to_call.append('update_budget')
                print(f"[{self.name}] 🎯 Detected UPDATE BUDGET request!")
        
        # UPDATE TRANSACTION if asking to update/change/modify/edit transaction
        if any(phrase in query_lower for phrase in ['update', 'change', 'modify', 'edit']) and 'transaction' in query_lower:
            # First get transactions to find the one to update
            if 'get_transactions' in self.tools:
                tools_to_call.append('get_transactions')
            if 'update_transaction' in self.tools:
                tools_to_call.append('update_transaction')
                print(f"[{self.name}] 🎯 Detected UPDATE TRANSACTION request!")
        
        # CREATE BUDGET if asking to create/add/set budget
        if any(phrase in query_lower for phrase in ['create', 'add', 'set', 'make', 'new']) and 'budget' in query_lower and 'create_budget' not in tools_to_call and 'update_budget' not in tools_to_call:
            if 'create_budget' in self.tools:
                tools_to_call.append('create_budget')
                print(f"[{self.name}] 🎯 Detected CREATE BUDGET request!")
        
        # CREATE TRANSACTION if asking to invest/add transaction/spent
        # STRICT DETECTION: Only create if explicitly asking to add/create
        transaction_create_phrases = [
            'add transaction', 'create transaction', 'add a transaction',
            'create a transaction', 'new transaction', 'i spent', 'i bought',
            'i purchased', 'i paid', 'invest', 'buy', 'purchase'
        ]
        
        has_explicit_create = any(phrase in query_lower for phrase in transaction_create_phrases)
        
        # Also detect "add" with amount AND category (very specific)
        has_add_with_amount_and_category = (
            'add' in query_lower and 
            ('rs' in query_lower or '₹' in query_lower) and
            any(word in query_lower for word in ['food', 'shopping', 'movie', 'entertainment', 'transport'])
        )
        
        if (has_explicit_create or has_add_with_amount_and_category) and 'delete_transaction' not in tools_to_call and 'budget' not in query_lower:
            if 'create_transaction' in self.tools:
                tools_to_call.append('create_transaction')
                print(f"[{self.name}] 🎯 Detected CREATE TRANSACTION request!")
        
        # NOW CHECK FOR READ OPERATIONS (only if no create operations detected)
        
        # ALWAYS get transactions if asking about spending/transactions/food/last
        if any(word in query_lower for word in ['transaction', 'spending', 'spent', 'expense', 'last', 'recent', 'food', 'dining', 'merchant', 'what', 'show', 'tell']):
            if 'get_transactions' in self.tools and 'get_transactions' not in tools_to_call:
                tools_to_call.append('get_transactions')
            if 'get_transaction_stats' in self.tools and 'get_transaction_stats' not in tools_to_call:
                tools_to_call.append('get_transaction_stats')
        
        # Get budgets if asking about budgets (but NOT if creating)
        if 'budget' in query_lower and 'create_budget' not in tools_to_call:
            if 'get_budgets' in self.tools and 'get_budgets' not in tools_to_call:
                tools_to_call.append('get_budgets')
        
        # Get fraud alerts if asking about fraud
        if any(word in query_lower for word in ['fraud', 'fraudulent', 'suspicious']):
            if 'get_fraud_alerts' in self.tools and 'get_fraud_alerts' not in tools_to_call:
                tools_to_call.append('get_fraud_alerts')
        
        # Get risk score if asking about risk
        if any(word in query_lower for word in ['risk', 'score', 'health']):
            if 'get_risk_score' in self.tools and 'get_risk_score' not in tools_to_call:
                tools_to_call.append('get_risk_score')
        
        # Get insurance if asking about insurance
        if any(word in query_lower for word in ['insurance', 'policy']):
            if 'get_insurance_policies' in self.tools and 'get_insurance_policies' not in tools_to_call:
                tools_to_call.append('get_insurance_policies')
        
        # If no specific tools matched, ALWAYS use agent's primary tools
        if not tools_to_call:
            print(f"[{self.name}] ⚠️ No keyword match, using agent's primary tools")
            # Use first 2 tools from agent's toolset
            tools_to_call = self.tools[:min(2, len(self.tools))]
        
        print(f"[{self.name}] 🔧 Selected tools: {tools_to_call}")
        
        # Execute tools directly
        actions = []
        for tool_name in tools_to_call:
            try:
                print(f"[{self.name}] ⚙️ Executing tool: {tool_name}")
                result = await self.protocol.registry.execute_tool(
                    name=tool_name,
                    arguments=self._prepare_tool_arguments(tool_name, context),
                    context=context
                )
                
                actions.append({
                    "step": len(actions) + 1,
                    "action": tool_name,
                    "status": "success",
                    "result": result
                })
                print(f"[{self.name}] ✅ Tool {tool_name} executed successfully - got {len(str(result))} chars of data")
            except Exception as e:
                print(f"[{self.name}] ❌ Tool {tool_name} failed: {str(e)}")
                import traceback
                traceback.print_exc()
                actions.append({
                    "step": len(actions) + 1,
                    "action": tool_name,
                    "status": "error",
                    "error": str(e)
                })
        
        print(f"[{self.name}] 📊 Executed {len(actions)} tools, {len([a for a in actions if a['status'] == 'success'])} successful")
        return actions
    
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
            # Try to extract JSON from response
            content = response["content"]
            # Sometimes LLM wraps JSON in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            plan = json.loads(content)
        except Exception as e:
            # Fallback plan - use actual tools
            print(f"[{self.name}] Plan parsing failed, using fallback with real tools")
            # Create a simple plan that uses the agent's primary tools
            fallback_steps = []
            if "get_transactions" in self.tools:
                fallback_steps.append({"step": 1, "action": "get_transactions", "purpose": "fetch transaction data"})
            if "get_budgets" in self.tools:
                fallback_steps.append({"step": 2, "action": "get_budgets", "purpose": "fetch budget data"})
            if "get_transaction_stats" in self.tools:
                fallback_steps.append({"step": 3, "action": "get_transaction_stats", "purpose": "get statistics"})
            
            # If no tools matched, use first available tool
            if not fallback_steps and self.tools:
                fallback_steps.append({"step": 1, "action": self.tools[0], "purpose": "gather data"})
            
            plan = {
                "steps": fallback_steps if fallback_steps else [{"step": 1, "action": "analyze", "purpose": "answer query"}],
                "reasoning": "Fallback plan using available tools"
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
        # Only pass user_id - let tools use their defaults for other params
        # Filter out conversation_history and other non-tool parameters
        args = {
            "user_id": context.get("user_id", "")
        }
        
        # Add optional parameters only if the tool expects them
        # Tools will use their default values if not provided
        if tool_name == "get_transactions":
            args["limit"] = 50
        elif tool_name == "get_transaction_stats":
            args["period"] = "month"
        elif tool_name == "analyze_budget_trends":
            args["months"] = 3
        elif tool_name == "create_budget":
            # Extract category and amount from query
            query = context.get("query", "").lower()
            print(f"[{self.name}] 🔍 Parsing query for create_budget: '{query}'")
            
            # Extract amount (look for numbers)
            import re
            amount_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)', query)
            if amount_match:
                amount_str = amount_match.group(1).replace(',', '')
                args["limit_amount"] = float(amount_str)
                print(f"[{self.name}] 💰 Amount extracted: {args['limit_amount']}")
            else:
                args["limit_amount"] = 10000  # Default
                print(f"[{self.name}] ⚠️ No amount found, using default: 10000")
            
            # Extract category - try multiple strategies
            # Strategy 1: Look for known categories in the query
            categories = ['entertainment', 'food', 'dining', 'healthcare', 'health', 'transportation', 
                         'shopping', 'utilities', 'rent', 'education', 'travel', 'savings', 'investment']
            
            category_found = None
            for cat in categories:
                if cat in query:
                    category_found = cat.title()
                    # Special handling for healthcare/health
                    if cat in ['healthcare', 'health']:
                        category_found = 'Healthcare'
                    break
            
            # Special handling for compound categories
            if 'food' in query and 'dining' in query:
                category_found = 'Food & Dining'
            
            # Strategy 2: If not found, try regex for word before "budget" (but skip common words)
            if not category_found:
                skip_words = ['the', 'a', 'an', 'that', 'this', 'my', 'your', 'our']
                # Find all words before "budget"
                words_before_budget = re.findall(r'(\w+)\s+budget', query)
                for word in words_before_budget:
                    if word.lower() not in skip_words:
                        category_found = word.title()
                        break
            
            if category_found:
                args["category"] = category_found
                print(f"[{self.name}] 🏷️ Category extracted: {args['category']}")
            else:
                args["category"] = "Other"
                print(f"[{self.name}] ⚠️ No category found, using default: Other")
            
            print(f"[{self.name}] 📝 Final create_budget params: category={args.get('category')}, amount={args.get('limit_amount')}")
        
        elif tool_name == "create_transaction":
            # Extract transaction details from query
            query = context.get("query", "").lower()
            original_query = context.get("query", "")  # Keep original for merchant name
            
            # Extract amount
            import re
            amount_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)', query)
            if amount_match:
                amount_str = amount_match.group(1).replace(',', '')
                args["amount"] = float(amount_str)
            else:
                args["amount"] = 1000  # Default
            
            # Determine type (expense or income)
            # PRIORITY 1: Check for explicit "as income" or "income" keywords
            if 'as income' in query or 'type income' in query or 'income for' in query:
                args["type"] = "income"
                print(f"[{self.name}] 💰 Detected INCOME transaction")
            # PRIORITY 2: Check for explicit "as expense" or "expense" keywords
            elif 'as expense' in query or 'type expense' in query or 'expense for' in query:
                args["type"] = "expense"
                print(f"[{self.name}] 💸 Detected EXPENSE transaction")
            # PRIORITY 3: Check for action words that imply expense
            elif any(word in query for word in ['buy', 'purchase', 'spent', 'paid']):
                args["type"] = "expense"
            # DEFAULT: expense
            else:
                args["type"] = "expense"
            
            # Extract merchant/description - look for "at [merchant]" or "food at [merchant]"
            merchant_match = re.search(r'(?:food|shopping|movie|dinner|lunch)\s+at\s+(\w+)', query, re.IGNORECASE)
            if merchant_match:
                merchant_name = merchant_match.group(1).title()
                args["description"] = f"Food at {merchant_name}"
                args["category"] = "Food & Dining"
                print(f"[{self.name}] 🏪 Merchant extracted: {merchant_name}")
            # Extract category based on keywords
            elif 'invest' in query or 'investment' in query:
                args["category"] = "Investments"
                args["description"] = "Investment via AI agent"
            elif 'gold' in query:
                args["category"] = "Investments"
                args["description"] = "Gold investment"
            elif 'stock' in query:
                args["category"] = "Investments"
                args["description"] = "Stock investment"
            elif 'food' in query or 'groceries' in query or 'restaurant' in query or 'dining' in query:
                args["category"] = "Food & Dining"
                if "description" not in args:
                    args["description"] = "Food purchase"
            elif 'shopping' in query or 'shop' in query:
                args["category"] = "Shopping"
                args["description"] = "Shopping"
            elif 'movie' in query or 'cinema' in query:
                args["category"] = "Entertainment"
                args["description"] = "Movie"
            elif 'transport' in query or 'uber' in query or 'taxi' in query:
                args["category"] = "Transportation"
                args["description"] = "Transportation"
            else:
                args["category"] = "Other"
                args["description"] = "Transaction via AI agent"
            
            # Set default description if not set
            if "description" not in args:
                args["description"] = f"{args['category']} via AI agent"
            
            args["location"] = "Online"
            
            print(f"[{self.name}] 📝 Extracted create_transaction params: amount={args.get('amount')}, category={args.get('category')}")
        
        elif tool_name == "update_transaction":
            # Extract transaction ID and fields to update
            query = context.get("query", "").lower()
            
            # Check if updating "last" or "recent" transaction
            if "last" in query or "latest" in query or "recent" in query:
                args["use_last"] = True
                print(f"[{self.name}] 🔍 Will update last transaction")
            
            # Check if there's a description to search by
            if "food at" in query or "shopping at" in query:
                # Extract merchant name
                import re
                merchant_match = re.search(r'(?:food|shopping)\s+at\s+(\w+)', query, re.IGNORECASE)
                if merchant_match:
                    args["find_by_description"] = merchant_match.group(1)
                    print(f"[{self.name}] 🔍 Will find transaction by description: {args['find_by_description']}")
            
            # Extract what to update
            # Check for type change (expense <-> income)
            if any(phrase in query for phrase in ['to income', 'as income', 'change to income', 'type income', 'make it income']):
                args["type"] = "income"
                print(f"[{self.name}] 🔄 Updating type to: income")
            elif any(phrase in query for phrase in ['to expense', 'as expense', 'change to expense', 'type expense', 'make it expense']):
                args["type"] = "expense"
                print(f"[{self.name}] 🔄 Updating type to: expense")
            
            # Extract category if present
            if "category" in query or "to food" in query or "to shopping" in query:
                categories = {
                    'food': 'Food & Dining',
                    'shopping': 'Shopping',
                    'entertainment': 'Entertainment',
                    'healthcare': 'Healthcare',
                    'health': 'Healthcare',
                    'transportation': 'Transportation',
                    'transport': 'Transportation',
                    'utilities': 'Utilities',
                    'investment': 'Investments',
                    'investments': 'Investments'
                }
                
                for keyword, category_name in categories.items():
                    if keyword in query:
                        args["category"] = category_name
                        print(f"[{self.name}] 🏷️ Updating category to: {category_name}")
                        break
            
            # Extract amount if present
            import re
            amount_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)', query)
            if amount_match and ("amount" in query or "to" in query):
                amount_str = amount_match.group(1).replace(',', '')
                args["amount"] = float(amount_str)
                print(f"[{self.name}] 💰 Updating amount to: {args['amount']}")
            
            print(f"[{self.name}] 📝 Update transaction params: {args}")
        
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
        Analyze observations - uses rule-based analysis to save LLM tokens.
        Only calls LLM for complex analysis queries.
        """
        query_lower = query.lower()
        
        # For ALL data retrieval queries - skip LLM, use rule-based reflection
        is_data_query = any(phrase in query_lower for phrase in [
            'how much', 'what is', 'show me', 'give me', 'tell me',
            'list', 'display', 'total', 'spent', 'spending', 'transactions',
            'budget', 'last', 'recent', 'add', 'create', 'update', 'edit',
            'delete', 'remove', 'food', 'movie', 'shopping', 'income', 'expense'
        ])
        
        # Only use LLM for complex analysis
        is_analysis_query = any(phrase in query_lower for phrase in [
            'analyze', 'should i', 'recommend', 'advice', 'suggest',
            'why', 'how can i improve', 'what should'
        ])
        
        if is_data_query and not is_analysis_query:
            # Build reflection from data without LLM call
            summary_parts = []
            for obs in observations:
                summary_parts.append(obs.get('summary', ''))
            return "Data retrieved: " + "; ".join(summary_parts)
        
        # Only call LLM for genuine analysis queries
        obs_text = "\n".join([f"- {obs['action']}: {obs['summary']}" for obs in observations])
        
        reflection_prompt = f"""Briefly analyze (2-3 sentences max):

Query: {query}
Data: {obs_text}

Key insight only."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": reflection_prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.5,
            max_tokens=150  # Very short for reflection
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
        # CRITICAL: Extract actual data from observations
        actual_data = self._extract_actual_data_from_observations(observations)
        
        # Format data for response
        data_summary = "\n".join([
            f"- {obs['summary']}"
            for obs in observations
        ])
        
        # DETECT QUERY TYPE to determine response length
        query_lower = query.lower()
        
        # Check if user wants ONLY specific data (concise response)
        wants_concise = any(phrase in query_lower for phrase in [
            'only', 'just', 'give me', 'show me', 'what is', 'how much',
            'tell me', 'list', 'display', 'quick', 'brief'
        ])
        
        # Check if user wants FULL/DETAILED data
        wants_detailed = any(phrase in query_lower for phrase in [
            'all', 'everything', 'complete', 'full', 'detailed', 'entire',
            'whole', 'every', 'total', 'summary', 'breakdown', 'analysis'
        ])
        
        # Check if asking about specific time period (month, week, etc.)
        has_time_period = any(phrase in query_lower for phrase in [
            'month', 'week', 'year', 'today', 'yesterday', 'last', 'this'
        ])
        
        # Determine response style
        if wants_concise and not wants_detailed:
            response_style = "CONCISE"
            max_tokens = 200  # Reduced from 300
            style_instruction = """
RESPONSE STYLE: ULTRA CONCISE (Maximum 3-4 lines ONLY)

CRITICAL RULES - YOU MUST FOLLOW THESE EXACTLY:
1. Maximum 3-4 lines total (NOT 3-4 lines per section!)
2. NO introductions ("Here are...", "Let me show you...")
3. NO recommendations or advice
4. NO explanations or analysis
5. NO "Let me know if you need anything else"
6. NO disclaimers
7. NO totals unless specifically asked
8. Show ONLY what was asked - nothing more

If showing transactions:
- Show ONLY 1-3 transactions maximum
- Format: "₹amount - merchant - date"
- One line per transaction
- NO category, location, or description unless asked

If showing amounts:
- Format: "Category: ₹amount"
- One line only

Examples:

Query: "Show me my last transaction"
Response: "₹450 - Shopping - April 27, 2026"

Query: "How much did I spend on food?"
Response: "Food & Dining: ₹3,588"

Query: "What is my food budget?"
Response: "Food budget: ₹15,000
Spent: ₹3,588
Remaining: ₹11,412"

REMEMBER: Maximum 3-4 lines total. Be extremely brief.
"""
        elif wants_detailed or has_time_period:
            response_style = "DETAILED"
            max_tokens = 1000  # Reduced from 1200
            style_instruction = """
RESPONSE STYLE: DETAILED

The user wants comprehensive information with full details.

RULES:
1. Show ALL relevant transactions (up to 10-12)
2. Include full details: amount, merchant, date, category
3. Add totals and summaries
4. Provide brief insights (2-3 lines max)
5. Use proper formatting with sections
6. Add blank lines between sections
7. Keep recommendations to 2-3 bullet points maximum
"""
        else:
            response_style = "BALANCED"
            max_tokens = 500  # Reduced from 800
            style_instruction = """
RESPONSE STYLE: BALANCED

Provide a helpful response with key data and brief insights.

RULES:
1. Show 3-5 most relevant items only
2. Include key details (amount, merchant, date)
3. Add a brief total if relevant
4. Maximum 1-2 recommendations
5. Keep it readable and well-formatted
6. Total response should be 6-8 lines maximum
"""
        
        response_prompt = f"""Generate a response to the user's query using the ACTUAL DATA provided.

User Query: {query}

ACTUAL DATA FROM DATABASE:
{actual_data}

{style_instruction}

CRITICAL: Follow the response style rules EXACTLY. Do not add extra content.

If CONCISE mode:
- Maximum 3-4 lines total
- NO introductions, NO recommendations, NO disclaimers
- Show ONLY the requested data

If DETAILED mode:
- Show full transaction list with details
- Add totals and brief insights

If BALANCED mode:
- Show 3-5 items with key details
- Keep total response under 8 lines

Format with proper line breaks between items."""
        
        messages = [
            {"role": "system", "content": self.system_prompt + f"\n\nCRITICAL: Response style is {response_style}. Follow the length restrictions EXACTLY. Do not exceed the specified line count."},
            {"role": "user", "content": response_prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens
        )
        
        generated_response = response["content"]
        
        # POST-PROCESSING: Forcefully truncate if response is too long
        if response_style == "CONCISE":
            generated_response = self._force_concise_response(generated_response, query)
        elif response_style == "BALANCED":
            generated_response = self._force_balanced_response(generated_response)
        
        return generated_response
    
    def _force_concise_response(self, response: str, query: str) -> str:
        """
        Forcefully make response concise by removing extra content.
        This is a safety net when LLM doesn't follow instructions.
        """
        lines = response.strip().split('\n')
        
        # Remove empty lines
        lines = [line for line in lines if line.strip()]
        
        # Remove common fluff phrases (case insensitive)
        fluff_phrases = [
            "here are", "let me", "i found", "based on", "please note",
            "recommendations:", "actionable steps:", "financial summary:",
            "note that", "it is essential", "please let me know",
            "disclaimer:", "⚠️", "let me know if", "feel free",
            "your recent", "transactions:", "category:", "type:", "location:",
            "description:", "total:", "however", "considering", "although"
        ]
        
        filtered_lines = []
        for line in lines:
            line_lower = line.lower().strip()
            
            # Skip lines that start with fluff phrases
            if any(line_lower.startswith(phrase) for phrase in fluff_phrases):
                continue
            
            # Skip lines with fluff phrases anywhere
            if any(phrase in line_lower for phrase in [
                "recommendations:", "actionable steps:", "financial summary:",
                "please let me know", "feel free", "disclaimer:", "⚠️",
                "note that", "it is essential", "however", "considering"
            ]):
                continue
            
            # Skip recommendation bullets
            if line.strip().startswith('•') or line.strip().startswith('-'):
                if any(word in line_lower for word in ['consider', 'monitor', 'track', 'review', 'recommend']):
                    continue
            
            # Skip numbered recommendation lists
            if re.match(r'^\d+\.', line.strip()):
                if any(word in line_lower for word in ['review', 'prioritize', 'consider', 'reduce']):
                    continue
            
            # Skip lines with "Category:", "Type:", "Location:", "Description:" (detail lines)
            if any(detail in line for detail in ['Category:', 'Type:', 'Location:', 'Description:']):
                continue
            
            filtered_lines.append(line)
        
        # For "how much" or "what is" queries, return ONLY the amount/total
        query_lower = query.lower()
        if any(phrase in query_lower for phrase in ['how much', 'what is', 'tell me the', 'total']):
            # Find lines with amounts (₹)
            amount_lines = [line for line in filtered_lines if '₹' in line]
            if amount_lines:
                # Return ONLY first 1-2 lines with amounts
                return '\n'.join(amount_lines[:2])
        
        # For "show me" queries, return max 3 lines
        if 'show me' in query_lower or 'give me' in query_lower:
            return '\n'.join(filtered_lines[:3])
        
        # Default: return max 3 lines
        return '\n'.join(filtered_lines[:3])
    
    def _force_balanced_response(self, response: str) -> str:
        """
        Forcefully limit balanced responses to 8 lines.
        """
        lines = response.strip().split('\n')
        lines = [line for line in lines if line.strip()]
        
        # Remove disclaimer lines
        lines = [line for line in lines if '⚠️' not in line and 'disclaimer' not in line.lower()]
        
        # Limit to 8 lines
        if len(lines) > 8:
            return '\n'.join(lines[:8])
        
        return '\n'.join(lines)
    
    def _extract_actual_data_from_observations(self, observations: List[Dict[str, Any]]) -> str:
        """
        Extract actual data from observations and format it clearly.
        This ensures the LLM sees the real data.
        """
        if not observations:
            return "No data available."
        
        formatted_data = []
        
        for obs in observations:
            data = obs.get("data", {})
            action = obs.get("action", "")
            
            # Format transactions
            if "transactions" in data:
                transactions = data["transactions"]
                formatted_data.append(f"\n{'='*60}")
                formatted_data.append(f"TRANSACTIONS ({len(transactions)} found)")
                formatted_data.append(f"{'='*60}")
                
                if transactions:
                    total = 0
                    for i, txn in enumerate(transactions[:30], 1):  # Show first 30
                        amount = txn.get("amount", 0)
                        desc = txn.get("description", "N/A")
                        merchant = txn.get("merchant", desc)  # Use description if no merchant
                        category = txn.get("category", "N/A")
                        timestamp = txn.get("timestamp", "")[:10]  # Just date
                        txn_type = txn.get("type", "expense")
                        location = txn.get("location", "N/A")
                        
                        formatted_data.append(
                            f"{i}. ₹{amount} - {merchant} - {timestamp}\n"
                            f"   Category: {category}, Type: {txn_type}, Location: {location}\n"
                            f"   Description: {desc}"
                        )
                        total += amount
                    
                    formatted_data.append(f"\n💰 TOTAL: ₹{total}")
                else:
                    formatted_data.append("No transactions found.")
            
            # Format budgets
            if "budgets" in data:
                budgets = data["budgets"]
                formatted_data.append(f"\n{'='*60}")
                formatted_data.append(f"BUDGETS ({len(budgets)} found)")
                formatted_data.append(f"{'='*60}")
                
                if budgets:
                    for i, budget in enumerate(budgets, 1):
                        category = budget.get("category", "N/A")
                        limit = budget.get("limit", budget.get("limit_amount", 0))
                        spent = budget.get("spent", 0)
                        remaining = budget.get("remaining", limit - spent)
                        percentage = budget.get("percentage_used", 0)
                        status = budget.get("status", "unknown")
                        
                        status_emoji = "🔴" if status == "over_budget" else "🟡" if status == "warning" else "🟢"
                        
                        formatted_data.append(
                            f"{i}. {category}: ₹{limit} limit\n"
                            f"   Spent: ₹{spent}, Remaining: ₹{remaining}\n"
                            f"   Usage: {percentage:.1f}% {status_emoji} {status}"
                        )
                else:
                    formatted_data.append("No budgets found.")
            
            # Format risk score
            if "score" in data or "risk_score" in data:
                score = data.get("score", data.get("risk_score", 0))
                grade = data.get("grade", "N/A")
                label = data.get("label", "N/A")
                formatted_data.append(f"\n{'='*60}")
                formatted_data.append(f"RISK SCORE")
                formatted_data.append(f"{'='*60}")
                formatted_data.append(f"Score: {score}/100")
                formatted_data.append(f"Grade: {grade}")
                formatted_data.append(f"Label: {label}")
                
                if "breakdown" in data:
                    formatted_data.append("\nBreakdown:")
                    for key, value in data["breakdown"].items():
                        formatted_data.append(f"  - {key}: {value}")
            
            # Format fraud alerts
            if "fraud_count" in data or "flagged_transactions" in data:
                count = data.get("fraud_count", 0)
                formatted_data.append(f"\n{'='*60}")
                formatted_data.append(f"FRAUD ALERTS ({count} found)")
                formatted_data.append(f"{'='*60}")
                
                if count > 0 and "flagged_transactions" in data:
                    for i, txn in enumerate(data["flagged_transactions"][:10], 1):
                        amount = txn.get("amount", 0)
                        desc = txn.get("description", "N/A")
                        timestamp = txn.get("timestamp", "")[:10]
                        fraud_score = txn.get("fraud_score", 0)
                        txn_id = txn.get("id", "N/A")
                        
                        formatted_data.append(
                            f"{i}. ₹{amount} - {desc} - {timestamp}\n"
                            f"   Fraud Score: {fraud_score}, ID: {txn_id}"
                        )
                else:
                    formatted_data.append("✅ No fraudulent transactions detected!")
            
            # Format insurance policies
            if "policies" in data:
                policies = data["policies"]
                formatted_data.append(f"\n{'='*60}")
                formatted_data.append(f"INSURANCE POLICIES ({len(policies)} found)")
                formatted_data.append(f"{'='*60}")
                
                if policies:
                    for i, policy in enumerate(policies, 1):
                        policy_type = policy.get("policy_type", "N/A")
                        premium = policy.get("premium_amount", 0)
                        coverage = policy.get("coverage_amount", 0)
                        status = policy.get("status", "N/A")
                        
                        formatted_data.append(
                            f"{i}. {policy_type}\n"
                            f"   Premium: ₹{premium}, Coverage: ₹{coverage}\n"
                            f"   Status: {status}"
                        )
                else:
                    formatted_data.append("No insurance policies found.")
            
            # Format stats
            if "total_income" in data or "total_expenses" in data:
                formatted_data.append(f"\n{'='*60}")
                formatted_data.append(f"FINANCIAL STATS")
                formatted_data.append(f"{'='*60}")
                if "total_income" in data:
                    formatted_data.append(f"Total Income: ₹{data['total_income']}")
                if "total_expenses" in data:
                    formatted_data.append(f"Total Expenses: ₹{data['total_expenses']}")
                if "balance" in data:
                    formatted_data.append(f"Balance: ₹{data['balance']}")
                if "net_savings" in data:
                    formatted_data.append(f"Net Savings: ₹{data['net_savings']}")
                if "category_breakdown" in data:
                    formatted_data.append("\nCategory Breakdown:")
                    for cat, amount in data["category_breakdown"].items():
                        formatted_data.append(f"  - {cat}: ₹{amount}")
        
        return "\n".join(formatted_data) if formatted_data else "No detailed data available."
    
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
            "has_guardrails": True,
            "memory_size": len(self.memory)
        }
