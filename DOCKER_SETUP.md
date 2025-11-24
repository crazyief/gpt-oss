# Docker Setup Guide for GPT-OSS

This guide explains how to run the entire GPT-OSS stack using Docker, including the frontend development server.

## Quick Start

### Windows (PowerShell)
```powershell
.\start-dev.ps1
```

### Linux/macOS (Bash)
```bash
./start-dev.sh
```

This single command will:
1. Check if Docker is running
2. Stop any existing containers
3. Build and start all services
4. Wait for services to be healthy
5. Display service URLs
6. Follow logs in real-time

---

## Manual Startup

If you prefer manual control:

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

---

## Services Included

### Frontend (Port 5173)
- **Container**: `gpt-oss-frontend`
- **Image**: Built from `./frontend/Dockerfile.dev`
- **URL**: http://localhost:5173
- **Features**:
  - Vite dev server with hot-reload
  - API proxy to backend (no CORS issues)
  - Live code changes without restart
  - Source maps for debugging

### Backend (Port 8000)
- **Container**: `gpt-oss-backend`
- **Image**: Built from `./backend/Dockerfile`
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### LLM Service (Port 8080)
- **Container**: `mistral-small-24b-Q6_K-llama`
- **Image**: `ghcr.io/ggml-org/llama.cpp:server-cuda`
- **URL**: http://localhost:8080

### Neo4j (Ports 7474, 7687)
- **Container**: `gpt-oss-neo4j`
- **Image**: `neo4j:5.13.0`
- **Browser**: http://localhost:7474
- **Credentials**: `neo4j / password123`

### ChromaDB (Port 8001)
- **Container**: `gpt-oss-chroma`
- **Image**: `chromadb/chroma:latest`
- **URL**: http://localhost:8001

---

## Frontend Docker Configuration

### Development Mode (Default)

**Dockerfile**: `frontend/Dockerfile.dev`

**Features**:
- Node.js 18 Alpine base image
- Hot-reload support via volume mounts
- Vite dev server on port 5173
- Source code mounted from `./frontend` directory

**Configuration in `docker-compose.yml`**:
```yaml
frontend:
  container_name: gpt-oss-frontend
  build:
    context: ./frontend
    dockerfile: Dockerfile.dev
  ports:
    - "5173:5173"
  volumes:
    - ./frontend:/app              # Mount source code
    - /app/node_modules            # Preserve container's node_modules
  environment:
    - NODE_ENV=development
    - VITE_BACKEND_URL=http://backend:8000  # Backend service name
  depends_on:
    - backend
  networks:
    - gpt-oss-network
```

**Why Volume Mounts?**
- `./frontend:/app` - Syncs your code changes to the container
- `/app/node_modules` - Prevents overwriting container's node_modules with host's version (important for cross-platform compatibility)

### Production Mode

**Dockerfile**: `frontend/Dockerfile`

**Features**:
- Multi-stage build for optimization
- Static file serving
- No hot-reload (production deployment)

**To use production mode**:
```bash
# Edit docker-compose.yml:
# Change: dockerfile: Dockerfile.dev
# To:     dockerfile: Dockerfile

docker-compose up -d --build frontend
```

---

## API Proxy Configuration

The frontend uses Vite's proxy feature to forward API requests to the backend.

**Why Proxy?**
- Frontend runs on port 5173
- Backend runs on port 8000
- Without proxy, browser blocks requests (CORS)
- With proxy, Vite forwards `/api/*` to backend

**How it Works** (from `vite.config.ts`):
```typescript
server: {
  port: 5173,
  host: true,  // Listen on all interfaces (required for Docker)
  proxy: {
    '/api': {
      target: process.env.VITE_BACKEND_URL || 'http://localhost:8000',
      changeOrigin: true,
      secure: false
    }
  }
}
```

**Request Flow**:
1. Component calls: `fetch('/api/projects/list')`
2. Browser sends to: `http://localhost:5173/api/projects/list`
3. Vite proxy forwards to: `http://backend:8000/api/projects/list`
4. Backend responds → Vite forwards → Browser receives

**Environment Variables**:
- `VITE_BACKEND_URL=http://backend:8000` (in Docker)
- `VITE_BACKEND_URL=http://localhost:8000` (running frontend locally)

---

## Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f llama

# Last 100 lines
docker-compose logs --tail=100 frontend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart frontend
docker-compose restart backend
```

### Rebuild Containers

```bash
# Rebuild all (after code changes to Dockerfile)
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build frontend

# Force rebuild (no cache)
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Enter Container

```bash
# Frontend shell
docker exec -it gpt-oss-frontend sh

# Backend shell
docker exec -it gpt-oss-backend bash

# Run commands inside container
docker exec -it gpt-oss-frontend npm list
docker exec -it gpt-oss-backend pip list
```

### Check Service Status

```bash
# List running containers
docker-compose ps

# Check service health
curl http://localhost:8000/health  # Backend
curl http://localhost:5173         # Frontend
curl http://localhost:8080/health  # LLM
```

---

## Troubleshooting

### Frontend Not Starting

**Symptoms**: `docker-compose ps` shows frontend as exited

**Solutions**:

1. **Check logs**:
   ```bash
   docker-compose logs frontend
   ```

