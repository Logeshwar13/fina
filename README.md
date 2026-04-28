# FinA - AI-Powered Personal Finance Management System

A comprehensive personal finance management platform powered by multi-agent AI system with RAG (Retrieval-Augmented Generation) capabilities.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)

## 🌟 Features

- **Multi-Agent AI System**: 5 specialized AI agents (Budget, Fraud, Risk, Investment, Insurance)
- **Natural Language Interface**: Chat with AI to manage your finances
- **Real-time Transaction Management**: Create, update, and delete transactions
- **Smart Budget Planning**: AI-powered budget recommendations and tracking
- **Fraud Detection**: ML-based fraud detection with real-time alerts
- **Risk Assessment**: Comprehensive financial health scoring
- **Investment Advisory**: Personalized investment recommendations
- **Insurance Planning**: Coverage analysis and recommendations
- **RAG Pipeline**: Context-aware responses using vector embeddings
- **Observability**: Metrics, logging, and distributed tracing

## 🏗️ Architecture Deep Dive

### MCP (Model-Context-Protocol) Architecture

FinA implements a true MCP architecture with three distinct layers:

**1. Model Layer** (`backend/mcp/model.py`)
- LLM integration supporting Groq (free!), OpenAI, and Anthropic
- Response generation with temperature control
- Embeddings generation for semantic search
- Automatic fallbacks and token tracking

**2. Context Layer** (`backend/mcp/context.py`)
- FAISS vector database (1536 dimensions)
- Semantic search with metadata filtering
- Persistent storage for user data
- Real-time context updates

**3. Protocol Layer** (`backend/mcp/protocol.py` + `tools.py`)
- 30+ registered tools for financial operations
- Tool execution engine with error handling
- Type-safe parameter validation
- Automatic tool discovery

### RAG (Retrieval-Augmented Generation) Pipeline

FinA uses RAG to provide accurate, data-grounded responses:

```
User Query → Embed Query → Search Vectors → Retrieve Context → LLM + Context → Response
```

**How it works:**
1. **Chunking**: Break transactions/budgets into searchable chunks
2. **Embedding**: Convert text to 1536-dimensional vectors
3. **Indexing**: Store in FAISS with metadata (user_id, category)
4. **Retrieval**: Find top-5 most relevant items using semantic search
5. **Generation**: LLM generates response using retrieved context

**Data Sources Indexed:**
- All user transactions
- Budget limits and spending patterns
- Insurance policies and coverage
- Risk assessments and financial health data

### Multi-Agent Orchestration

Queries are intelligently routed to specialized agents:

```
User Query → Query Planner → Agent Selection → Parallel Execution → Response Synthesis
```

**Agent Capabilities:**
- **Budget Agent**: Spending analysis, budget recommendations, overspending alerts
- **Fraud Agent**: ML-based fraud detection, pattern analysis, security alerts
- **Risk Agent**: Financial health scoring (0-100), risk factor analysis, recommendations
- **Investment Agent**: Portfolio analysis, investment advice, risk-adjusted returns
- **Insurance Agent**: Coverage gap analysis, policy recommendations, premium optimization

**Orchestration Features:**
- Intelligent query routing based on intent keywords
- Parallel agent execution for complex queries
- LLM-based response synthesis combining multiple agent outputs
- Context sharing between agents for collaborative reasoning

### Agentic Loop

Each agent follows a 5-step reasoning cycle:

1. **PLAN**: Analyze query, select tools, create execution strategy
2. **ACT**: Execute tools, call APIs, gather data from database
3. **OBSERVE**: Process results, structure data, extract insights
4. **REFLECT**: Analyze observations, generate insights, identify patterns
5. **RESPOND**: Format answer, add recommendations, apply guardrails

**Example**: "Create a budget for Food with ₹15,000"
- PLAN: Detect "create budget" intent, select `create_budget` tool
- ACT: Execute `create_budget(category="Food", limit=15000)`
- OBSERVE: Tool returns success, budget ID created
- REFLECT: Budget created successfully, user can now track spending
- RESPOND: "✅ Budget created! Food: ₹15,000/month. I'll help you track your spending."

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
  - Download: https://www.docker.com/products/docker-desktop
  - Verify: `docker --version` and `docker-compose --version`

