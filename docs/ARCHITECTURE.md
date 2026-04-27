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
- **Model Layer**: LLM integration (Groq, OpenAI, Anthropic)
- **Context Layer**: Vector storage (FAISS), semantic search
- **Protocol Layer**: Tool registry, execution engine

### 6. RAG Pipeline
- **Chunker**: Document segmentation
- **Embedder**: Text to vectors (sentence-transformers)
- **Indexer**: Vector indexing
- **Retriever**: Semantic search
- **Generator**: LLM response generation

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
