# Docker Quick Start Guide

## Prerequisites

- ✅ Docker Desktop installed and RUNNING
- ✅ `.env` and `backend/.env` files configured with your API keys

## Start the Application

### Windows (PowerShell):

```powershell
# Start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# View backend logs only
docker logs fina-backend --follow
```

### Linux/Mac:

```bash
# Make script executable (first time only)
chmod +x deploy.sh

# Start all services
./deploy.sh up

# Or use docker-compose directly
docker-compose up -d --build
```

## Wait for Services to Start

**Wait 30-60 seconds** for all services to initialize.

## Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Important: Clear Browser Cache

After starting Docker, you MUST clear your browser cache:

**Windows:**
```
Press: Ctrl + Shift + R
```

Or:
1. Press F12 (DevTools)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"

## Common Docker Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker logs fina-backend --follow
docker logs fina-nginx --follow
```

### Stop Services

```bash
# Stop (keeps data)
docker-compose down

# Stop and remove data
docker-compose down -v
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart nginx
```

### Check Status

```bash
# List running containers
docker-compose ps

# Check backend health
curl http://localhost:8000/health
```

### Rebuild After Code Changes

```bash
# Stop everything
docker-compose down

# Rebuild and start
docker-compose up -d --build --force-recreate

# Wait 30 seconds

# Clear browser cache (Ctrl + Shift + R)
```

## Troubleshooting

### Services won't start

```powershell
# Check if Docker Desktop is running
docker --version

# Check if ports are in use
netstat -ano | findstr :8000
netstat -ano | findstr :80

# Remove old containers
docker-compose down -v
docker-compose up -d --build --force-recreate
```

### Backend errors

```powershell
# View backend logs
docker logs fina-backend --follow

# Check environment variables
docker exec fina-backend env | findstr GROQ
docker exec fina-backend env | findstr SUPABASE

# Restart backend
docker-compose restart backend
```

### Frontend not loading

```powershell
# View nginx logs
docker logs fina-nginx --follow

# Check if nginx is running
docker ps | findstr nginx

# Restart nginx
docker-compose restart nginx

# Clear browser cache (Ctrl + Shift + R)
```

### Database connection fails

```powershell
# Check backend logs for database errors
docker logs fina-backend | findstr -i "database\|supabase\|connection"

# Verify DATABASE_URL in backend/.env
docker exec fina-backend cat /app/.env | findstr DATABASE_URL
```

## Services Overview

| Service | Port | Purpose |
|---------|------|---------|
| Frontend (Nginx) | 80 | Web interface |
| Backend (FastAPI) | 8000 | API server |
| Redis | 6379 | Caching |
| Prometheus | 9090 | Metrics |
| Grafana | 3000 | Dashboards |

## Environment Variables

### Required in `.env`:
```env
VITE_API_URL=http://localhost:8000
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=your_anon_key
```

### Required in `backend/.env`:
```env
DATABASE_URL=postgresql+psycopg2://...
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
GROQ_API_KEY=gsk_...
```

## Complete Reset

If nothing works, do a complete reset:

```powershell
# Stop everything
docker-compose down -v

# Remove images
docker rmi fina-backend fina-nginx

# Remove all stopped containers
docker container prune -f

# Remove all unused images
docker image prune -a -f

# Rebuild from scratch
docker-compose up -d --build --force-recreate

# Wait 60 seconds

# Close ALL browser windows

# Reopen browser in Incognito mode

# Go to http://localhost
```

## Verify Everything is Working

### 1. Check Docker containers:
```bash
docker-compose ps
```

All services should show "Up".

### 2. Check backend health:
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy"}`

### 3. Check frontend:
```bash
curl http://localhost
```

Should return HTML.

### 4. Check logs for errors:
```bash
docker-compose logs | findstr -i "error\|exception\|failed"
```

Should be minimal or no errors.

## Next Steps

1. ✅ Docker services running
2. ✅ Browser cache cleared
3. ✅ Go to http://localhost
4. ✅ Sign up / Login
5. ✅ Start using FinA!

---

**Last Updated**: April 28, 2026  
**Status**: Production Ready ✅