- **Supabase Account** (Free)
  - Sign up: https://supabase.com
  - Create a new project

- **Groq API Key** (Free)
  - Sign up: https://console.groq.com
  - Create an API key

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd rag_p1
```

### Step 2: Setup Environment Variables

#### 2.1 Create Root .env File

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your Supabase credentials:

```env
# Frontend Configuration
VITE_API_URL=http://localhost:8000
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

**Where to find these values:**
1. Go to your Supabase project dashboard
2. Click "Settings" → "API"
3. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_ANON_KEY`

#### 2.2 Create Backend .env File

```bash
# Copy the example file
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your credentials:

```env
# Database Configuration
DATABASE_URL=postgresql+psycopg2://postgres.YOUR_PROJECT_REF:YOUR_PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres?sslmode=require
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_role_key_here

# LLM API Key
GROQ_API_KEY=your_groq_api_key_here

# Application Settings (keep defaults)
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
PORT=8000
```

**Where to find these values:**

**Supabase:**
1. Go to Supabase Dashboard → Settings → API
2. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_KEY` and `SUPABASE_ANON_KEY`
   - **service_role key** → `SUPABASE_SERVICE_KEY`

3. Go to Settings → Database → Connection String
4. Select "Session pooler" and copy the connection string
5. Replace `[YOUR-PASSWORD]` with your database password → `DATABASE_URL`

**Groq:**
1. Go to https://console.groq.com
2. Sign up (free, no credit card required)
3. Go to "API Keys" section
4. Click "Create API Key"
5. Copy the key (starts with `gsk_...`) → `GROQ_API_KEY`

### Step 3: Setup Database Tables

1. Go to your Supabase project
2. Click "SQL Editor"
3. Open `backend/data/complete_database_schema.sql` from this repository
4. Copy the entire SQL content
5. Paste into Supabase SQL Editor
6. Click "Run"

This creates all necessary tables:
- `users` - User profiles and income
- `transactions` - Financial transactions
- `budgets` - Budget limits by category
- `risk_scores` - Financial health assessments
- `insurance_policies` - Insurance policies
- `insurance_risk_assessments` - Insurance needs assessments

**Alternative**: You can also use individual schema files:
- `backend/data/create_tables_supabase.py` - Core tables
- `backend/data/create_insurance_tables_supabase.sql` - Insurance tables

### Step 4: Run with Docker

## � Docker Commands

### Start Services

```bash
# Start all services
docker-compose up -d

# Start with rebuild
docker-compose up -d --build

# View logs
docker-compose logs -f

# View specific service logs
docker logs fina-backend --follow
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Check Status

```bash
# List running containers
docker-compose ps

```bash
# Make deploy script executable (Linux/Mac)
chmod +x deploy.sh

# Start all services
./deploy.sh up

# Or use docker-compose directly
docker-compose up -d --build
```

**What this does:**
- Builds the backend Docker image
- Starts 5 services:
  - Backend API (FastAPI)
  - Frontend (Nginx)
  - Redis (caching)
  - Prometheus (metrics)
  - Grafana (dashboards)

### Step 5: Access the Application

Open your browser and navigate to:

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

### Step 6: Create Your Account

1. Go to http://localhost
2. Click "Sign Up"
3. Enter your details
4. Verify email (check Supabase Auth)
5. Login and start using FinA!

## 🔧 Development Setup

### Running Locally (Without Docker)

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd public

# Simple HTTP server (Python)
python -m http.server 8080

# Or use Node.js
npx http-server . -p 8080
```

## 📝 Environment Variables Reference

### Required Variables

| Variable | Description | Where to Find |
|----------|-------------|---------------|
| `SUPABASE_URL` | Your Supabase project URL | Supabase Dashboard → Settings → API |
| `SUPABASE_KEY` | Supabase anon/public key | Supabase Dashboard → Settings → API |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | Supabase Dashboard → Settings → API |
| `DATABASE_URL` | PostgreSQL connection string | Supabase Dashboard → Settings → Database |
| `GROQ_API_KEY` | Groq LLM API key | https://console.groq.com → API Keys |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Environment mode |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `PORT` | `8000` | Backend port |
| `WORKERS` | `4` | Number of workers |
| `DEFAULT_LLM_MODEL` | `llama-3.3-70b-versatile` | LLM model to use |