2. **Common errors**:
   - **"Cannot find module '@sveltejs/kit'"**: Dependencies not installed
     ```bash
     docker-compose build --no-cache frontend
     docker-compose up -d frontend
     ```

   - **"Port 5173 already in use"**: Kill existing process
     ```bash
     # Windows
     netstat -ano | findstr :5173
     taskkill /PID <PID> /F

     # Linux/macOS
     lsof -i :5173
     kill -9 <PID>
     ```

   - **"EACCES: permission denied"**: Node modules permission issue
     ```bash
     docker-compose down
     docker volume rm gpt-oss_frontend_node_modules
     docker-compose up -d --build frontend
     ```

### Hot Reload Not Working

**Symptoms**: Code changes don't appear in browser

**Solutions**:

1. **Check volume mounts**:
   ```bash
   docker inspect gpt-oss-frontend | grep -A 10 "Mounts"
   ```
   Should show `./frontend:/app`

2. **Force browser refresh**: Ctrl+Shift+R (hard refresh)

3. **Check Vite config** (`vite.config.ts`):
   ```typescript
   server: {
     host: true,  // Must be true for Docker
     port: 5173
   }
   ```

4. **Restart frontend container**:
   ```bash
   docker-compose restart frontend
   ```

### API Requests Failing (CORS)

**Symptoms**: Browser console shows CORS errors

**Solutions**:

1. **Verify proxy is working**:
   - Open browser DevTools → Network tab
   - Make API request
   - Check if request goes to `http://localhost:5173/api/...` (not `http://localhost:8000/api/...`)

2. **Check backend CORS config** (`docker-compose.yml`):
   ```yaml
   backend:
     environment:
       - CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```

3. **Restart backend**:
   ```bash
   docker-compose restart backend
   ```

### Node Modules Out of Sync

**Symptoms**: Different errors on host vs container

**Solutions**:

1. **Rebuild container**:
   ```bash
   docker-compose down
   docker-compose up -d --build frontend
   ```

2. **Remove host node_modules** (optional):
   ```bash
   rm -rf frontend/node_modules
   docker-compose restart frontend
   ```

---

## Development Workflow

### Making Code Changes

**Frontend**:
1. Edit files in `./frontend/src/`
2. Changes auto-reload in browser (Vite HMR)
3. No need to restart container

**Backend**:
1. Edit files in `./backend/app/`
2. Uvicorn auto-reloads (--reload flag)
3. No need to restart container

**Docker Configuration** (requires rebuild):
1. Edit `Dockerfile.dev` or `docker-compose.yml`
2. Rebuild: `docker-compose up -d --build frontend`

### Adding Dependencies

**Frontend**:
```bash
# Option 1: Install inside container
docker exec -it gpt-oss-frontend npm install <package>
docker-compose restart frontend

# Option 2: Install on host, rebuild container
cd frontend
npm install <package>
docker-compose up -d --build frontend
```

**Backend**:
```bash
# Option 1: Install inside container
docker exec -it gpt-oss-backend pip install <package>
docker-compose restart backend

# Option 2: Add to requirements.txt, rebuild
echo "<package>" >> backend/requirements.txt
docker-compose up -d --build backend
```

---

## Production Deployment

For production, switch to production Dockerfiles:

**Frontend** (`docker-compose.yml`):
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile  # Use production Dockerfile
  ports:
    - "3000:3000"  # Production port
  environment:
    - NODE_ENV=production
```

**Backend** (already production-ready):
- Remove `--reload` flag from uvicorn command
- Set `DEBUG=false`
- Use PostgreSQL instead of SQLite
- Configure proper secrets

**Build and Deploy**:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## Docker Compose Override

For local customization without modifying `docker-compose.yml`:

**Create** `docker-compose.override.yml`:
```yaml
services:
  frontend:
    environment:
      - VITE_BACKEND_URL=http://my-custom-backend:8000
```

Docker Compose automatically merges `docker-compose.yml` + `docker-compose.override.yml`.

---

## Cleanup

**Stop and remove containers**:
```bash
docker-compose down
```

**Remove volumes** (deletes data):
```bash
docker-compose down -v
```

**Remove images**:
```bash
docker-compose down --rmi all
```

**Clean everything** (nuclear option):
```bash
docker-compose down -v --rmi all
docker system prune -af --volumes
```

---

## Performance Tips

1. **Use .dockerignore**:
   - Already configured in `frontend/.dockerignore`
   - Excludes `node_modules`, `.git`, build output

2. **Layer Caching**:
   - `package.json` copied before source code
   - Allows Docker to cache `npm install` layer

3. **Multi-stage Builds** (production):
   - Stage 1: Build application
   - Stage 2: Only copy built files
   - Reduces final image size by 50-70%

4. **Volume Performance** (Windows):
   - Use WSL2 backend for better I/O
   - Store source code in WSL2 filesystem

---

## Summary

You now have a fully Dockerized development environment with:
- ✅ One-command startup (`start-dev.ps1` or `start-dev.sh`)
- ✅ Hot-reload for both frontend and backend
- ✅ API proxy (no CORS issues)
- ✅ All services networked together
- ✅ Easy log viewing and debugging
- ✅ Production-ready Dockerfiles

**Next Steps**:
1. Run `.\start-dev.ps1` (Windows) or `./start-dev.sh` (Linux/macOS)
2. Open http://localhost:5173 in your browser
3. Start developing!

For more details, see:
- User Manual: `docs/user-manual.md`
- API Documentation: `docs/api-documentation.md`
- Setup Guide: `docs/setup-guide.md`
