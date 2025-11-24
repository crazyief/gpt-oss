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

### 🤖 Automatic Agent Invocation (Workflow Automation)

**Main Session Role**: You ARE the **PM-Architect-Agent** throughout the entire project lifecycle (all phases, all stages). This ensures continuous context and project oversight.

**When to Auto-Invoke Other Agents**:

At the start of each phase, automatically:
1. **Read the phase checklist**: `.claude-bus/planning/stages/stage{N}/phase{N}-*-checklist.json`
2. **Check the `assigned_to` field**: Lists all agents responsible for this phase
3. **Invoke co-agents automatically**: If other agents are listed (besides PM-Architect-Agent), invoke them via Task tool
4. **DO NOT wait for user request**: This is automatic workflow orchestration

**Phase-Specific Automation Patterns**:

**Planning Phase** (assigned_to: ["PM-Architect-Agent", "Super-AI-UltraThink"]):
- **Step 1**: PM-Architect (you) creates initial requirements and planning artifacts (outputs o1-o6)
- **Step 2**: **MANDATORY - Automatically invoke Super-AI-UltraThink** to review ALL planning outputs
- **Step 3**: Super-AI validates: task decomposition, API contracts, dependencies, architecture, standards, test scenarios
- **Step 4**: Incorporate Super-AI feedback - revise outputs if needed
- **Step 5**: Mark Phase 1 as completed ONLY after Super-AI approval
- **CRITICAL**: Do NOT transition to Phase 2 until Super-AI review is complete and outputs are approved

**Development Phase** (assigned_to: ["Backend-Agent", "Frontend-Agent", "Document-RAG-Agent", etc.]):
- PM-Architect (you) coordinates the development work
- **Automatically invoke ALL development agents IN PARALLEL** using a single message with multiple Task tool calls
- Monitor their progress and integrate their outputs
- Each agent works independently on their tasks

**Review Phase** (assigned_to: ["QA-Agent", "PM-Architect-Agent"]):
- **Automatically invoke QA-Agent** with git diff scope from Phase 2 checkpoint
- PM-Architect reviews QA results and makes approval decisions
- If issues found: agents fix, create new git checkpoint, QA re-reviews

**Integration Testing Phase** (assigned_to: ["QA-Agent", "All Agents"]):
- **Automatically invoke QA-Agent** for automated test execution
- Run integration tests, performance benchmarks, end-to-end scenarios
- Invoke other agents as needed for debugging failures

**Manual Approval Phase** (assigned_to: ["PM-Architect-Agent", "User"]):
- PM-Architect deploys application locally for user testing
- User manually tests all features against acceptance criteria
- User provides explicit approval OR documents bugs/changes needed
- If approved: Create final git checkpoint, generate completion certificate
- If rejected: Return to Phase 2 with user feedback

**Critical Rules**:
- Always read the phase checklist FIRST before starting phase work
- Invoke agents based on `assigned_to` field, not assumptions
- Use PARALLEL invocation for Development Phase (single message, multiple Task calls)
- Maintain continuous PM-Architect context - never hand off full control
- Log all agent invocations to `.claude-bus/events.jsonl`

### 🔖 Git Checkpoint Protocol (MANDATORY)

**Purpose**: Create clear audit trail and enable focused code reviews by marking completion milestones.

**PM-Architect-Agent responsibilities**:

