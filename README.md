# FinA - Personal Finance Management System

FinA is a production-grade AI-powered personal finance advisor built on a true MCP (Model-Context-Protocol) architecture with a full RAG pipeline, 5 specialized AI agents, and an agentic reasoning loop. It helps users manage transactions, budgets, fraud detection, risk assessment, investments, and insurance — all through natural language.

![Version](https://img.shields.io/badge/version-1.2.0-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Pipeline Stages](#pipeline-stages)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [User Guide](#user-guide)
- [Docker Commands](#docker-commands)
- [Development Setup](#development-setup)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)

---

## Architecture Overview

![FinA Architecture Diagram](docs/Architecture_Diagram.png)

---

## Pipeline Stages

| Step | Agent | Description |
|------|-------|-------------|
| 1 | **QueryPlanner** | Receives user natural language query. Detects intent (BUDGET / FRAUD / RISK / INVESTMENT / INSURANCE). Routes to one or multiple agents. No LLM call — pure keyword routing. |
| 2 | **Guardrails (Input)** | Pre-LLM validation. Detects XSS, SQL injection, excessive amounts, invalid queries. Sanitizes input before any agent sees it. Zero LLM cost. |
| 3 | **RAG Retrieval** | Embeds query, searches FAISS vector DB, retrieves top-5 relevant transactions/budgets/policies. Injects context into agent prompt. |
| 4 | **BudgetAgent** | `[Direct LLM + Tools]` Handles spending queries, budget creation/update/delete, transaction management. Tools: `get_transactions`, `create_budget`, `update_transaction`, `analyze_budget_trends`. |
| 5 | **FraudAgent** | `[ML + LLM]` Isolation Forest ML model scores each transaction. LLM interprets patterns. Tools: `get_fraud_alerts`, `flag_transaction_fraud`, `detect_patterns`. |
| 6 | **RiskAgent** | `[Direct LLM]` Calculates financial health score (0-100, grade A-F). Analyzes debt-to-income ratio, emergency fund, spending stability. Tools: `get_risk_score`, `calculate_health_metrics`. |
| 7 | **InvestmentAgent** | `[Direct LLM]` Analyzes investment capacity, recommends portfolio allocation. Tools: `get_transactions`, `get_risk_score`, `analyze_investments`. |
| 8 | **InsuranceAgent** | `[Direct LLM]` Assesses coverage needs, recommends policies, calculates premiums. Tools: `get_insurance_policies`, `assess_coverage`, `save_assessment`. |
| 9 | **ResponseSynthesizer** | Combines outputs from multiple agents into one coherent response using LLM. Applies post-processing for concise/detailed/balanced formatting. |
| 10 | **Guardrails (Output)** | Post-LLM validation. Removes hallucinations, verifies data accuracy, adds disclaimers for investment/insurance advice. |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **LLM** | Groq — `llama-3.3-70b-versatile` (free tier, 100K tokens/day) |
| **Agent Framework** | Custom multi-agent system with Agentic Loop (Plan, Act, Observe, Reflect, Respond) |
| **MCP Architecture** | Custom Model-Context-Protocol (Model Layer, Context Layer, Protocol Layer) |
| **RAG Pipeline** | FAISS vector DB, sentence-transformers, custom chunker/embedder/retriever |
| **Backend API** | FastAPI + Uvicorn (port 8000), 30+ REST endpoints, WebSocket |
| **Frontend** | Vanilla JS (ES6+), Custom CSS, Nginx (reverse proxy) |
| **Database** | Supabase (PostgreSQL), 6 tables, Row-Level Security (RLS) |
| **Vector Store** | FAISS, 1536 dimensions, persistent index |
| **Cache** | Redis |
| **ML Models** | Isolation Forest (fraud), Logistic Regression (categorization), Custom risk scorer |
| **Guardrails** | Input Validator, Prompt Constraints, Output Validator, XSS/SQL injection prevention |
| **Observability** | Prometheus metrics, Grafana dashboards, Structured JSON logging, Distributed tracing |
| **Containerization** | Docker, Docker Compose (5 services) |
| **Testing** | pytest, 181+ tests, 70%+ coverage |

---

## Features

- **Multi-Agent AI System** — 5 specialized agents: Budget, Fraud, Risk, Investment, Insurance
- **Natural Language Interface** — Chat with AI to manage your finances
- **Real-time Transaction Management** — Create, update, and delete transactions via chat or UI
- **Smart Budget Planning** — AI-powered budget recommendations and tracking
- **Fraud Detection** — ML-based fraud detection with real-time alerts
- **Risk Assessment** — Comprehensive financial health scoring (0-100, grade A-F)
- **Investment Advisory** — Personalized investment recommendations based on your data
- **Insurance Planning** — Coverage analysis, needs assessment, and policy recommendations
- **RAG Pipeline** — Context-aware responses grounded in your actual financial data
- **Agentic Loop** — Plan, Act, Observe, Reflect, Respond reasoning cycle per agent
- **Guardrails** — Input/output validation, hallucination prevention, safe financial advice
- **Observability** — Metrics, logging, and distributed tracing with Prometheus and Grafana

---

## Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux) — https://www.docker.com/products/docker-desktop
- **Supabase Account** (Free) — https://supabase.com
- **Groq API Key** (Free) — https://console.groq.com

---

## Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/Logeshwar13/fina.git
cd fina
```

### Step 2: Setup Environment Variables

Copy and fill in the root `.env`:

```env
VITE_API_URL=http://localhost:8000
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

Copy and fill in `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres.YOUR_PROJECT_REF:YOUR_PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres?sslmode=require
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_role_key_here
GROQ_API_KEY=your_groq_api_key_here
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
PORT=8000
```

**Where to find Supabase values:** Dashboard > Settings > API
**Where to find Groq key:** https://console.groq.com > API Keys

### Step 3: Setup Database

1. Go to Supabase project > SQL Editor
2. Open `backend/data/complete_database_schema.sql`
3. Copy, paste, and run it

This creates 6 tables: `users`, `transactions`, `budgets`, `risk_scores`, `insurance_policies`, `insurance_risk_assessments`

### Step 4: Run with Docker

```bash
docker-compose up -d --build
```

### Step 5: Access the Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Grafana | http://localhost:3000 (admin/admin) |
| Prometheus | http://localhost:9090 |

---

## User Guide

### Sign Up and Login

1. Open http://localhost
2. Click "Sign Up" and fill in your details (email, password, name)
3. Check your email for a verification link
4. Login and you'll land on the Dashboard

### Dashboard

Shows your total balance, monthly income/expenses, spending by category (pie chart), monthly trends (line chart), and recent transactions.

### Transactions

Add, edit, or delete transactions manually via the UI, or use AI Chat:
- "Add a transaction of Rs.500 for food at Starbucks"
- "Edit the last transaction to income"
- "Delete the movie transaction"

### Budgets

Set monthly limits per category. Track progress with color indicators:
- Green: under 50% spent
- Yellow: 50-80% spent
- Red: over 80% spent

Use AI Chat: "Create a budget for Food with Rs.15,000"

### AI Chat

Talk to your financial advisor in natural language. Examples:

| Query | What it does |
|-------|-------------|
| "How much did I spend on food?" | Shows food spending total |
| "Show my last 5 transactions" | Lists recent transactions |
| "Create a budget for Shopping with Rs.10,000" | Creates budget |
| "What is my financial health score?" | Shows risk score |
| "Should I invest Rs.50,000?" | Investment advice |
| "Do I need life insurance?" | Insurance recommendation |
| "Are there any suspicious transactions?" | Fraud check |

### Fraud Detection

ML model scores every transaction. View flagged transactions, review patterns, and mark safe ones.

### Risk Assessment

Financial health score (0-100) with grade A-F. Analyzes debt-to-income ratio, emergency fund, income stability, and spending patterns.

### Insurance

Add policies (Health, Life, Property, Vehicle), track premiums and expiry dates, and run the coverage calculator for personalized recommendations.

### Troubleshooting

| Problem | Fix |
|---------|-----|
| Page not loading | Press `Ctrl + Shift + R` (hard refresh) |
| AI Chat not responding | Check Groq API key in `backend/.env`, check token limit |
| Transactions not saving | Verify Supabase credentials, check browser console (F12) |
| Login issues | Confirm email in Supabase Auth dashboard |
| Charts not showing | Ensure transactions exist, hard refresh |

---

## Docker Commands

```bash
# Start all services
docker-compose up -d --build

# Stop all services
docker-compose down

# View logs
docker logs fina-backend --follow

# Check running containers
docker-compose ps
```

### Updating API Keys (Important)

`docker-compose restart` does NOT reload `.env` changes. Use this instead:

```bash
docker-compose stop backend
docker-compose up -d backend
```

Verify the new key loaded:
```bash
docker exec fina-backend env | grep GROQ_API_KEY
```

Full rebuild if still not working:
```bash
docker-compose down
docker-compose up -d --build
```

> **Groq Free Tier**: 100,000 tokens/day per organization. If you hit the limit, wait for daily reset (midnight UTC) or use a new Groq account.

---

## Development Setup

### Backend (without Docker)

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
source venv/bin/activate       # Linux/Mac
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (without Docker)

```bash
cd public
python -m http.server 8080
```

Then open http://localhost:8080

---

## Environment Variables

### Required

| Variable | Description | Where to Find |
|----------|-------------|---------------|
| `SUPABASE_URL` | Supabase project URL | Dashboard > Settings > API |
| `SUPABASE_KEY` | Supabase anon/public key | Dashboard > Settings > API |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | Dashboard > Settings > API |
| `DATABASE_URL` | PostgreSQL connection string | Dashboard > Settings > Database |
| `GROQ_API_KEY` | Groq LLM API key | https://console.groq.com > API Keys |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Environment mode |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `PORT` | `8000` | Backend port |
| `DEFAULT_LLM_MODEL` | `llama-3.3-70b-versatile` | LLM model |

---

## Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agents_phase3.py
```

---

## Project Structure

```
fina/
├── backend/
│   ├── agents/          # 5 AI agents (Budget, Fraud, Risk, Investment, Insurance)
│   ├── api/             # REST API endpoints
│   ├── database/        # Supabase client and models
│   ├── guardrails/      # Input/output validation
│   ├── mcp/             # Model-Context-Protocol layers
│   ├── ml/              # ML models (fraud, categorization, risk)
│   ├── observability/   # Logging, metrics, tracing
│   ├── orchestrator/    # Query planner, executor, synthesizer
│   ├── rag/             # RAG pipeline (chunker, embedder, indexer, retriever)
│   └── main.py          # FastAPI application entry point
├── public/
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript (views, components, utils)
│   └── index-new.html   # Main HTML
├── docs/                # Documentation and architecture diagram
├── docker-compose.yml   # Docker services
├── Dockerfile           # Backend Docker image
└── README.md
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture Guide](docs/ARCHITECTURE.md) | System design and MCP/RAG/Agent details |
| [Features Guide](docs/FEATURES.md) | Complete feature documentation (40+ features) |
| [API Reference](docs/API.md) | REST API endpoints and schemas |
| [Deployment Guide](docs/DEPLOYMENT.md) | Production deployment instructions |
| [Technical Deep Dive](docs/TECHNICAL.md) | Backend, frontend, and agent workflows |
| [Groq Setup Guide](GROQ_SETUP_GUIDE.md) | Free LLM API setup |

---

## Troubleshooting

```bash
# Backend won't start
docker logs fina-backend

# Port already in use
netstat -ano | findstr :8000   # Windows

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build

# Check Groq rate limit
docker logs fina-backend | grep "rate_limit"
```

---

## Roadmap

- [ ] Mobile app (React Native)
- [ ] Voice interface
- [ ] Multi-currency support
- [ ] Bank account integration
- [ ] Cryptocurrency tracking
- [ ] Tax optimization
- [ ] Family/shared budgets

---

**Built by LOGESHWAR R**

**Version**: 1.2.0 | **Last Updated**: April 2026 | **Status**: Production Ready
