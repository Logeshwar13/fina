# System Architecture

FinA is a production-grade AI-powered personal finance advisor built with a modern, scalable architecture.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Nginx)                        │
│                    Vanilla JS + Custom CSS                      │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/WebSocket
┌────────────────────────────┴────────────────────────────────────┐
│                      API Gateway (FastAPI)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Rate Limiter │  │  Guardrails  │  │ Error Handler│           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │ 
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                    Agent Orchestrator                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Query Planner → Agent Executor → Response Synthesizer   │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐   ┌───────▼────────┐   ┌───────▼────────┐
│ Budget Agent   │   │  Fraud Agent   │   │  Risk Agent    │
└───────┬────────┘   └───────┬────────┘   └───────┬────────┘
        │                    │                    │
┌───────▼────────┐   ┌───────▼────────┐           |
│Investment Agent│   │Insurance Agent │           |
└───────┬────────┘   └───────┬────────┘           |
        │                    │                    |
        └────────────────────┼────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                         MCP Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Model Layer  │  │Context Layer │  │Protocol Layer│           │
│  │  (LLM API)   │  │ (FAISS Vec)  │  │(Tool Registry)│          │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                      RAG Pipeline                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Chunker → Embedder → Indexer → Retriever → Generator    │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                    Data & Storage Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Supabase   │  │    Redis     │  │    FAISS     │           │
│  │  (Postgres)  │  │   (Cache)    │  │  (Vectors)   │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                    Observability Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Logging    │  │   Metrics    │  │   Tracing    │           │
│  │ (Structured) │  │(Prometheus)  │  │  (Spans)     │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend Layer
- **Technology**: Vanilla JavaScript, Custom CSS
- **Server**: Nginx (reverse proxy, caching, compression)
- **Features**: Responsive design, real-time updates, WebSocket support

### 2. API Gateway
- **Framework**: FastAPI (Python)
- **Middleware**: Rate limiting, guardrails, error handling
- **Features**: 30+ REST endpoints, WebSocket support, API versioning

### 3. Agent Orchestrator
- **Components**: Query Planner, Agent Executor, Response Synthesizer
- **Features**: Multi-agent coordination, parallel execution, LLM synthesis

### 4. AI Agents (5 Specialized Agents)
- **Budget Agent**: Spending analysis, budget recommendations
- **Fraud Agent**: Security analysis, pattern detection
- **Risk Agent**: Health assessment, risk scoring
- **Investment Agent**: Portfolio analysis, investment advice
- **Insurance Agent**: Coverage analysis, policy recommendations

### 5. MCP Layer (Model-Context-Protocol)

MCP provides a standardized architecture separating concerns into three layers:

#### Model Layer (`backend/mcp/model.py`)
- **LLM Integration**: Supports Groq (free!), OpenAI, Anthropic
- **Response Generation**: Temperature-controlled text generation
- **Embeddings**: Convert text to 1536-dimensional vectors
- **Features**: Multi-provider support, automatic fallbacks, token tracking

**Implementation:**
```python
class ModelLayer:
    def __init__(self, api_key: str, provider: str = "groq"):
        self.client = self._init_client(provider, api_key)
        self.model = "llama-3.3-70b-versatile"  # Groq default
    
    async def generate(self, messages: List[Dict], temperature: float = 0.7):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return {"content": response.choices[0].message.content}
    
    def generate_embeddings(self, text: str) -> List[float]:
        # Returns 1536-dimensional vector
        return self.embedder.encode(text).tolist()
```

#### Context Layer (`backend/mcp/context.py`)
- **Vector Storage**: FAISS index with 1536 dimensions
- **Semantic Search**: Similarity search with metadata filtering
- **Memory Management**: Persistent storage and retrieval
- **Features**: User-scoped contexts, automatic indexing, real-time updates

**Implementation:**
```python
class ContextLayer:
    def __init__(self):
        self.index = faiss.IndexFlatL2(1536)  # L2 distance
        self.documents = []
        self.metadata = []
    
    def add_documents(self, docs: List[str], embeddings: List[List[float]], 
                     metadata: List[Dict]):
        self.index.add(np.array(embeddings))
        self.documents.extend(docs)
        self.metadata.extend(metadata)
    
    def search(self, query_embedding: List[float], top_k: int = 5, 
              filters: Dict = None) -> List[Dict]:
        distances, indices = self.index.search(
            np.array([query_embedding]), top_k
        )
        results = []
        for i, idx in enumerate(indices[0]):
            if filters and not self._matches_filters(self.metadata[idx], filters):
                continue
            results.append({
                "document": self.documents[idx],
                "metadata": self.metadata[idx],
                "score": float(distances[0][i])
            })
        return results
```

#### Protocol Layer (`backend/mcp/protocol.py` + `tools.py`)
- **Tool Registry**: 30+ registered financial tools
- **Execution Engine**: Type-safe tool execution with validation
- **API Interface**: Standardized tool calling interface
- **Features**: Automatic tool discovery, parameter validation, error handling

