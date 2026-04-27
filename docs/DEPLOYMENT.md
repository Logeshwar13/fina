# FinA Deployment Guide

Complete guide for deploying FinA to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Security Checklist](#security-checklist)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- Docker 20.10+ and Docker Compose 2.0+
- Supabase account (free tier available)
- Groq API key (free tier available)
- Domain name (for production)
- SSL certificate (Let's Encrypt recommended)

### Recommended
- Linux server (Ubuntu 22.04 LTS recommended)
- 2+ CPU cores
- 4GB+ RAM
- 20GB+ storage
- Reverse proxy (Nginx/Caddy)

---

## Local Development

### 1. Clone Repository

```bash
git clone https://github.com/your-username/fina.git
cd fina
```


Edit `backend/.env` 

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
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=http://localhost,http://localhost:8080

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### 3. Run with Docker

```bash
chmod +x deploy.sh
./deploy.sh up
```

### 4. Access Application

- Frontend: http://localhost
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Docker Deployment

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: fina-backend-prod
    restart: always
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=INFO
    env_file:
      - backend/.env
    volumes:
      - ./backend/logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - fina-network

  nginx:
    image: nginx:alpine
    container_name: fina-nginx-prod
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./public:/usr/share/nginx/html:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    networks:
      - fina-network

  prometheus:
    image: prom/prometheus:latest
    container_name: fina-prometheus-prod
    restart: always
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    networks:
      - fina-network

  grafana:
    image: grafana/grafana:latest
    container_name: fina-grafana-prod
    restart: always
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=your-secure-password
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - fina-network

networks:
  fina-network:
    driver: bridge

volumes:
  prometheus-data:
  grafana-data:
```

### Deploy to Production

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.prod.yml down
```

---

## Cloud Deployment

### AWS EC2

#### 1. Launch EC2 Instance

```bash
# Instance type: t3.medium or larger
# OS: Ubuntu 22.04 LTS
# Storage: 20GB+ EBS
# Security Group: Allow ports 22, 80, 443
```

#### 2. Connect and Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/your-username/fina.git
cd fina
```

#### 3. Configure and Deploy

```bash
# Setup environment
cp backend/.env.example backend/.env
nano backend/.env  # Edit with production values

# Deploy
docker-compose -f docker-compose.prod.yml up -d --build
```

#### 4. Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### DigitalOcean Droplet

Similar to AWS EC2, but use DigitalOcean's one-click Docker image:

```bash
# Create Droplet with Docker pre-installed
# Size: 2GB RAM / 1 CPU minimum
# Region: Choose closest to users

# SSH and deploy
ssh root@your-droplet-ip
git clone https://github.com/your-username/fina.git
cd fina
# Follow same steps as EC2
```

### Google Cloud Platform

```bash
# Create Compute Engine instance
gcloud compute instances create fina-instance \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB

# SSH and deploy
gcloud compute ssh fina-instance
# Follow same steps as EC2
```

### Heroku

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create your-fina-app

# Add buildpack
heroku buildpacks:set heroku/python

# Set environment variables
heroku config:set SUPABASE_URL=your_url
heroku config:set SUPABASE_KEY=your_key
heroku config:set GROQ_API_KEY=your_key

# Deploy
git push heroku main

# Open app
heroku open
```

---

## Environment Configuration

### Production Environment Variables

```env
# ============================================================================
# PRODUCTION CONFIGURATION
# ============================================================================

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key  # Use service role for backend

# LLM Provider
GROQ_API_KEY=your_groq_api_key
DEFAULT_LLM_PROVIDER=groq
DEFAULT_LLM_MODEL=llama-3.3-70b-versatile
MAX_TOKENS=1200
TEMPERATURE=0.7

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
PORT=8000
WORKERS=4  # Number of Uvicorn workers

# Security
SECRET_KEY=generate-a-strong-random-key-here
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_BURST=20

# Guardrails
MAX_TRANSACTION_AMOUNT=10000000
MAX_BUDGET_LIMIT=5000000
ENABLE_INPUT_VALIDATION=true
ENABLE_OUTPUT_SANITIZATION=true

# Observability
ENABLE_METRICS=true
ENABLE_TRACING=true
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# Caching (if using Redis)
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Generate Secret Key

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32
```

---

## Security Checklist

### Pre-Deployment

- [ ] Change `SECRET_KEY` to random string
- [ ] Set `DEBUG=false`
- [ ] Configure `CORS_ORIGINS` (no wildcards)
- [ ] Use service role key for Supabase (not anon key)
- [ ] Enable HTTPS/SSL
- [ ] Set strong passwords for Grafana
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Review and update `.gitignore`
- [ ] Remove test files from production

### Post-Deployment

- [ ] Test all endpoints
- [ ] Verify SSL certificate
- [ ] Check CORS configuration
- [ ] Test rate limiting
- [ ] Verify authentication
- [ ] Check error handling
- [ ] Test backup/restore
- [ ] Setup monitoring alerts
- [ ] Document deployment process
- [ ] Create runbook for incidents

### Nginx Security Headers

Add to `nginx.conf`:

```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

---

## Monitoring & Logging

### Prometheus Metrics

Access at `http://your-domain:9090`

Key metrics to monitor:
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `agent_execution_duration_seconds` - Agent execution time
- `llm_api_calls_total` - LLM API calls
- `database_query_duration_seconds` - Database query time

### Grafana Dashboards

Access at `http://your-domain:3000`

Create dashboards for:
- API request rate and latency
- Agent performance
- Error rates
- Database performance
- System resources (CPU, memory, disk)

### Application Logs

```bash
# View logs
docker-compose logs -f backend

# Save logs to file
docker-compose logs backend > logs/backend.log

# Tail logs
tail -f backend/logs/app.log
```

### Log Aggregation

For production, consider:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Loki** (with Grafana)
- **CloudWatch** (AWS)
- **Stackdriver** (GCP)

---

## Backup & Recovery

### Database Backup

```bash
# Supabase automatic backups (Pro plan)
# Or manual export via Supabase dashboard

# Backup to S3
aws s3 sync ./backups s3://your-bucket/fina-backups/
```

### Application Backup

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$DATE"

mkdir -p $BACKUP_DIR

# Backup environment
cp backend/.env $BACKUP_DIR/

# Backup logs
cp -r backend/logs $BACKUP_DIR/

# Backup Docker volumes
docker run --rm -v fina_prometheus-data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/prometheus-data.tar.gz -C /data .
docker run --rm -v fina_grafana-data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/grafana-data.tar.gz -C /data .

echo "Backup completed: $BACKUP_DIR"
```

### Restore

```bash
# Restore environment
cp backups/20260428_100000/.env backend/

# Restore Docker volumes
docker run --rm -v fina_prometheus-data:/data -v $(pwd)/backups/20260428_100000:/backup alpine tar xzf /backup/prometheus-data.tar.gz -C /data
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Check health
docker-compose ps

# Restart container
docker-compose restart backend

# Rebuild
docker-compose up -d --build --force-recreate
```

### High Memory Usage

```bash
# Check container stats
docker stats

# Limit memory in docker-compose.yml
services:
  backend:
    mem_limit: 2g
    mem_reservation: 1g
```

### Database Connection Issues

```bash
# Test Supabase connection
curl https://your-project.supabase.co/rest/v1/

# Check environment variables
docker-compose exec backend env | grep SUPABASE
```

### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew

# Test SSL
openssl s_client -connect your-domain.com:443

# Check certificate expiry
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Performance Issues

```bash
# Check system resources
htop
df -h
free -m

# Check Docker resources
docker system df

# Clean up
docker system prune -a
```

---

## Scaling

### Horizontal Scaling

```bash
# Scale backend workers
docker-compose up -d --scale backend=4

# Use load balancer (Nginx)
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
    server backend4:8000;
}
```

### Vertical Scaling

```bash
# Increase container resources
services:
  backend:
    cpus: '2.0'
    mem_limit: 4g
```

### Database Scaling

- Use Supabase connection pooling
- Enable read replicas
- Implement caching (Redis)
- Optimize queries

---

## Maintenance

### Regular Tasks

**Daily:**
- Check error logs
- Monitor metrics
- Verify backups

**Weekly:**
- Review performance
- Update dependencies
- Check disk space

**Monthly:**
- Security updates
- Certificate renewal
- Backup testing
- Performance optimization

### Update Procedure

```bash
# 1. Backup current state
./backup.sh

# 2. Pull latest changes
git pull origin main

# 3. Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Verify health
curl http://localhost:8000/health

# 5. Monitor logs
docker-compose logs -f backend
```

---

## Support

- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues
- **Health Check**: `curl http://your-domain/health`
- **Logs**: `docker-compose logs -f`

---

**Last Updated**: April 28, 2026
