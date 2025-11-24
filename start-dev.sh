#!/bin/bash
# GPT-OSS Development Environment Startup Script
# Bash script to start all services including frontend

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  GPT-OSS Development Environment${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Check if Docker is running
echo -e "${YELLOW}[1/5] Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Docker is not running!${NC}"
    echo -e "${RED}Please start Docker and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Stop existing containers
echo -e "${YELLOW}[2/5] Stopping existing containers...${NC}"
docker-compose down
echo -e "${GREEN}✓ Containers stopped${NC}"
echo ""

# Build and start services
echo -e "${YELLOW}[3/5] Building and starting services...${NC}"
echo -e "${GRAY}This may take 5-10 minutes on first run...${NC}"
docker-compose up -d --build

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to start services!${NC}"
    echo -e "${RED}Check docker-compose logs for details${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Services started${NC}"
echo ""

# Wait for services to be healthy
echo -e "${YELLOW}[4/5] Waiting for services to be ready...${NC}"
echo -e "${GRAY}Waiting for backend...${NC}"
BACKEND_READY=false
for i in {1..30}; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null | grep -q "200"; then
        BACKEND_READY=true
        break
    fi
    sleep 2
done

if [ "$BACKEND_READY" = false ]; then
    echo -e "${YELLOW}WARNING: Backend did not respond within 60 seconds${NC}"
    echo -e "${YELLOW}Check logs: docker-compose logs backend${NC}"
else
    echo -e "${GREEN}✓ Backend is ready${NC}"
fi

echo -e "${GRAY}Waiting for frontend...${NC}"
FRONTEND_READY=false
for i in {1..30}; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 2>/dev/null | grep -q "200"; then
        FRONTEND_READY=true
        break
    fi
    sleep 2
done

if [ "$FRONTEND_READY" = false ]; then
    echo -e "${YELLOW}WARNING: Frontend did not respond within 60 seconds${NC}"
    echo -e "${YELLOW}Check logs: docker-compose logs frontend${NC}"
else
    echo -e "${GREEN}✓ Frontend is ready${NC}"
fi
echo ""

# Display service URLs
echo -e "${YELLOW}[5/5] Services are running!${NC}"
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Service URLs${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${WHITE}Frontend:       ${GREEN}http://localhost:5173${NC}"
echo -e "${WHITE}Backend API:    ${GREEN}http://localhost:8000${NC}"
echo -e "${WHITE}API Docs:       ${GREEN}http://localhost:8000/docs${NC}"
echo -e "${WHITE}LLM Service:    ${GREEN}http://localhost:8080${NC}"
echo -e "${WHITE}Neo4j Browser:  ${GREEN}http://localhost:7474${NC}"
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Useful Commands${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${WHITE}View logs (all):       ${YELLOW}docker-compose logs -f${NC}"
echo -e "${WHITE}View logs (frontend):  ${YELLOW}docker-compose logs -f frontend${NC}"
echo -e "${WHITE}View logs (backend):   ${YELLOW}docker-compose logs -f backend${NC}"
echo -e "${WHITE}Stop all services:     ${YELLOW}docker-compose down${NC}"
echo -e "${WHITE}Restart a service:     ${YELLOW}docker-compose restart <service>${NC}"
echo ""
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${GRAY}Press Ctrl+C to stop watching logs${NC}"
echo ""

# Follow logs
docker-compose logs -f
