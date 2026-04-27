# FinA - Complete Project Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Features](#features)
5. [API Reference](#api-reference)
6. [Development](#development)
7. [Deployment](#deployment)

---

## Project Overview

**FinA** is an AI-powered personal finance management system with multi-agent architecture, RAG pipeline, and real-time chat interface.

### Technology Stack
- **Backend**: Python 3.11+, FastAPI
- **Frontend**: Vanilla JavaScript, Custom CSS
- **Database**: Supabase (PostgreSQL)
- **LLM**: Groq (Llama 3.3 70B)
- **Vector Store**: FAISS
- **Monitoring**: Prometheus, Grafana
- **Deployment**: Docker, Docker Compose

### Key Components
- **5 AI Agents**: Budget, Fraud, Risk, Investment, Insurance
- **MCP Layer**: Model-Context-Protocol for tool execution
- **RAG Pipeline**: Semantic search and context retrieval
- **Guardrails**: Input/output validation
- **Observability**: Logging, metrics, tracing

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Supabase account (https://supabase.com)
- Groq API key (https://console.groq.com)

### Setup Steps

1. **Clone Repository**
```bash
git clone <repository-url>
cd rag_p1
```

2. **Configure Environment**

Edit `backend/.env`:
```env
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# LLM Provider
GROQ_API_KEY=your_groq_api_key
DEFAULT_LLM_PROVIDER=groq
DEFAULT_LLM_MODEL=llama-3.3-70b-versatile

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
PORT=8000

# Security
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost,http://localhost:8080
```

3. **Setup Database**
```bash
cd backend
python data/create_tables_supabase.py
python data/create_insurance_tables.py
python data/seed_supabase.py
```

4. **Train ML Models**
```bash
python data/train_models.py
```

5. **Run Application**
```bash
# Stop any running containers
docker-compose down

# Build and start
docker-compose build
docker-compose up -d

# View logs
docker logs fina-backend -f
```

6. **Access Application**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────┐
│                  Frontend (Nginx)                        │
│           Vanilla JS SPA with Router                     │
└────────────────────┬─────────────