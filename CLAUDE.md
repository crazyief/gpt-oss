# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Project: Local AI Knowledge Assistant (LightRAG)

### Quick Context
Building a LightRAG-based system for cybersecurity document analysis (IEC 62443, ETSI EN 303 645, EN 18031) with full audit trails and source transparency.

### Key Project Files (Auto-Loaded via @ references)
- Documentation: @todo/*.html @todo/*.md (all workflow & agent docs)
  - Critical: MESSAGE_BUS_PROTOCOL.md - How agents communicate
  - PROJECT_STATUS.md - Current progress tracker
  - STAGE_DEFINITIONS.md - Stage roadmap
- Agent Configs: @.claude-bus/agents/*.md (all agent definitions)
- Current Tasks: @.claude-bus/tasks/*.json (active work items)
- Planning Docs: @.claude-bus/planning/*.json (requirements)
- Project History: @bak/*.md (vision & architecture)

## Multi-Agent Workflow

### 6 Agents Working in Parallel
1. **PM-Architect-Agent** (Opus) - Planning & Architecture
2. **Document-RAG-Agent** (Sonnet) - RAG Pipeline & Docs
3. **Backend-Agent** (Sonnet) - FastAPI & Database
4. **Frontend-Agent** (Sonnet) - UI Development
5. **QA-Agent** (Sonnet) - Testing & Code Review
6. **Super-AI-UltraThink-Agent** (Opus 4.1) - Emergency Help

### Message Bus Structure
```
.claude-bus/
├── planning/      # Requirements input
├── tasks/         # Work assignments
├── contracts/     # API specifications
├── code/          # Development sandbox
├── reviews/       # QA results
├── git/           # Version control
└── events.jsonl   # Activity log
```

### Code Quality Standards
- **Max Lines**: 400 per file
- **Max Nesting**: 3 levels deep
- **Min Comments**: 20% coverage
- **Max Function**: 50 lines

### Workflow Phases (Repeat per Stage)
1. **Planning** → Tasks & Contracts
2. **Development** → Code in sandbox
3. **Review** → Quality checks
4. **Git** → Approved commits only
5. **Integration** → Testing & metrics

### Project Stages
- **Stage 1**: Foundation (upload, parse, store)
- **Stage 2**: RAG Core (retrieve, generate, cite)
- **Stage 3**: Standards (IEC 62443, ETSI EN 303 645)
- **Stage 4**: Intelligence (knowledge graphs)
- **Stage 5**: Production (UI, audit, performance)
- **Stage 6**: Advanced (multi-user, fine-tuning)

## Quick Commands

Check current tasks:
```bash
ls .claude-bus/tasks/*.json
```

View recent activity:
```bash
tail -20 .claude-bus/events.jsonl
```

Monitor message bus:
```powershell
.\monitor.ps1
```

## How to Start Working

1. Check agent assignment: @.claude-bus/agents/current-agent.txt
2. Review all docs: @todo/*.html @todo/*.md
3. Check active tasks: @.claude-bus/tasks/*.json
4. Write code to: `.claude-bus/code/`
5. Update task status when done
6. Log actions to: `events.jsonl`

## Project Overview

**GPT-OSS** is a local AI knowledge assistant system built with LightRAG for cybersecurity, product testing, and risk assessment. The system combines:
- Local LLM (gpt-oss-20b via llama.cpp)
- Knowledge graph RAG (LightRAG architecture)
- Vector search (ChromaDB)
- Graph database (Neo4j)
- Persistent chat sessions (SQLite/PostgreSQL)

**Core Value**: Privacy-first local deployment with knowledge graph-enhanced RAG for analyzing IEC 62443, ETSI EN 303 645, EN 18031, and other security standards.

## Architecture

### Multi-Database Strategy
The system uses **specialized databases** for different data types:

1. **SQLite** (structured data) → upgradeable to PostgreSQL
   - Projects, chat messages, document metadata, users
   - Location: `./data/gpt_oss.db`

2. **Neo4j** (knowledge graph)
   - Entity relationships across documents
   - Ports: 7474 (HTTP), 7687 (Bolt)
   - Credentials: neo4j/password123

3. **ChromaDB** (vector embeddings)
   - Semantic search and similarity matching
   - Port: 8001

4. **File System** (binary files only)
   - Original uploaded documents
   - Location: `./uploads/`

### Backend Stack
- **FastAPI** - REST API + WebSocket support
- **SQLAlchemy** - ORM for structured data
- **LightRAG** - Knowledge graph + vector RAG
- **llama.cpp** - Local LLM inference (GPU accelerated)

### Frontend Stack (Planned)
- **Svelte + SvelteKit** - Reactive UI framework
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **WebSocket** - Real-time chat
- **D3.js** - Knowledge graph visualization
- **Marked + Prism.js** - Markdown rendering with syntax highlighting

## Project Structure

```
D:\gpt-oss\
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration management
│   │   ├── models/
│   │   │   └── database.py      # SQLAlchemy models
│   │   ├── services/
│   │   │   ├── llm_service.py        # LLM integration
│   │   │   ├── lightrag_service.py   # RAG orchestration
│   │   │   └── project_manager.py    # Project CRUD
│   │   └── api/
│   │       ├── chat.py          # Chat endpoints (SSE/WebSocket)
│   │       ├── documents.py     # Document upload/parsing
│   │       └── projects.py      # Project management
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── routes/              # SvelteKit routes
│   │   │   ├── +page.svelte           # Project list
│   │   │   └── project/[id]/
│   │   │       ├── +page.svelte       # Chat interface
│   │   │       ├── docs/+page.svelte  # Document manager
│   │   │       └── graph/+page.svelte # Knowledge graph viz
│   │   └── lib/
│   │       ├── components/      # Reusable Svelte components
│   │       ├── stores/          # Svelte stores (state)
│   │       └── ws/              # WebSocket client
│   ├── package.json
│   ├── svelte.config.js
│   ├── tailwind.config.js
│   └── vite.config.ts
├── data/                        # SQLite database directory
├── uploads/                     # Uploaded documents
├── rag_data/                    # LightRAG working directory
├── docker-compose.yml
└── bak/                         # Planning documents
    ├── goal.md                  # Product vision
    └── CHATROOM_SUMMARY.md      # Architecture decisions
```

## Development Commands

### Starting Services
```bash
# Start all services (LLM + Neo4j + ChromaDB + Backend)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Frontend development (when implemented)
cd frontend
npm install
npm run dev  # Runs on http://localhost:3000
```

### Testing
```bash
# Health check (when implemented)
python health_check.py

# Integration tests (when implemented)
python test_integration.py

# Backend API docs
# Visit http://localhost:8000/docs
```

## Key Service Endpoints

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000 (Svelte dev server)
- **Neo4j Browser**: http://localhost:7474
- **ChromaDB**: http://localhost:8001
- **LLM Service**: http://localhost:8080

## API Design

### REST Endpoints
```
POST   /api/projects/create
GET    /api/projects/{id}
GET    /api/projects/{id}/stats
POST   /api/documents/upload
GET    /api/documents/{id}
POST   /api/chat/chat              # Supports SSE streaming
GET    /api/projects/{id}/knowledge-graph
```

### WebSocket (Planned)
```
/ws/chat/{project_id}         # Real-time chat
/ws/notifications             # System notifications
```

## Document Processing Pipeline

1. **Upload** → Validate format (PDF, Excel, Word, TXT, Markdown, images)
2. **Parse** → Extract text (including OCR for scanned PDFs)
3. **Chunk** → Split into semantic units
4. **Embed** → Generate vectors (ChromaDB)
5. **Graph** → Build knowledge graph (Neo4j via LightRAG)
6. **Index** → Store metadata (SQLite/PostgreSQL)

Supported formats:
- PDF (including scanned documents with OCR)
- Microsoft Word (.docx)
- Microsoft Excel (.xlsx)
- Plain text (.txt)
- Markdown (.md)
- Images (OCR extraction)

## LightRAG Query Capabilities

The system should support:
- **Standard clause lookup**: "Find IEC 62443-4-2 CR 2.11"
- **Cross-standard comparison**: Compare requirements across IEC 62443, EN 303 645, EN 18031
- **Evidence matching**: Find supporting evidence for answers
- **Compliance checking**: Verify if answers meet requirements
- **Gap analysis**: Identify missing evidence or non-compliance

**Critical constraint**: If data is insufficient, the system MUST respond with "I cannot answer this question because the data is incomplete."

## Hardware Configuration

The system is designed for:
- **Primary GPU**: RTX 5090 eGPU (32GB VRAM) - main LLM inference
- **Secondary GPU**: RTX 4070 (8GB VRAM) - auxiliary tasks
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 50GB minimum

GPU selection in docker-compose.yml:
```yaml
environment:
  NVIDIA_VISIBLE_DEVICES: "GPU-3143337d-5132-41c1-9381-33b56ef28990"
```

If memory constrained, edit llama service command:
```yaml
command:
  - -ngl 50      # Reduce GPU layers
  - -c 32768     # Reduce context length
```

## Database Migration Path

**Phase 1** (Current): SQLite for simplicity
- Single-user or small team
- No setup required, auto-created on first run
- Easy backup (single file)

**Phase 2** (Future): PostgreSQL for production
- Multi-user support
- Better concurrency
- Uncomment postgres service in docker-compose.yml
- Update DATABASE_URL in backend config
- Run migration scripts (to be implemented)

Migration is intentionally easy - SQLAlchemy models work with both.

## Frontend Implementation Guidelines

When building Svelte components:

1. **Use TypeScript** for all new code
2. **WebSocket-first** for real-time chat, fallback to SSE
3. **Markdown rendering** with syntax highlighting (Prism.js/Shiki)
4. **Responsive design** - Mobile-first with TailwindCSS
5. **Knowledge graph visualization** - D3.js for interactive graphs
6. **Drag-and-drop** file uploads
7. **Svelte stores** for state management (avoid prop drilling)

Example WebSocket store pattern:
```typescript
// lib/stores/chat.ts
import { writable } from 'svelte/store';

export const messages = writable([]);
export const ws = writable<WebSocket | null>(null);
```

## Configuration Files

### Backend (.env or docker-compose environment)
```bash
LLM_API_URL=http://llama:8080
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password123
DATABASE_URL=sqlite:///./data/gpt_oss.db  # or postgresql://...
VECTOR_DB_TYPE=chroma
CHROMA_HOST=chroma
CHROMA_PORT=8001
```

### Frontend (to be created)
```typescript
// src/lib/config.ts
export const API_URL = 'http://localhost:8000';
export const WS_URL = 'ws://localhost:8000';
```

## Design Principles

1. **KISS (Keep It Simple, Stupid)** - Use the right tool for each job
2. **Privacy-first** - All processing happens locally
3. **Transparency** - Every answer must cite sources with page numbers and highlights
4. **Separation of concerns** - Structured data (SQLite), vectors (ChromaDB), graphs (Neo4j)
5. **Progressive enhancement** - Start simple (SQLite), upgrade when needed (PostgreSQL)
6. **Svelte over React** - Lighter, faster, better for real-time applications

## Important Notes

- **First startup**: Docker image downloads take 10-20 minutes
- **Data storage**: ALL structured data is in SQLite, NOT the file system
- **Source transparency**: All AI responses must include PDF highlights showing exact locations
- **No hallucination**: System must refuse to answer when data is insufficient
- **Upgrade path**: SQLite → PostgreSQL migration is straightforward with SQLAlchemy
- **Frontend choice**: Svelte (not React) for performance and simplicity
