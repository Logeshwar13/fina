# FinA Documentation

Welcome to the FinA (Personal Finance Advisor) documentation!

## 📚 Available Documentation

### Core Documentation
- **[README.md](../README.md)** - Project overview and quick start (in root directory)
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete system architecture and design
- **[API.md](./API.md)** - Complete API reference with all endpoints
- **[FEATURES.md](./FEATURES.md)** - Comprehensive feature list (40+ features)
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production deployment guide
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - Local development setup and workflow
- **[TECHNICAL.md](./TECHNICAL.md)** - Deep technical dive into all components

### Additional Guides (in root directory)
- **[GROQ_SETUP_GUIDE.md](../GROQ_SETUP_GUIDE.md)** - Free LLM API setup
- **[RISK_SCORE_EXPLANATION.md](../RISK_SCORE_EXPLANATION.md)** - How risk scoring works

## 🎯 Quick Navigation

### For New Users
1. Start with [README.md](../README.md) for project overview
2. Read [FEATURES.md](./FEATURES.md) to understand capabilities
3. Follow [GROQ_SETUP_GUIDE.md](../GROQ_SETUP_GUIDE.md) for API setup

### For Developers
1. Read [DEVELOPMENT.md](./DEVELOPMENT.md) for local setup
2. Review [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
3. Check [API.md](./API.md) for endpoint reference
4. Study [TECHNICAL.md](./TECHNICAL.md) for implementation details

### For DevOps
1. Follow [DEPLOYMENT.md](./DEPLOYMENT.md) for production setup
2. Review [ARCHITECTURE.md](./ARCHITECTURE.md) for infrastructure
3. Check [API.md](./API.md) for health and monitoring endpoints

## 📖 Documentation Overview

### [README.md](../README.md)
Project overview, features, quick start, and basic usage

### [ARCHITECTURE.md](./ARCHITECTURE.md)
- High-level system design
- Component diagrams
- Technology stack
- Data flow
- Scalability and performance
- Security architecture

### [API.md](./API.md)
- 30+ REST endpoints
- Request/response schemas
- Authentication
- Rate limiting
- Error handling
- Code examples

### [FEATURES.md](./FEATURES.md)
- 40+ major features
- Transaction management
- Budget tracking
- AI agents (5 specialized)
- Fraud detection
- Risk assessment
- Insurance management
- RAG pipeline
- Observability

### [DEPLOYMENT.md](./DEPLOYMENT.md)
- Local development setup
- Docker deployment
- Cloud deployment (AWS, GCP, DigitalOcean)
- Environment configuration
- Security checklist
- Monitoring setup
- Backup and recovery

### [DEVELOPMENT.md](./DEVELOPMENT.md)
- Prerequisites and setup
- Project structure
- Development workflow
- Testing guide
- Code style
- Debugging tips
- Common tasks

### [TECHNICAL.md](./TECHNICAL.md)
- MCP (Model-Context-Protocol) layer
- RAG (Retrieval-Augmented Generation) pipeline
- Multi-agent orchestration
- Guardrails system
- Observability implementation
- API architecture
- Testing infrastructure

### [GROQ_SETUP_GUIDE.md](../GROQ_SETUP_GUIDE.md)
- Free Groq API setup
- Model selection
- Configuration
- Performance comparison
- Troubleshooting

### [RISK_SCORE_EXPLANATION.md](../RISK_SCORE_EXPLANATION.md)
- How risk scoring works
- 5 health factors explained
- Real data usage
- Score calculation
- Improvement tips

## 🚀 Getting Started

### Quick Start (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/your-username/fina.git
cd fina

# 2. Setup environment
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials

# 3. Run with Docker
chmod +x deploy.sh
./deploy.sh up

# 4. Access application
# Frontend: http://localhost
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

See [README.md](../README.md) for detailed quick start.

## 🔍 Finding Information

### Need to...
- **Understand the system?** → [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Use the API?** → [API.md](./API.md)
- **See all features?** → [FEATURES.md](./FEATURES.md)
- **Deploy to production?** → [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Develop locally?** → [DEVELOPMENT.md](./DEVELOPMENT.md)
- **Understand implementation?** → [TECHNICAL.md](./TECHNICAL.md)
- **Setup Groq API?** → [GROQ_SETUP_GUIDE.md](../GROQ_SETUP_GUIDE.md)
- **Understand risk scores?** → [RISK_SCORE_EXPLANATION.md](../RISK_SCORE_EXPLANATION.md)

## 📊 System Overview

**FinA** is a production-grade AI-powered personal finance advisor with:

- **5 Specialized AI Agents** - Budget, Fraud, Risk, Investment, Insurance
- **30+ REST API Endpoints** - Complete financial management
- **RAG Pipeline** - Semantic search and context retrieval
- **ML Models** - Fraud detection, transaction categorization
- **Real-time Chat** - Natural language financial assistant
- **Observability** - Logging, metrics, tracing
- **Production Ready** - Docker, monitoring, security

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, FastAPI
- **Frontend**: Vanilla JavaScript, Custom CSS
- **Database**: Supabase (PostgreSQL)
- **LLM**: Groq (Llama 3.3 70B)
- **Vector Store**: FAISS
- **Monitoring**: Prometheus, Grafana
- **Deployment**: Docker, Docker Compose

## 📈 Project Status

- **Version**: 1.0.0
- **Status**: Production Ready
- **Tests**: 181+ tests
- **Coverage**: 70%+
- **Documentation**: Complete

## 💡 Support

- **Documentation**: This folder
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **GitHub Issues**: Report bugs and request features

## 📝 Contributing

Contributions are welcome! See [DEVELOPMENT.md](./DEVELOPMENT.md) for:
- Development setup
- Code style guide
- Testing requirements
- Pull request process

---

**Last Updated:** April 28, 2026  
**Version:** 1.0.0  
**Status:** Production Ready
