# GPT-OSS Setup Guide

**Version**: Stage 1 - Foundation
**Last Updated**: 2025-11-18
**Target Audience**: Developers, system administrators, DevOps

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Prerequisites](#prerequisites)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Database Setup](#database-setup)
7. [GPU Configuration](#gpu-configuration)
8. [Troubleshooting](#troubleshooting)
9. [Production Deployment](#production-deployment)
10. [Upgrading to PostgreSQL](#upgrading-to-postgresql)

---

## System Requirements

### Minimum Requirements

- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 12+
- **CPU**: 8-core processor (Intel i7/AMD Ryzen 7 or better)
- **RAM**: 16 GB minimum, 32 GB recommended
- **GPU**: RTX 4070 (8GB VRAM) or better
- **Disk**: 50 GB free space (SSD recommended)
- **Network**: 100 Mbps for initial model download

### Recommended Configuration

- **OS**: Windows 11 or Linux (Ubuntu 22.04)
- **CPU**: 12-core processor
- **RAM**: 32-64 GB
- **GPU**: RTX 5090 (32GB VRAM) or RTX 4090 (24GB)
- **Disk**: 100 GB free space on NVMe SSD
- **Network**: Gigabit Ethernet

### Supported GPUs

**Excellent Performance** (recommended):
- NVIDIA RTX 5090 (32GB VRAM)
- NVIDIA RTX 4090 (24GB VRAM)
- NVIDIA A6000 (48GB VRAM)

**Good Performance**:
- NVIDIA RTX 4070 (8GB VRAM)
- NVIDIA RTX 4080 (16GB VRAM)
- NVIDIA A5000 (24GB VRAM)

**Basic Performance** (limited):
- NVIDIA RTX 3060 (12GB VRAM)
- NVIDIA RTX 3070 (8GB VRAM)

**Not Recommended**:
- GPUs with <8GB VRAM (will run in CPU-only mode, very slow)
- AMD GPUs (llama.cpp CUDA support required)

---

## Prerequisites

### 1. Docker and Docker Compose

**Windows**:
```powershell
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker-compose --version
```

**Linux (Ubuntu)**:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

**macOS**:
```bash
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker-compose --version
```

### 2. NVIDIA GPU Drivers and CUDA

**Windows**:
```powershell
# Download NVIDIA drivers from:
# https://www.nvidia.com/download/index.aspx

# Verify GPU
nvidia-smi

# Install CUDA Toolkit (optional, Docker images include CUDA)
# https://developer.nvidia.com/cuda-downloads
```

**Linux**:
```bash
# Install NVIDIA drivers
sudo apt install nvidia-driver-535

# Install NVIDIA Docker runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install -y nvidia-docker2
sudo systemctl restart docker

# Verify GPU in Docker
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### 3. Node.js and npm (for frontend development)

**All Platforms**:
```bash
# Install Node.js 18+ LTS
# Download from: https://nodejs.org/

# Verify installation
node --version  # Should be v18.x or higher
npm --version   # Should be 9.x or higher
```

### 4. Git

**All Platforms**:
```bash
# Verify Git is installed
git --version

# If not installed:
# Windows: https://git-scm.com/download/win
# Linux: sudo apt install git
# macOS: brew install git
```

---

## Installation Steps

### 1. Clone the Repository

```bash
# Clone the project
cd D:\  # Or your preferred directory
git clone <repository-url> gpt-oss
cd gpt-oss

# Or if starting from existing directory
cd D:\gpt-oss
```

### 2. Download LLM Model

**Option A: Automatic Download** (recommended):

```bash
# Create models directory
mkdir -p models

# Download Mistral Small 24B Q6_K (20GB)
# Using wget (Linux/macOS) or PowerShell (Windows)

# Windows PowerShell:
Invoke-WebRequest -Uri "https://huggingface.co/bartowski/Mistral-Small-24B-Instruct-2501-GGUF/resolve/main/Mistral-Small-24B-Instruct-2501-Q6_K.gguf" -OutFile "models/Mistral-Small-24B-Instruct-2501-Q6_K.gguf"

# Linux/macOS:
wget -O models/Mistral-Small-24B-Instruct-2501-Q6_K.gguf \
  "https://huggingface.co/bartowski/Mistral-Small-24B-Instruct-2501-GGUF/resolve/main/Mistral-Small-24B-Instruct-2501-Q6_K.gguf"
```

**Option B: Manual Download**:
1. Visit: https://huggingface.co/bartowski/Mistral-Small-24B-Instruct-2501-GGUF
2. Download `Mistral-Small-24B-Instruct-2501-Q6_K.gguf`
3. Move to `D:\gpt-oss\models\`

**Verify Model**:
```bash
# Check file size (should be ~20GB)
ls -lh models/Mistral-Small-24B-Instruct-2501-Q6_K.gguf
```

### 3. Create Data Directories

```bash
# Create required directories
mkdir -p data          # SQLite database
mkdir -p uploads       # Document uploads (future stages)
mkdir -p rag_data      # LightRAG working directory (future stages)
```

### 4. Configure Environment

**Backend Configuration** (optional):

Create `backend/.env` if you need custom settings:

```bash
# Database
DATABASE_URL=sqlite:///./data/gpt_oss.db

# LLM Service
LLM_API_URL=http://llama:8080

# Neo4j (future stages)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password123

# ChromaDB (future stages)
VECTOR_DB_TYPE=chroma
CHROMA_HOST=chroma
CHROMA_PORT=8001

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Debug
DEBUG=false
```

**Default values** are already set in `backend/app/config.py`, so this file is optional.

### 5. Identify Your GPU

**Windows**:
```powershell
# List available GPUs
nvidia-smi -L

# Get GPU UUID
nvidia-smi -L | Select-String -Pattern "GPU-.*"
```

**Linux**:
```bash
# List available GPUs
nvidia-smi -L

# Get GPU UUID
nvidia-smi -L | grep -oP 'GPU-[a-f0-9-]+'
```

**Example Output**:
```
GPU 0: NVIDIA GeForce RTX 5090 (UUID: GPU-3143337d-5132-41c1-9381-33b56ef28990)
```

### 6. Update docker-compose.yml

Edit `docker-compose.yml` and set your GPU UUID:

```yaml
llama:
  image: ghcr.io/ggerganov/llama.cpp:server-cuda
  environment:
    # REPLACE WITH YOUR GPU UUID FROM nvidia-smi -L
    NVIDIA_VISIBLE_DEVICES: "GPU-3143337d-5132-41c1-9381-33b56ef28990"
```

**For CPU-only mode** (not recommended):
```yaml
llama:
  image: ghcr.io/ggerganov/llama.cpp:server
  # Remove all GPU-related settings
```

---

## Running the Application

### 1. Start Backend Services

**First-time startup** (downloads Docker images, 10-20 minutes):

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

**Services started**:
- `backend`: FastAPI application (port 8000)
- `llama`: LLM inference service (port 8080)
- `neo4j`: Graph database (ports 7474, 7687) - future stages
- `chroma`: Vector database (port 8001) - future stages

### 2. Verify Services

**Check service status**:
```bash
# List running containers
docker-compose ps

# Expected output:
# backend    running    0.0.0.0:8000->8000/tcp
# llama      running    0.0.0.0:8080->8080/tcp
```

**Check health**:
```bash
# Backend health
curl http://localhost:8000/health

# Expected: {"status":"healthy","database":"connected","llm_service":"available"}

# LLM health
curl http://localhost:8080/health

# Expected: {"status":"ok"}
```

**View logs**:
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# LLM service only
docker-compose logs -f llama
```

### 3. Initialize Database

Database is **automatically initialized** on first backend startup.

**Verify database**:
```bash
# Check database file exists
ls -lh data/gpt_oss.db

# Check WAL mode enabled
sqlite3 data/gpt_oss.db "PRAGMA journal_mode;"
# Expected: wal
```

### 4. Start Frontend (Development)

**Install dependencies** (first time only):
```bash
cd frontend
npm install
```

**Run development server**:
```bash
npm run dev
```

**Access frontend**: http://localhost:3000

**Alternative: Build for production**:
```bash
npm run build

# Output in: .svelte-kit/output/
# Bundle size: ~267 KB
```

---

## Database Setup

### SQLite (Default)

**Location**: `./data/gpt_oss.db`

**Configuration**: Automatic (no setup required)

**Features**:
- WAL mode for concurrent access
- Foreign key constraints enabled
- 10MB cache size
- Auto-vacuum enabled

**Backup**:
```bash
# Backup database
cp data/gpt_oss.db backup/gpt_oss_$(date +%Y%m%d).db

# Backup WAL files too
cp data/gpt_oss.db-wal backup/
cp data/gpt_oss.db-shm backup/
```

**Restore**:
```bash
# Stop backend
docker-compose stop backend

# Restore database
cp backup/gpt_oss_20251118.db data/gpt_oss.db

# Start backend
docker-compose start backend
```

### PostgreSQL (Production)

See [Upgrading to PostgreSQL](#upgrading-to-postgresql) section below.

---

## GPU Configuration

### Check GPU Status

```bash
# GPU utilization
nvidia-smi

# Detailed GPU info
nvidia-smi -q

# Watch GPU in real-time
watch -n 1 nvidia-smi
```

### Adjust GPU Memory Usage

If you encounter **CUDA out of memory** errors:

**Option 1: Reduce GPU layers** (offload some to CPU):

Edit `docker-compose.yml`:
```yaml
llama:
  command:
    - --model
    - /models/Mistral-Small-24B-Instruct-2501-Q6_K.gguf
    - -ngl 50        # Reduce from 99 (default: all layers)
    - -c 32768
    - --port 8080
    - --host 0.0.0.0
```

**Option 2: Reduce context length**:

```yaml
llama:
  command:
    - --model
    - /models/Mistral-Small-24B-Instruct-2501-Q6_K.gguf
    - -ngl 99
    - -c 16384       # Reduce from 32768
    - --port 8080
    - --host 0.0.0.0
```

**Option 3: Use smaller quantization**:

Download Q4_K_M instead of Q6_K (smaller, faster, slightly lower quality):
```bash
wget -O models/Mistral-Small-24B-Instruct-2501-Q4_K_M.gguf \
  "https://huggingface.co/bartowski/Mistral-Small-24B-Instruct-2501-GGUF/resolve/main/Mistral-Small-24B-Instruct-2501-Q4_K_M.gguf"
```

Update `docker-compose.yml`:
```yaml
llama:
  command:
    - --model
    - /models/Mistral-Small-24B-Instruct-2501-Q4_K_M.gguf  # Changed filename
```

**Restart services**:
```bash
docker-compose restart llama
```

### CPU-Only Mode

If no GPU available:

**Option 1: Use llama-server (CPU-optimized)**:

Edit `docker-compose.yml`:
```yaml
llama:
  image: ghcr.io/ggerganov/llama.cpp:server  # Remove -cuda suffix
  # Remove NVIDIA_VISIBLE_DEVICES environment variable
  command:
    - --model
    - /models/Mistral-Small-24B-Instruct-2501-Q4_K_M.gguf  # Use smaller model
    - -c 8192        # Reduce context length
    - --port 8080
    - --host 0.0.0.0
```

**Performance**: ~10-20x slower than GPU mode (first token: 2-5 seconds instead of 270ms)

---

## Configuration

### Backend Configuration

**File**: `backend/app/config.py`

**Key Settings**:

```python
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./data/gpt_oss.db"

    # LLM Service
    LLM_API_URL: str = "http://llama:8080"
    LLM_MODEL_NAME: str = "mistral-small-24b"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000
    LLM_TIMEOUT: int = 30

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
```

**Override via environment variables**:
```bash
export DATABASE_URL="postgresql://user:pass@localhost/gpt_oss"
export LLM_TEMPERATURE=0.5
docker-compose restart backend
```

### Frontend Configuration

**File**: `frontend/src/lib/config.ts` (to be created)

```typescript
export const API_URL = 'http://localhost:8000';
export const WS_URL = 'ws://localhost:8000';
```

### Docker Compose Configuration

**File**: `docker-compose.yml`

**Backend Service**:
```yaml
backend:
  build: ./backend
  ports:
    - "8000:8000"
  volumes:
    - ./data:/app/data
    - ./uploads:/app/uploads
    - ./rag_data:/app/rag_data
  environment:
    - DATABASE_URL=sqlite:///./data/gpt_oss.db
    - LLM_API_URL=http://llama:8080
```

**LLM Service**:
```yaml
llama:
  image: ghcr.io/ggerganov/llama.cpp:server-cuda
  ports:
    - "8080:8080"
  volumes:
    - ./models:/models
  environment:
    - NVIDIA_VISIBLE_DEVICES=GPU-<your-gpu-uuid>
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

---

## Troubleshooting

### Services Won't Start

**Problem**: `docker-compose up` fails

**Solutions**:

1. **Check Docker is running**:
   ```bash
   docker ps
   ```

2. **Check port conflicts**:
   ```bash
   # Windows
   netstat -ano | findstr :8000

   # Linux/macOS
   lsof -i :8000
   ```

3. **View error logs**:
   ```bash
   docker-compose logs backend
   docker-compose logs llama
   ```

4. **Rebuild containers**:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

### GPU Not Detected

**Problem**: llama service runs on CPU despite GPU available

**Solutions**:

1. **Verify GPU UUID** in docker-compose.yml matches `nvidia-smi -L`

2. **Check NVIDIA Docker runtime**:
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
   ```

3. **Check Docker Compose GPU config**:
   ```yaml
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: 1
             capabilities: [gpu]
   ```

4. **Restart Docker service** (Linux):
   ```bash
   sudo systemctl restart docker
   ```

### Database Locked Errors

**Problem**: `database is locked` errors in logs

**Solutions**:

1. **Verify WAL mode**:
   ```bash
   sqlite3 data/gpt_oss.db "PRAGMA journal_mode;"
   # Should return: wal
   ```

2. **Check for stale locks**:
   ```bash
   # Stop backend
   docker-compose stop backend

   # Remove WAL files
   rm data/gpt_oss.db-wal
   rm data/gpt_oss.db-shm

   # Start backend
   docker-compose start backend
   ```

3. **Upgrade to PostgreSQL** (see below)

### LLM Service Timeout

**Problem**: Chat requests timeout after 30 seconds

**Solutions**:

1. **Increase timeout** in `backend/app/config.py`:
   ```python
   LLM_TIMEOUT: int = 60  # Increase from 30
   ```

2. **Reduce context length** in docker-compose.yml:
   ```yaml
   - -c 16384  # Reduce from 32768
   ```

3. **Use smaller model** (Q4_K_M instead of Q6_K)

### Frontend Build Fails

**Problem**: `npm run build` fails

**Solutions**:

1. **Clear npm cache**:
   ```bash
   npm cache clean --force
   rm -rf node_modules
   npm install
   ```

2. **Check Node.js version**:
   ```bash
   node --version  # Should be 18.x or higher
   ```

3. **View detailed errors**:
   ```bash
   npm run build -- --verbose
   ```

---

## Production Deployment

### Security Hardening

**1. Disable DEBUG mode**:
```python
# backend/app/config.py
DEBUG: bool = False
```

**2. Configure CORS for production domain**:
```python
CORS_ORIGINS: str = "https://your-domain.com"
```

**3. Use environment variables for secrets**:
```bash
export NEO4J_PASSWORD="your-secure-password"
export DATABASE_URL="postgresql://user:secure-password@db-host/gpt_oss"
```

**4. Enable HTTPS** (reverse proxy with nginx):

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Database Backup

**Automated backup script**:

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup SQLite database
sqlite3 data/gpt_oss.db ".backup ${BACKUP_DIR}/gpt_oss_${DATE}.db"

# Backup uploaded documents
tar -czf ${BACKUP_DIR}/uploads_${DATE}.tar.gz uploads/

# Keep only last 30 days
find ${BACKUP_DIR} -name "gpt_oss_*.db" -mtime +30 -delete
find ${BACKUP_DIR} -name "uploads_*.tar.gz" -mtime +30 -delete

echo "Backup completed: ${DATE}"
```

**Cron job** (run daily at 2 AM):
```cron
0 2 * * * /path/to/backup.sh >> /var/log/gpt-oss-backup.log 2>&1
```

### Monitoring

**Health check endpoint**:
```bash
curl http://localhost:8000/health
```

**Prometheus metrics** (future stages):
- Request latency (P50, P95, P99)
- Error rates
- Database query performance
- GPU utilization

---

## Upgrading to PostgreSQL

### Why Upgrade?

**SQLite limitations**:
- Single-user or small team only
- Limited concurrent writes
- No built-in replication

**PostgreSQL benefits**:
- Multi-user support
- Better concurrency (100+ concurrent users)
- Built-in replication and backups
- Advanced features (full-text search, JSON indexing)

### Migration Steps

**1. Start PostgreSQL**:

Uncomment in `docker-compose.yml`:
```yaml
postgres:
  image: postgres:15
  environment:
    POSTGRES_USER: gpt_oss
    POSTGRES_PASSWORD: your-secure-password
    POSTGRES_DB: gpt_oss
  ports:
    - "5432:5432"
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

Start PostgreSQL:
```bash
docker-compose up -d postgres
```

**2. Export SQLite data**:

```bash
# Dump data to SQL
sqlite3 data/gpt_oss.db .dump > backup/sqlite_dump.sql
```

**3. Update DATABASE_URL**:

```python
# backend/app/config.py
DATABASE_URL: str = "postgresql://gpt_oss:your-secure-password@postgres:5432/gpt_oss"
```

**4. Initialize PostgreSQL schema**:

```bash
# Restart backend (creates tables automatically)
docker-compose restart backend
```

**5. Import SQLite data**:

```bash
# Install pgloader (Linux)
sudo apt install pgloader

# Migrate data
pgloader sqlite://data/gpt_oss.db postgresql://gpt_oss:your-secure-password@localhost:5432/gpt_oss
```

**6. Verify migration**:

```bash
# Connect to PostgreSQL
docker exec -it gpt-oss-postgres psql -U gpt_oss

# Check tables
\dt

# Check record counts
SELECT 'projects' AS table, COUNT(*) FROM projects
UNION ALL
SELECT 'conversations', COUNT(*) FROM conversations
UNION ALL
SELECT 'messages', COUNT(*) FROM messages;

# Exit
\q
```

**7. Test application**:

```bash
# Health check
curl http://localhost:8000/health

# Create test project
curl -X POST http://localhost:8000/api/projects/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project", "description": "Migration test"}'
```

**8. Remove SQLite** (optional):

```bash
# Backup SQLite before removing
cp data/gpt_oss.db backup/

# Remove SQLite database
rm data/gpt_oss.db*
```

---

## Appendix: Directory Structure

```
D:\gpt-oss\
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── api/                 # API endpoints
│   │   ├── services/            # Business logic
│   │   └── db/                  # Database session
│   ├── tests/                   # Backend tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── routes/              # SvelteKit routes
│   │   └── lib/                 # Components, stores
│   ├── package.json
│   └── vite.config.ts
├── models/                      # LLM model files
│   └── Mistral-Small-24B-Instruct-2501-Q6_K.gguf
├── data/                        # SQLite database
│   ├── gpt_oss.db
│   ├── gpt_oss.db-wal
│   └── gpt_oss.db-shm
├── uploads/                     # Document uploads (future)
├── rag_data/                    # LightRAG data (future)
├── docs/                        # Documentation
│   ├── user-manual.md
│   ├── api-documentation.md
│   └── setup-guide.md
├── .claude-bus/                 # Multi-agent workflow
├── docker-compose.yml
└── README.md
```

---

**Document Version**: 1.0
**Stage**: Stage 1 - Foundation
**Next Update**: After Stage 2 completion (RAG deployment)