# Check backend health
curl http://localhost:8000/health
```

## 🧪 Testing

### Run Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agents_phase3.py

# Run specific test
pytest tests/test_agents_phase3.py::test_budget_agent
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get transactions
curl http://localhost:8000/transactions?user_id=YOUR_USER_ID

# Create budget via AI
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Create a budget for Food with 10000", "user_id": "YOUR_USER_ID"}'
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and components
- **[Features Guide](docs/FEATURES.md)** - Complete feature documentation (40+ features)
- **[API Reference](docs/API.md)** - REST API endpoints and schemas
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Technical Deep Dive](docs/TECHNICAL.md)** - Backend, frontend, and agent workflows

### Additional Guides

- **[Groq Setup Guide](GROQ_SETUP_GUIDE.md)** - Free LLM API setup



## 🔍 Troubleshooting

### Backend won't start

```bash
# Check Docker logs
docker logs fina-backend

# Check if port 8000 is in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Restart Docker
docker-compose restart backend
```

### Frontend not loading

```bash
# Check if backend is running
curl http://localhost:8000/health

# Clear browser cache
# Press Ctrl + Shift + R (hard refresh)

# Check Docker logs
docker logs fina-nginx
```

### Database connection fails

```bash
# Test Supabase connection
curl https://YOUR_PROJECT_REF.supabase.co/rest/v1/

# Check environment variables
docker exec fina-backend env | grep SUPABASE

# Verify credentials in Supabase dashboard
```

### "Module not found" errors

```bash
# Rebuild Docker image
docker-compose up -d --build --force-recreate

# Or reinstall dependencies locally
cd backend
pip install -r requirements.txt --force-reinstall
```

### Groq API rate limit

```bash
# Free tier limits:
# - 30 requests per minute
# - 6,000 tokens per minute
# - 14,400 requests per day

# Wait a minute and try again
# Or upgrade to paid tier at https://console.groq.com
```

## 🛠️ Common Tasks

### Update Dependencies

```bash
cd backend
pip install -r requirements.txt --upgrade
```

### Clear Database

```bash
# Go to Supabase Dashboard → SQL Editor
# Run: TRUNCATE TABLE transactions, budgets, risk_scores CASCADE;
```

### Reset Docker

```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker rmi fina-backend fina-nginx

# Rebuild from scratch
docker-compose up -d --build
```

### View Metrics

1. Open Grafana: http://localhost:3000
2. Login: admin/admin
3. Add Prometheus data source: http://prometheus:9090
4. Import dashboards from `docs/grafana/`

## 📊 Project Structure

```
rag_p1/
├── backend/              # Backend application
│   ├── agents/          # AI agents
│   ├── api/             # API endpoints
│   ├── database/        # Database models
│   ├── mcp/             # Model-Context-Protocol
│   ├── ml/              # Machine learning
│   ├── rag/             # RAG pipeline
│   ├── tests/           # Test suites
│   └── main.py          # FastAPI app
├── public/              # Frontend
│   ├── css/            # Styles
│   ├── js/             # JavaScript
│   └── index-new.html  # Main HTML
├── docs/                # Documentation
├── docker-compose.yml   # Docker services
├── Dockerfile          # Docker image
├── deploy.sh           # Deployment script
└── README.md           # This file
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework
- **Supabase** - Backend-as-a-Service
- **Groq** - Fast LLM inference
- **Docker** - Containerization
- **Prometheus & Grafana** - Monitoring

## 📞 Support

- **Documentation**: See `docs/` folder
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Issues**: GitHub Issues

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Voice interface
- [ ] Multi-currency support
- [ ] Bank account integration
- [ ] Advanced analytics dashboard
- [ ] Social features (family budgets)
- [ ] Cryptocurrency tracking
- [ ] Tax optimization

---

**Built with ❤️ by the FinA Team**

**Version**: 1.0.0  
**Last Updated**: April 28, 2026  
**Status**: Production Ready ✅

