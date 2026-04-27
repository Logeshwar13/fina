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

Each agent follows the **Agentic Loop** pattern:

```
┌─────────────────────────────────────────┐
│         User Query                       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  1. PLAN                                 │
│     - Detect intent                      │
│     - Select tools                       │
│     - Create execution plan              │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  2. ACT                                  │
│     - Execute tools                      │
│     - Gather data                        │
│     - Handle errors                      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  3. OBSERVE                              │
│     - Process results                    │
│     - Structure data                     │
│     - Extract insights                   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  4. REFLECT                              │
│     - Analyze observations               │
│     - Generate insights                  │
│     - Identify patterns                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  5. RESPOND                              │
│     - Format response                    │
│     - Add recommendations                │
│     - Return to user                     │
└──────────────────────────────────────────┘
```

### Base Agent Implementation

```python
class BaseAgent:
    async def process(self, query: str, context: Dict) -> Dict:
        # 1. PLAN
        plan = await self.plan(query, context)
        
        # 2. ACT
        actions = await self.act(plan, context)
        
        # 3. OBSERVE
        observations = await self.observe(actions)
        
        # 4. REFLECT
        reflection = await self.reflect(query, observations, context)
        
        # 5. RESPOND
        response = await self.respond(query, reflection, observations, context)
        
        return {
            "agent": self.name,
            "response": response,
            "success": True
        }
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