**Tool Categories:**
- Transaction tools: get_transactions, create_transaction, update_transaction, delete_transaction
- Budget tools: get_budgets, create_budget, update_budget, analyze_budget_trends
- Risk tools: get_risk_score, calculate_health_metrics
- Fraud tools: get_fraud_alerts, flag_transaction_fraud, detect_patterns
- Insurance tools: get_insurance_policies, assess_coverage, recommend_policies
- Analytics tools: get_insights, analyze_trends, generate_reports

**Implementation:**
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
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        
        tool = self.tools[name]
        # Validate parameters against schema
        self._validate_parameters(arguments, tool["parameters"])
        
        # Execute with context
        return await tool["function"](**arguments, context=context)
```

**Example Tool Registration:**
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
async def create_budget(user_id: str, category: str, limit_amount: float, context: Dict):
    sb = get_supabase()
    result = sb.table("budgets").insert({
        "user_id": user_id,
        "category": category,
        "limit_amount": limit_amount
    }).execute()
    return {"success": True, "budget": result.data[0]}
```

### 6. RAG Pipeline

RAG (Retrieval-Augmented Generation) enhances LLM responses with relevant context from your financial data.

#### Complete RAG Workflow

```
User Query: "How much did I spend on food last month?"
     │
     ▼
┌─────────────────────────────────────────┐
│  1. CHUNK                                │
│  • Break transactions into chunks        │
│  • "Transaction: Food at Starbucks ₹500" │
│  • "Budget: Food category ₹15,000"       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  2. EMBED                                │
│  • Convert text to vectors (1536-dim)    │
│  • [0.123, -0.456, 0.789, ...]          │
│  • Uses sentence-transformers           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  3. INDEX                                │
│  • Store in FAISS vector database        │
│  • With metadata (user_id, category)    │
│  • Persistent storage to disk            │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  4. RETRIEVE                             │
│  • Embed query: "food spending"          │
│  • Find top-5 similar transactions       │
│  • Filter by user_id and date range     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  5. GENERATE                             │
│  • LLM + Retrieved Context               │
│  • "You spent ₹2,500 on food last month" │
│  • "Top merchants: Starbucks, McDonald's"│
└──────────────────────────────────────────┘
```

#### Implementation Details

**Chunker** (`backend/rag/chunker.py`)
```python
class Chunker:
    def chunk_transaction(self, transaction: Dict) -> str:
        return f"""Transaction: {transaction['description']}
Amount: ₹{transaction['amount']}
Category: {transaction['category']}
Date: {transaction['timestamp']}
Type: {transaction['type']}"""
    
    def chunk_budget(self, budget: Dict) -> str:
        return f"""Budget: {budget['category']}
Limit: ₹{budget['limit_amount']}
Spent: ₹{budget.get('spent', 0)}
Remaining: ₹{budget['limit_amount'] - budget.get('spent', 0)}"""
```

**Embedder** (`backend/rag/embedder.py`)
```python
class Embedder:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Produces 384-dimensional vectors (can be upgraded to 1536)
    
    def embed(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()
```

**Indexer** (`backend/rag/indexer.py`)
```python
class Indexer:
    def __init__(self, dimension: int = 1536):
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
        self.metadata = []
    
    def add_documents(self, docs: List[str], embeddings: List[List[float]], 
                     metadata: List[Dict]):
        self.index.add(np.array(embeddings))
        self.documents.extend(docs)
        self.metadata.extend(metadata)
    
    def save_index(self, path: str):
        faiss.write_index(self.index, f"{path}/vector_index.index")
        with open(f"{path}/vector_index.json", "w") as f:
            json.dump({
                "documents": self.documents,
                "metadata": self.metadata
            }, f)
```

**Retriever** (`backend/rag/retriever.py`)
```python
class Retriever:
    def retrieve(self, query: str, top_k: int = 5, 
                filters: Dict = None) -> List[Dict]:
        # 1. Embed query
        query_embedding = self.embedder.embed(query)
        
        # 2. Search vector database
        distances, indices = self.index.search(
            np.array([query_embedding]), top_k * 2  # Get more for filtering
        )
        
        # 3. Apply filters (user_id, category, date range)
        results = []
        for i, idx in enumerate(indices[0]):
            metadata = self.metadata[idx]
            
            # Filter by user_id
            if filters and filters.get("user_id") != metadata.get("user_id"):
                continue
            
            # Filter by category
            if filters and filters.get("category") and \
               filters["category"] != metadata.get("category"):
                continue
            
            results.append({
                "document": self.documents[idx],
                "metadata": metadata,
                "score": float(distances[0][i])
            })
            
            if len(results) >= top_k:
                break
        
        return results
```

