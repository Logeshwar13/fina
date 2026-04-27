#!/bin/bash

# FinA Deployment Script
# Deploys the application using Docker Compose

set -e  # Exit on error

echo "================================"
echo "FinA Deployment Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}Error: backend/.env file not found${NC}"
    echo "Please copy backend/.env.example to backend/.env and configure it"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

# Parse command line arguments
COMMAND=${1:-up}

case $COMMAND in
    up)
        echo -e "${GREEN}Starting FinA services...${NC}"
        docker-compose up -d
        echo -e "${GREEN}Services started successfully!${NC}"
        echo ""
        echo "Access the application at:"
        echo "  Frontend: http://localhost"
        echo "  Backend API: http://localhost:8000"
        echo "  API Docs: http://localhost:8000/docs"
        echo "  Grafana: http://localhost:3000"
        echo "  Prometheus: http://localhost:9090"
        ;;
    
    down)
        echo -e "${YELLOW}Stopping FinA services...${NC}"
        docker-compose down
        echo -e "${GREEN}Services stopped${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}Restarting FinA services...${NC}"
        docker-compose restart
        echo -e "${GREEN}Services restarted${NC}"
        ;;
    
    logs)
        echo -e "${GREEN}Showing logs...${NC}"
        docker-compose logs -f
        ;;
    
    build)
        echo -e "${GREEN}Building Docker images...${NC}"
        docker-compose build --no-cache
        echo -e "${GREEN}Build complete${NC}"
        ;;
    
    clean)
        echo -e "${YELLOW}Cleaning up Docker resources...${NC}"
        docker-compose down -v
        docker system prune -f
        echo -e "${GREEN}Cleanup complete${NC}"
        ;;
    
    status)
        echo -e "${GREEN}Service status:${NC}"
        docker-compose ps
        ;;
    
    health)
        echo -e "${GREEN}Checking health...${NC}"
        curl -f http://localhost:8000/health || echo -e "${RED}Backend unhealthy${NC}"
        ;;
    
    *)
        echo "Usage: $0 {up|down|restart|logs|build|clean|status|health}"
        echo ""
        echo "Commands:"
        echo "  up       - Start all services"
        echo "  down     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - Show service logs"
        echo "  build    - Rebuild Docker images"
        echo "  clean    - Clean up Docker resources"
        echo "  status   - Show service status"
        echo "  health   - Check application health"
        exit 1
        ;;
esac