**When to Create Git Checkpoints** (automatic, don't wait for user request):
1. **After Phase 2 (Development) completes** - Commit all new code BEFORE invoking QA-Agent
2. **After Phase 3 (QA Review) approval** - Commit all fixes, ready for integration testing
3. **After Phase 5 (Integration Testing) passes** - Final checkpoint before production
4. **Before major refactoring** - Safety net for rollback if needed

**Checkpoint Commit Message Format**:
```
Stage {N} Phase {P} Complete: {brief description}

Files changed: {count}
- Backend: {list of key new/modified files}
- Frontend: {list of key new/modified files}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Example**:
```
Stage 1 Phase 2 Complete: Backend CRUD/SSE APIs + Frontend Chat Interface

Files changed: 40
- Backend: API endpoints (projects, conversations, chat, messages), Services (LLM, stream manager), Tests (140+ test methods)
- Frontend: Sidebar (6 components), Chat Interface (6 components), SSE client, Markdown renderer

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**QA-Agent Review Scope Protocol**:

When invoking QA-Agent, PM-Architect MUST:
1. **Create git checkpoint FIRST** (if not already done after Phase 2)
2. **Get previous checkpoint hash**: Use `git log --oneline` to find last checkpoint
3. **Provide QA-Agent with git diff scope**:
   ```
   Review scope: All files changed since commit <hash>

   Use this command to see what's new:
   git diff <previous-checkpoint-hash> --name-only

   OR for detailed diff:
   git diff <previous-checkpoint-hash>

   Focus your review ONLY on these changed files. Do NOT review files unchanged since last approved checkpoint.
   ```

**Benefits**:
- ✅ QA reviews only new code (efficient, focused, prevents re-reviewing approved code)
- ✅ Clear audit trail of what changed when (compliance requirement for IEC 62443)
- ✅ Easy rollback if critical issues found
- ✅ Prevents wasted effort reviewing already-approved code
- ✅ Git history shows which agent/phase created each change

**Phase Transition Gate Enforcement**:

Before transitioning Phase 2 → Phase 3:
- ✅ Git checkpoint MUST exist
- ✅ If no checkpoint: BLOCK transition and alert user

**Automated Monitoring Rule** (added to `.claude-bus/config/auto-monitoring.json`):
```json
{
  "rule_id": "git-checkpoint-phase2",
  "severity": "critical",
  "condition": "Phase 2 complete AND no git checkpoint",
  "action": "BLOCK phase transition, create user alert"
}
```

### Message Bus Structure
```
.claude-bus/
├── planning/        # Requirements input
├── tasks/           # Work assignments
├── contracts/       # API specifications
├── code/            # Development sandbox
├── reviews/         # QA results
├── git/             # Version control
├── notifications/   # AUTOMATED USER ALERTS
├── monitoring/      # Service health logs
├── tech-debt/       # Technical debt tracking
└── events.jsonl     # Activity log
```

### 🔔 Automated Monitoring & Alerting (CRITICAL)

**All agents MUST perform automated checks according to `.claude-bus/config/auto-monitoring.json`**

**PM-Architect-Agent responsibilities**:
1. **Before EVERY phase transition**: Run automated gate checks
2. **Check service health**: Before Phase 2, verify all services up
3. **Check for user notifications**: After each phase, review `.claude-bus/notifications/user-alerts.jsonl`
4. **Create critical alerts**: When blockers detected, auto-create notification
5. **Update PROJECT_STATUS.md**: Add critical alerts to 🔔 Important Notes section

**QA-Agent responsibilities**:
1. **During Phase 3 Review**: Auto-detect tech debt using rules in auto-monitoring.json
2. **Create tech debt files**: Automatically for detected issues
3. **Security check**: Auto-flag security vulnerabilities (creates CRITICAL alert)
4. **Performance check**: Auto-compare metrics vs baselines (creates alert if fails)

**All Agents**:
- **If service fails**: Create notification in `.claude-bus/notifications/user-alerts.jsonl`
- **If blocked > 4 hours**: Auto-escalate to user notification
- **If critical issue**: MUST notify user immediately via alert

**User Notification Format**:
```json
{
  "id": "notify-{N}",
  "severity": "critical",
  "message": "🔴 CRITICAL: {description}",
  "suggested_actions": ["action1", "action2"]
}
```

**How to Create AND Display Alert**:
```bash
# 1. Write to file (for logging)
echo '{"id":"notify-001","timestamp":"2025-11-17T14:00:00","severity":"critical","notification_type":"blocker_alert","message":"🔴 CRITICAL: Phase 2 blocked for 5 hours","status":"active"}' >> .claude-bus/notifications/user-alerts.jsonl

# 2. MUST ALSO output text message to user (DO NOT skip this!)
```

**CRITICAL: In-Session Notification Protocol**

**ALL AGENTS MUST**:
1. **Write alert to file** (for history/logging)
2. **Output warning message directly to user** (visible in chat)
3. **Display suggested actions** in user-facing text
4. **Block phase transition** if severity is critical

**Example - PM-Architect detects service down**:
```
PM-Architect: I've detected a critical issue that requires your attention:

🔴 CRITICAL: llama.cpp service failed to restart after 3 attempts

**What happened**:
- Service health check failed at 14:20, 14:22, and 14:25
- Auto-restart attempts all failed
- Phase 2 Development is now BLOCKED

**Suggested actions**:
1. Check docker logs: docker-compose logs llama
2. Check GPU status: nvidia-smi
3. Restart manually: docker-compose restart llama
4. Verify model file exists and is accessible

**Status**: Phase 2 cannot proceed until this is resolved.
Alert logged to: .claude-bus/notifications/user-alerts.jsonl (notify-001)

Would you like me to help troubleshoot this issue?
```

**Phase Transition Protocol**:

Before EVERY phase transition, PM-Architect MUST:
1. Check for active alerts in user-alerts.jsonl
2. If any CRITICAL alerts → **DISPLAY BLOCKING MESSAGE**:
   ```
   ⚠️ CANNOT PROCEED TO PHASE {N+1}

   Active Critical Issues (2):
   - 🔴 llama.cpp service down (notify-001)
   - 🔴 Security: SQL injection in chat.py (notify-003)

   Please resolve these issues before continuing.
   ```
3. If any HIGH alerts → **DISPLAY WARNING (can proceed with confirmation)**:
   ```
   ⚠️ WARNING: High-priority issues detected

   Active Warnings (1):
   - ⚠️ Phase 3 blocked for 4 hours (notify-002)

   You can proceed, but these issues should be addressed soon.
   Proceed to Phase {N+1}? (y/n)
   ```
4. If MEDIUM/LOW alerts → **DISPLAY INFO ONLY**:
   ```
   📘 FYI: {N} medium/low priority issues detected
   Check .claude-bus/notifications/user-alerts.jsonl for details

   Proceeding to Phase {N+1}...
   ```

### Code Quality Standards
- **Max Lines**: 400 per file
- **Max Nesting**: 3 levels deep
- **Min Comments**: 20% coverage
- **Max Function**: 50 lines

### Testing Standards (MANDATORY)

**All stages MUST follow the MCP-Enhanced Hybrid Testing Approach.**

**Documentation**:
- **Developer Guide**: @docs/TESTING-STANDARDS.md (comprehensive testing guidelines)
- **Agent Rules**: @.claude-bus/standards/TESTING-RULES.md (enforcement rules)

**Testing Pyramid** (ALL stages):
```
Unit Tests:        60% (Vitest)
Integration Tests: 20% (Vitest + MSW)
Component Tests:   10% (Playwright MCP)
E2E Tests:         10% (Playwright MCP)
Visual Regression: 3-5 critical UI states (Chrome DevTools MCP)
Performance Tests: 2-3 key journeys (Chrome DevTools MCP)
```

**Coverage Thresholds** (enforced gates):
All stages require **≥ 70% coverage** (consistent quality standard).

| Stage | Coverage | Tests | Key Features |
|-------|----------|-------|--------------|
| Stage 1 | 70% | 188 | Foundation (projects, chat) |
| Stage 2 | 70% | 280 | RAG Core (retrieval, citations) |
| Stage 3 | 70% | 380 | Standards (IEC 62443, ETSI) |
| Stage 4 | 70% | 480 | Intelligence (knowledge graphs) |
| Stage 5 | 70% | 580 | Production (audit, performance) |
| Stage 6 | 70% | 680 | Advanced (multi-user, deployment) |

**Tool Selection Rules**:
- **Vitest**: Pure logic, utilities, business rules, API clients (with MSW)
- **Playwright MCP**: Component interactions, user workflows, WebSocket/SSE
- **Chrome DevTools MCP**: Visual regression, Core Web Vitals, bundle size

**Quality Gates** (automatic enforcement):
- ❌ Phase 3→4: BLOCKED if coverage < 70%
- ❌ Phase 3→4: BLOCKED if test pyramid inverted
- ❌ Phase 4→5: BLOCKED if performance fails (LCP > 4.0s)
- ⚠️ Phase 3→4: WARNING if file > 400 lines

**Performance Thresholds** (Chrome DevTools):
- LCP (Largest Contentful Paint) ≤ 2.5s
- FCP (First Contentful Paint) ≤ 1.8s
- CLS (Cumulative Layout Shift) ≤ 0.1
- Bundle size (gzipped) ≤ 60 KB (Stage 1)

**QA-Agent Enforcement**:
During Phase 3 (Review), QA-Agent MUST:
1. Run all tests: `npm run test && npm run test:e2e && npm run test:visual && npm run test:performance`
2. Generate coverage report
3. Validate test pyramid compliance
4. If coverage < 70%: Create CRITICAL alert, BLOCK transition
5. If test pyramid violated: Create HIGH alert, request refactoring
6. Create comprehensive review report

**PM-Architect Responsibilities**:
During Phase 1 (Planning):
1. Define test scenarios for new features
2. Estimate test count (target 70% coverage)
3. Allocate 30% of development time for testing
4. Create test plan: `.claude-bus/planning/stages/stage{N}/test-plan.json`

**All Agents**:
- Write tests co-located with source code (`*.test.ts`, `*.integration.test.ts`)
- Add `data-testid` attributes to interactive elements
- Never commit code without tests
- Run tests before creating git checkpoint

### Workflow Phases (Repeat per Stage)
1. **Planning** → Tasks, API contracts, architecture (Super-AI review)
2. **Development** → Code in sandbox + git checkpoint
3. **Review** → QA review via git diff + fixes if needed
4. **Integration Testing** → Automated tests, service integration, performance metrics
5. **Manual Approval** → User testing, acceptance validation, final sign-off

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

**You are PM-Architect-Agent** (continuous main session):

1. **Check current phase**: Read `.claude-bus/planning/stages/stage{N}/phase{N}-*-checklist.json`
2. **Auto-invoke co-agents**: If `assigned_to` includes other agents, invoke them automatically via Task tool
3. **Review all docs**: @todo/*.html @todo/*.md
4. **Check active tasks**: @.claude-bus/tasks/*.json
5. **Coordinate work**: Development agents write to `.claude-bus/code/`, you review and coordinate
6. **Update phase status**: Mark inputs/outputs as completed in checklist JSON
7. **Log actions**: All events to `.claude-bus/events.jsonl`

**Remember**: You maintain continuous context across all phases. You are the PM who sees the project from start to finish.

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