**Pipeline** (`backend/rag/pipeline.py`)
```python
class RAGPipeline:
    def __init__(self):
        self.chunker = Chunker()
        self.embedder = Embedder()
        self.indexer = Indexer()
        self.retriever = Retriever(self.embedder, self.indexer)
    
    async def index_user_data(self, user_id: str):
        """Index all user transactions and budgets"""
        sb = get_supabase()
        
        # Get transactions
        transactions = sb.table("transactions")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute().data
        
        # Chunk and embed
        chunks = [self.chunker.chunk_transaction(t) for t in transactions]
        embeddings = self.embedder.embed_batch(chunks)
        metadata = [{"user_id": user_id, "type": "transaction", 
                    "id": t["id"]} for t in transactions]
        
        # Index
        self.indexer.add_documents(chunks, embeddings, metadata)
        
        # Repeat for budgets, insurance, etc.
    
    async def query(self, query: str, user_id: str, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant context for a query"""
        return self.retriever.retrieve(
            query, 
            top_k=top_k, 
            filters={"user_id": user_id}
        )
    
    async def generate_rag_response(self, query: str, user_id: str) -> str:
        """Generate LLM response with retrieved context"""
        # 1. Retrieve context
        context_docs = await self.query(query, user_id, top_k=5)
        
        # 2. Build prompt
        context_str = "\n\n".join([doc["document"] for doc in context_docs])
        prompt = f"""Based on the following financial data:

{context_str}

Answer this question: {query}

Provide specific numbers and details from the data."""
        
        # 3. Generate response
        model = ModelLayer()
        response = await model.generate([
            {"role": "system", "content": "You are a financial advisor."},
            {"role": "user", "content": prompt}
        ])
        
        return response["content"]
```

#### Data Sources Indexed

1. **Transactions** - All user transactions with amount, category, description
2. **Budgets** - Budget limits, spending, and remaining amounts
3. **Insurance Policies** - Coverage details, premiums, providers
4. **Risk Assessments** - Financial health scores and risk factors

#### RAG Benefits

- **Accurate Responses**: Grounded in actual user data, not hallucinations
- **Real-time Updates**: Index updates as new transactions are added
- **Semantic Search**: Finds relevant data even with different wording
- **Context-Aware**: Understands user intent and retrieves appropriate data
- **Fast Retrieval**: FAISS provides <10ms search times

### 7. Data Layer
- **Supabase**: Primary database (PostgreSQL)
- **Redis**: Caching layer
- **FAISS**: Vector storage

### 8. Observability
- **Logging**: Structured JSON logs
- **Metrics**: Prometheus metrics (counters, gauges, histograms)
- **Tracing**: Distributed tracing with spans
- **Visualization**: Grafana dashboards

## Request Flow

### 1. User Query Flow
```
User → Frontend → API Gateway → Guardrails → Orchestrator
  → Agent Selection → Tool Execution → RAG Retrieval
  → LLM Generation → Validation → Response
```

### 2. Data Flow
```
Transaction → Database → Indexer → Vector Store
  → Retriever → Context → Agent → Response
```

### 3. Webhook Flow
```
Event → Webhook Manager → HMAC Signature → HTTP POST
  → Delivery Tracking → Retry Logic
```

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Vector Store**: FAISS
- **Cache**: Redis
- **LLM**: Groq (primary), OpenAI, Anthropic
- **Embeddings**: sentence-transformers

### Frontend
- **Language**: JavaScript (ES6+)
- **Server**: Nginx
- **Styling**: Custom CSS

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Monitoring**: Prometheus, Grafana
- **Deployment**: Automated with deploy.sh

### Testing
- **Framework**: pytest
- **Coverage**: pytest-cov
- **Load Testing**: Custom load tester

## Scalability

### Horizontal Scaling
- Multiple backend workers (Gunicorn/Uvicorn)
- Load balancing with Nginx
- Stateless API design

### Vertical Scaling
- Configurable worker count
- Resource limits in Docker
- Connection pooling

### Caching Strategy
- Redis for API responses
- FAISS for vector search
- Browser caching for static assets

## Security

### Authentication
- API key authentication
- Scope-based permissions
- Rate limiting per key

### Data Protection
- Input validation (XSS, SQL injection)
- Output sanitization
- Sensitive data masking

### Network Security
- HTTPS enforcement (production)
- CORS configuration
- Security headers (Nginx)

## Performance

### Response Times
- API: <100ms (p95)
- LLM: <2s
- RAG: <100ms
- Vector Search: <10ms

### Throughput
- API: >100 req/s per worker
- Concurrent Users: >200
- Database: >1000 queries/s

## Deployment Architecture

### Development
```
Local Machine
  ├── Backend (uvicorn --reload)
  ├── Frontend (file server)
  └── Database (Supabase cloud)
```

### Production
```
Docker Compose
  ├── Backend (4 workers)
  ├── Frontend (Nginx)
  ├── Redis
  ├── Prometheus
  └── Grafana
```

## Design Principles

1. **Modularity**: Each component is independent and replaceable
2. **Scalability**: Horizontal and vertical scaling support
3. **Reliability**: Error handling, retries, circuit breakers
4. **Observability**: Comprehensive logging, metrics, tracing
5. **Security**: Multiple layers of protection
6. **Performance**: Optimized for speed and efficiency
7. **Maintainability**: Clean code, comprehensive tests

---

For more details, see [TECHNICAL.md](./TECHNICAL.md) and [DEPLOYMENT.md](./DEPLOYMENT.md)
