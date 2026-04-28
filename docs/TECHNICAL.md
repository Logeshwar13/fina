# Technical Deep Dive

Complete technical documentation of the FinA system architecture, implementation details, and workflows.

## Table of Contents

1. [Backend Architecture](#backend-architecture)
2. [Frontend Architecture](#frontend-architecture)
3. [Multi-Agent System](#multi-agent-system)
4. [MCP Layer](#mcp-layer)
5. [RAG Pipeline](#rag-pipeline)
6. [Database Schema](#database-schema)
7. [API Workflows](#api-workflows)
8. [Security](#security)

---

## Backend Architecture

### Technology Stack
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11
- **Database**: PostgreSQL (via Supabase)
- **Cache**: Redis
- **LLM**: Groq (llama-3.3-70b-versatile)
- **Monitoring**: Prometheus + Grafana

### Directory Structure
```
backend/
├── agents/              # AI Agent implementations
│   ├── base_agent.py    # Base agent with agentic loop
│   ├── budget_agent.py  # Budget management specialist
│   ├── fraud_agent.py   # Fraud detection specialist
│   ├── risk_agent.py    # Risk analysis specialist
│   ├── investment_agent.py
│   └── insurance_agent.py
├── api/                 # API layer
│   ├── auth.py          # Authentication endpoints
│   ├── endpoints.py     # CRUD endpoints
│   ├── websocket.py     # Real-time communication
│   └── webhooks.py      # External integrations
├── database/            # Database layer
│   ├── db.py            # Supabase client
│   └── models.py        # Pydantic models
├── guardrails/          # Safety layer
│   ├── input_validator.py
│   ├── output_validator.py
│   └── prompt_constraints.py
├── mcp/                 # Model Context Protocol
│   ├── model.py         # LLM interface
│   ├── protocol.py      # Tool registry
│   ├── context.py       # Context management
│   └── tools.py         # Tool definitions
├── ml/                  # Machine learning
│   ├── categorizer.py   # Transaction categorization
│   ├── fraud_detector.py # Fraud detection model
│   └── risk_scorer.py   # Risk scoring
├── observability/       # Monitoring
│   ├── logger.py        # Structured logging
│   ├── metrics.py       # Prometheus metrics
│   └── tracer.py        # Distributed tracing
├── orchestrator/        # Multi-agent coordination
│   ├── coordinator.py   # Agent coordination
│   ├── planner.py       # Query planning
│   ├── executor.py      # Parallel execution
│   └── synthesizer.py   # Response synthesis
├── rag/                 # RAG pipeline
│   ├── embedder.py      # Text embeddings
│   ├── indexer.py       # Vector indexing
│   ├── retriever.py     # Similarity search
│   └── pipeline.py      # End-to-end pipeline
└── main.py              # FastAPI application
```

### Core Components

#### 1. FastAPI Application (`main.py`)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FinA API", version="1.0.0")

# Middleware
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(GuardrailsMiddleware, ...)
app.add_middleware(ErrorHandlerMiddleware, ...)

# Routers
app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(budgets_router)
app.include_router(ai_chat_router)
```

#### 2. Database Layer (`database/db.py`)
```python
from supabase import create_client

def get_supabase():
    return create_client(
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY
    )
```

**Features**:
- Connection pooling
- Row-Level Security (RLS)
- Real-time subscriptions
- Automatic timestamps

---

## Frontend Architecture

### Technology Stack
- **Framework**: Vanilla JavaScript (ES6+)
- **Router**: Custom SPA router
- **State Management**: AuthState singleton
- **HTTP Client**: Fetch API with wrapper
- **Styling**: Custom CSS with CSS Variables

### Directory Structure
```
public/
├── css/
│   └── style-new.css    # Main stylesheet
├── js/
│   ├── app-new.js       # Main app & router
│   ├── auth.js          # Authentication state
│   ├── utils.js         # HTTP client & utilities
│   ├── components/      # Reusable components
│   └── views/           # Page views
│       ├── dashboard-new.js
│       ├── transactions-new.js
│       ├── budget-new.js
│       ├── ai-chat-new.js
│       └── ...
└── index-new.html       # Main HTML file
```

### Router Implementation
```javascript
// app-new.js
const routes = {
    'dashboard': () => import('./views/dashboard-new.js'),
    'transactions': () => import('./views/transactions-new.js'),
    'ai-chat': () => import('./views/ai-chat-new.js?v=18'),
    // ...
};

async function router() {
    const path = window.location.hash.slice(1) || 'dashboard';
    const view = await routes[path]();
    document.getElementById('router-view').innerHTML = view();
}
```

### State Management
```javascript
// auth.js
export const authState = {
    _state: { user: null, token: null },
    
    get() { return this._state; },
    
    set(newState) {
        this._state = { ...this._state, ...newState };
        localStorage.setItem('auth', JSON.stringify(this._state));
    },
    
    clear() {
        this._state = { user: null, token: null };
        localStorage.removeItem('auth');
    }
};
```

### HTTP Client
```javascript
// utils.js
export async function apiFetch(endpoint, options = {}) {
    const { token } = authState.get();
    
    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : '',
            ...options.headers
        }
    });
    
    if (!response.ok) throw new Error(await response.text());
    return response.json();
}
```

---

## Multi-Agent System

### Agent Architecture

Each agent follows the **Agentic Loop** pattern - a 5-step reasoning cycle that enables autonomous decision-making and action execution.

### The Agentic Loop

```
┌─────────────────────────────────────────┐
│         User Query                       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  1. PLAN                                 │
│     - Detect intent (CREATE/READ/etc)    │
│     - Select appropriate tools           │
│     - Create execution strategy          │
│     - Use RAG for context                │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  2. ACT                                  │
│     - Execute selected tools             │
│     - Call database APIs                 │
│     - Gather financial data              │
│     - Handle errors gracefully           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  3. OBSERVE                              │
│     - Process tool results               │
│     - Structure data into insights       │
│     - Extract key metrics                │
│     - Identify patterns                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  4. REFLECT                              │
│     - Analyze observations               │
│     - Generate financial insights        │
│     - Compare with goals/budgets         │
│     - Identify recommendations           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  5. RESPOND                              │
│     - Format user-friendly response      │
│     - Add actionable recommendations     │
│     - Include data sources               │
│     - Apply guardrails for safety        │
└──────────────────────────────────────────┘
```

### Real-World Examples

#### Example 1: Budget Creation

**User Query**: "Create a budget for Food with ₹15,000"

**1. PLAN Phase**
```python
# Agent detects intent
intent = "CREATE_BUDGET"
# Extracts parameters
params = {
    "category": "Food",
    "limit_amount": 15000,
    "user_id": "ad200e5a-3d99-4d9f-850b-22ae2563bcc4"
}
# Selects tool
tool = "create_budget"
```

**2. ACT Phase**
```python
# Execute tool
result = await tool_registry.execute_tool(
    name="create_budget",
    arguments=params,
    context={"user_id": user_id}
)
# Result: {"success": True, "budget": {"id": "...", "category": "Food", ...}}
```

**3. OBSERVE Phase**
```python
# Process result
observations = {
    "budget_created": True,
    "budget_id": result["budget"]["id"],
    "category": "Food",
    "limit": 15000,
    "current_spending": 0
}
```

**4. REFLECT Phase**
```python
# Generate insights
reflection = """
Budget successfully created for Food category.
User can now track spending against ₹15,000 limit.
Recommend setting up alerts at 80% threshold.
"""
```

**5. RESPOND Phase**
```python
# Format response
response = """
✅ Budget created successfully!

Category: Food
Monthly Limit: ₹15,000
Current Spending: ₹0
Remaining: ₹15,000

I'll help you track your food expenses and alert you when you're approaching the limit.
"""
```

#### Example 2: Spending Analysis

**User Query**: "How much did I spend on food last month?"

**1. PLAN Phase**
```python
intent = "ANALYZE_SPENDING"
params = {
    "category": "Food",
    "time_period": "last_month",
    "user_id": user_id
}
tools = ["get_transactions", "analyze_budget_trends"]
# Also use RAG to retrieve relevant transactions
```

**2. ACT Phase**
```python
# Execute multiple tools in parallel
transactions = await get_transactions(
    user_id=user_id,
    category="Food",
    start_date="2026-03-01",
    end_date="2026-03-31"
)

# RAG retrieval for context
rag_context = await rag_pipeline.query(
    query="food spending last month",
    user_id=user_id,
    top_k=10
)
```

**3. OBSERVE Phase**
```python
observations = {
    "total_spent": sum(t["amount"] for t in transactions),
    "transaction_count": len(transactions),
    "top_merchants": ["Starbucks", "McDonald's", "Grocery Store"],
    "average_transaction": 450,
    "budget_limit": 15000,
    "budget_used_percent": 16.67
}
```

**4. REFLECT Phase**
```python
reflection = """
User spent ₹2,500 on food last month (16.67% of budget).
This is well within the ₹15,000 limit.
Spending pattern is healthy with good budget adherence.
Top spending: Coffee shops (₹800), Restaurants (₹1,200), Groceries (₹500).
"""
```

**5. RESPOND Phase**
```python
response = """
📊 Food Spending Analysis - March 2026

Total Spent: ₹2,500
Budget: ₹15,000
Used: 16.67% ✅

Breakdown:
• Restaurants: ₹1,200 (48%)
• Coffee Shops: ₹800 (32%)
• Groceries: ₹500 (20%)

Top Merchants:
1. Starbucks - ₹800
2. McDonald's - ₹400
3. Grocery Store - ₹500

💡 Insights:
You're doing great! You're well within your budget with ₹12,500 remaining.
Consider meal prepping to reduce restaurant spending if you want to save more.
"""
```

#### Example 3: Fraud Detection

**User Query**: "Check if my last transaction is suspicious"

**1. PLAN Phase**
```python
intent = "FRAUD_CHECK"
tools = ["get_transactions", "flag_transaction_fraud", "detect_patterns"]
# Get last transaction
```

**2. ACT Phase**
```python
# Get last transaction
last_transaction = await get_transactions(
    user_id=user_id,
    limit=1,
    order_by="timestamp DESC"
)

# Run ML fraud detection
fraud_result = await fraud_detector.predict(last_transaction)

# Check historical patterns
patterns = await detect_patterns(user_id=user_id, category=last_transaction["category"])
```

**3. OBSERVE Phase**
```python
observations = {
    "transaction": last_transaction,
    "fraud_score": 0.15,  # Low risk
    "is_fraud": False,
    "unusual_factors": [],
    "similar_transactions": 12,
    "average_amount": 450,
    "this_amount": 500
}
```

**4. REFLECT Phase**
```python
reflection = """
Transaction appears legitimate.
Fraud score: 0.15 (Low risk, threshold: 0.7)
Amount (₹500) is consistent with user's typical spending pattern.
No unusual factors detected.
"""
```

**5. RESPOND Phase**
```python
response = """
🔒 Transaction Security Check

Transaction: Food at Starbucks
Amount: ₹500
Date: April 28, 2026

Status: ✅ SAFE
Fraud Risk: Low (15%)

This transaction appears legitimate based on:
• Consistent with your spending patterns
• Similar to 12 previous transactions
• Amount within normal range (avg: ₹450)
• No unusual location or timing

Your account is secure! 🛡️
"""
```

### Base Agent Implementation

```python
class BaseAgent:
    def __init__(self, name: str, role: str, tools: List[str]):
        self.name = name
        self.role = role
        self.tools = tools
        self.tool_registry = get_tool_registry()
        self.model = ModelLayer()
        self.rag = RAGPipeline()
    
    async def process(self, query: str, context: Dict) -> Dict:
        """Main agentic loop"""
        try:
            # 1. PLAN
            plan = await self.plan(query, context)
            logger.info(f"{self.name} - PLAN: {plan}")
            
            # 2. ACT
            actions = await self.act(plan, context)
            logger.info(f"{self.name} - ACT: {len(actions)} actions executed")
            
            # 3. OBSERVE
            observations = await self.observe(actions)
            logger.info(f"{self.name} - OBSERVE: {observations}")
            
            # 4. REFLECT
            reflection = await self.reflect(query, observations, context)
            logger.info(f"{self.name} - REFLECT: {reflection}")
            
            # 5. RESPOND
            response = await self.respond(query, reflection, observations, context)
            logger.info(f"{self.name} - RESPOND: Generated response")
            
            return {
                "agent": self.name,
                "response": response,
                "success": True,
                "observations": observations
            }
        
        except Exception as e:
            logger.error(f"{self.name} - ERROR: {str(e)}")
            return {
                "agent": self.name,
                "response": f"I encountered an error: {str(e)}",
                "success": False
            }
    
    async def plan(self, query: str, context: Dict) -> Dict:
        """Detect intent and select tools"""
        # Detect intent (CREATE, READ, UPDATE, DELETE, ANALYZE)
        intent = self._detect_intent(query)
        
        # Extract parameters using LLM
        params = await self._extract_parameters(query, intent, context)
        
        # Select appropriate tools
        tools = self._select_tools(intent)
        
        # Use RAG for additional context
        rag_context = await self.rag.query(query, context["user_id"], top_k=5)
        
        return {
            "intent": intent,
            "parameters": params,
            "tools": tools,
            "rag_context": rag_context
        }
    
    async def act(self, plan: Dict, context: Dict) -> List[Dict]:
        """Execute tools"""
        results = []
        
        for tool_name in plan["tools"]:
            try:
                result = await self.tool_registry.execute_tool(
                    name=tool_name,
                    arguments=plan["parameters"],
                    context=context
                )
                results.append({
                    "tool": tool_name,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "tool": tool_name,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    async def observe(self, actions: List[Dict]) -> Dict:
        """Process tool results"""
        observations = {
            "successful_actions": [],
            "failed_actions": [],
            "data": {},
            "insights": []
        }
        
        for action in actions:
            if action["success"]:
                observations["successful_actions"].append(action["tool"])
                observations["data"][action["tool"]] = action["result"]
            else:
                observations["failed_actions"].append({
                    "tool": action["tool"],
                    "error": action["error"]
                })
        
        # Extract insights from data
        observations["insights"] = self._extract_insights(observations["data"])
        
        return observations
    
    async def reflect(self, query: str, observations: Dict, context: Dict) -> str:
        """Analyze observations and generate insights"""
        prompt = f"""
You are a {self.role}.

User Query: {query}

Observations:
{json.dumps(observations, indent=2)}

Analyze the observations and provide:
1. Key insights
2. Patterns or trends
3. Recommendations
4. Any concerns or warnings

Be specific and actionable.
"""
        
        response = await self.model.generate([
            {"role": "system", "content": f"You are a {self.role}."},
            {"role": "user", "content": prompt}
        ])
        
        return response["content"]
    
    async def respond(self, query: str, reflection: str, 
                     observations: Dict, context: Dict) -> str:
        """Format final response"""
        prompt = f"""
You are a {self.role}.

User Query: {query}

Analysis:
{reflection}

Data:
{json.dumps(observations["data"], indent=2)}

Generate a user-friendly response that:
1. Directly answers the query
2. Includes specific numbers and details
3. Provides actionable recommendations
4. Uses emojis and formatting for readability
5. Is structured with bullet points and sections

Format with proper line breaks (\\n\\n for paragraphs, \\n for lists).
"""
        
        response = await self.model.generate([
            {"role": "system", "content": f"You are a {self.role}."},
            {"role": "user", "content": prompt}
        ], temperature=0.7)
        
        # Apply guardrails
        validated_response = await output_validator.validate_and_enhance(
            response["content"],
            context
        )
        
        return validated_response
```

### Specialized Agents

#### Budget Agent
**Tools**: get_budgets, create_budget, update_budget, delete_budget, get_transactions, analyze_budget_trends

**Capabilities**:
- Budget creation and management
- Spending analysis
- Budget recommendations
- Overspending alerts

#### Fraud Agent
**Tools**: get_fraud_alerts, flag_transaction_fraud, flag_transaction_safe, get_transactions

**Capabilities**:
- Anomaly detection
- Pattern recognition
- Security recommendations
- Transaction flagging

#### Risk Agent
**Tools**: get_risk_score, get_transactions, get_budgets, analyze_budget_trends

**Capabilities**:
- Financial health scoring
- Risk factor analysis
- Mitigation strategies
- Trajectory prediction

#### Investment Agent
**Tools**: get_transactions, create_transaction, get_budgets, get_risk_score

**Capabilities**:
- Investment capacity analysis
- Asset allocation recommendations
- Portfolio optimization
- Goal-based planning

#### Insurance Agent
**Tools**: get_insurance_policies, get_transactions, get_risk_score, get_budgets

**Capabilities**:
- Coverage needs assessment
- Policy recommendations
- Premium optimization
- Gap analysis

### Multi-Agent Orchestration

```python
class AgentCoordinator:
    async def process_query(self, query: str, user_id: str):
        # 1. Plan: Determine which agents to use
        plan = await self.planner.plan(query)
        
        # 2. Execute: Run agents in parallel or sequence
        results = await self.executor.execute(plan, user_id)
        
        # 3. Synthesize: Combine agent responses
        response = await self.synthesizer.synthesize(results, query)
        
        return response
```

**Query Routing**:
```python
intent_keywords = {
    "BUDGET": ["budget", "spending", "expense", "transaction", "edit", "update"],
    "FRAUD": ["fraud", "suspicious", "security", "unauthorized"],
    "RISK": ["risk", "health", "score", "assessment"],
    "INVESTMENT": ["invest", "portfolio", "stock", "asset"],
    "INSURANCE": ["insurance", "policy", "coverage", "premium"]
}
```

---

## MCP Layer

### Model Context Protocol

MCP provides a standardized interface for tool execution and context management.

### Components

#### 1. Model Layer (`mcp/model.py`)
```python
class ModelLayer:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
    
    async def generate(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return {"content": response.choices[0].message.content}
```

#### 2. Protocol Layer (`mcp/protocol.py`)
```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}
    
    def register(self, name: str, description: str, parameters: Dict):
        def decorator(func):
            self.tools[name] = {
                "function": func,
                "description": description,
                "parameters": parameters
            }
            return func
        return decorator
    
    async def execute_tool(self, name: str, arguments: Dict, context: Dict):
        tool = self.tools[name]
        return await tool["function"](**arguments)
```

#### 3. Context Layer (`mcp/context.py`)
```python
class ContextLayer:
    def __init__(self):
        self.contexts = {}
    
    def add_context(self, user_id: str, key: str, value: Any):
        if user_id not in self.contexts:
            self.contexts[user_id] = {}
        self.contexts[user_id][key] = value
    
    def get_context(self, user_id: str) -> Dict:
        return self.contexts.get(user_id, {})
```

### Tool Definition Example

```python
@tool_registry.register(
    name="create_budget",
    description="Create a new budget for a category",
    parameters={
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "category": {"type": "string"},
            "limit_amount": {"type": "number"}
        },
        "required": ["user_id", "category", "limit_amount"]
    }
)
async def create_budget(user_id: str, category: str, limit_amount: float):
    sb = get_supabase()
    result = sb.table("budgets").insert({
        "user_id": user_id,
        "category": category,
        "limit_amount": limit_amount
    }).execute()
    return {"success": True, "budget": result.data[0]}
```

---

## RAG Pipeline

### Architecture

```
┌─────────────┐
│   Document  │
└──────┬──────┘
       │
┌──────▼──────┐
│   Chunker   │  Split into chunks
└──────┬──────┘
       │
┌──────▼──────┐
│  Embedder   │  Generate embeddings
└──────┬──────┘
       │
┌──────▼──────┐
│   Indexer   │  Store in vector DB
└──────┬──────┘
       │
┌──────▼──────┐
│  Retriever  │  Similarity search
└──────┬──────┘
       │
┌──────▼──────┐
│   Context   │  Augment prompt
└─────────────┘
```

### Implementation

#### Embedder
```python
class Embedder:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def embed(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
```

#### Indexer
```python
class Indexer:
    def __init__(self):
        self.index = faiss.IndexFlatL2(384)  # 384 dimensions
        self.documents = []
    
    def add_documents(self, docs: List[str], embeddings: List[List[float]]):
        self.index.add(np.array(embeddings))
        self.documents.extend(docs)
```

#### Retriever
```python
class Retriever:
    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        query_embedding = self.embedder.embed(query)
        distances, indices = self.index.search(
            np.array([query_embedding]), top_k
        )
        return [self.documents[i] for i in indices[0]]
```

---

## Database Schema

### Tables

#### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### transactions
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL,
    type TEXT CHECK (type IN ('income', 'expense')),
    category TEXT NOT NULL,
    description TEXT,
    location TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    is_fraud BOOLEAN DEFAULT FALSE,
    fraud_score DECIMAL(5,2) DEFAULT 0
);
```

#### budgets
```sql
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    category TEXT NOT NULL,
    limit_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, category)
);
```

#### insurance_policies
```sql
CREATE TABLE insurance_policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    policy_type TEXT NOT NULL,
    provider TEXT,
    premium DECIMAL(10,2),
    coverage_amount DECIMAL(12,2),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Row-Level Security (RLS)

```sql
-- Enable RLS
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own transactions
CREATE POLICY "Users can view own transactions"
ON transactions FOR SELECT
USING (auth.uid() = user_id);

-- Policy: Users can insert their own transactions
CREATE POLICY "Users can insert own transactions"
ON transactions FOR INSERT
WITH CHECK (auth.uid() = user_id);
```

---

## API Workflows

### 1. User Authentication Flow

```
Client                  Backend                 Supabase
  │                       │                        │
  ├─ POST /auth/login ───>│                        │
  │                       ├─ Verify credentials ──>│
  │                       │<─ Return user + token ─┤
  │<─ Return JWT token ───┤                        │
  │                       │                        │
  ├─ Store token ─────────┤                        │
  │                       │                        │
  ├─ GET /transactions ──>│                        │
  │   (with JWT)          ├─ Validate token ──────>│
  │                       │<─ User verified ───────┤
  │                       ├─ Query transactions ──>│
  │                       │<─ Return data ─────────┤
  │<─ Return transactions ┤                        │
```

### 2. AI Chat Flow

```
Client                  Backend                 Agents                  Supabase
  │                       │                        │                        │
  ├─ POST /ai/chat ──────>│                        │                        │
  │   {query, user_id}    │                        │                        │
  │                       ├─ Route to coordinator ─>│                        │
  │                       │                        ├─ Plan query ───────────┤
  │                       │                        ├─ Select agents ────────┤
  │                       │                        │                        │
  │                       │                        ├─ Execute tools ───────>│
  │                       │                        │<─ Return data ─────────┤
  │                       │                        │                        │
  │                       │                        ├─ Generate response ────┤
  │                       │<─ Return response ─────┤                        │
  │<─ Return AI response ─┤                        │                        │
```

### 3. Transaction Creation Flow

```
Client                  Backend                 MCP                     Supabase
  │                       │                        │                        │
  ├─ Chat: "add Rs 500" ─>│                        │                        │
  │                       ├─ Detect CREATE ───────>│                        │
  │                       │                        ├─ Extract params ───────┤
  │                       │                        │   amount=500           │
  │                       │                        │   category=Food        │
  │                       │                        │                        │
  │                       │                        ├─ Call create_transaction>│
  │                       │                        │<─ Return success ──────┤
  │                       │<─ Format response ─────┤                        │
  │<─ "Transaction created"┤                       │                        │
```

---

## Security

### Authentication
- JWT tokens with expiration
- Secure password hashing (bcrypt)
- Token refresh mechanism

### Authorization
- Row-Level Security (RLS) in Supabase
- User-scoped data access
- Role-based permissions

### Input Validation
- Pydantic models for type safety
- SQL injection prevention
- XSS protection
- CSRF tokens

### Guardrails
```python
class InputValidator:
    def validate_and_sanitize(self, query: str, context: Dict):
        # Check for malicious patterns
        if self._contains_sql_injection(query):
            return False, "SQL injection detected", ""
        
        # Sanitize input
        sanitized = self._sanitize(query)
        
        return True, None, sanitized
```

### Rate Limiting
- API rate limits per user
- LLM token usage tracking
- Request throttling

### Data Privacy
- PII masking in logs
- Encrypted data at rest
- Secure data transmission (HTTPS)

---

## Performance Optimization

### Caching
- Redis for session data
- Query result caching
- Vector embedding caching

### Database
- Indexed columns
- Connection pooling
- Query optimization

### Frontend
- Code splitting
- Lazy loading
- Asset minification
- Browser caching

---

## Monitoring & Observability

### Metrics (Prometheus)
- Request count
- Response time
- Error rate
- Agent execution time
- Tool usage

### Logging
- Structured JSON logs
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Request tracing
- Error tracking

### Tracing
- Distributed tracing
- Request flow visualization
- Performance bottleneck identification

---

**Last Updated**: April 28, 2026
