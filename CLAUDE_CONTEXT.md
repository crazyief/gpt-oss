# CLAUDE_CONTEXT.md - Session Bootstrap File

## 🚀 Quick Start for New Claude Sessions

**IMPORTANT**: Read this file first when starting any new Claude session for the GPT-OSS project.

## Project Overview
You are working on the **Local AI Knowledge Assistant** project - a LightRAG-based system for processing cybersecurity documents (IEC 62443, ETSI EN 303 645, EN 18031) with full audit trails and source transparency.

## Your Role
Check `.claude-bus/agents/current-agent.txt` to see which agent you should act as. If not specified, ask the user.

## Key Files to Load

### 1. Workflow Definition
```
D:\gpt-oss\todo\workflow-v2.html     # Complete workflow with I/O specs
D:\gpt-oss\todo\agent-roles.html     # Agent R&R definitions
```

### 2. Agent Configurations
```
D:\gpt-oss\.claude-bus\agents\PM_AGENT.md       # PM-Architect config
D:\gpt-oss\.claude-bus\agents\AGENT_PROMPTS.md  # All agent prompts
```

### 3. Current State
```
D:\gpt-oss\.claude-bus\tasks\*.json        # Current tasks
D:\gpt-oss\.claude-bus\events.jsonl        # Recent activity
D:\gpt-oss\.claude-bus\planning\*.json     # Active requirements
```

## Message Bus Structure
```
.claude-bus/
├── planning/        # Requirements (INPUT for PM-Architect)
├── tasks/          # Work items (OUTPUT from PM, INPUT for devs)
├── contracts/      # API specs (OUTPUT from PM, INPUT for devs)
├── code/           # Development (OUTPUT from devs, INPUT for QA)
├── reviews/        # Quality checks (OUTPUT from QA)
├── git/            # Version control (TRIGGER from QA)
└── events.jsonl    # Activity log (APPEND ONLY)
```

## Workflow Phases

### Phase 1: Planning
- **Input**: User requirements in `planning/req-XXX.json`
- **Output**: Tasks in `tasks/task-XXX.json`
- **Agent**: PM-Architect-Agent

### Phase 2: Development
- **Input**: Tasks and contracts
- **Output**: Code in `code/*/`
- **Agents**: Backend, Frontend, Document-RAG

### Phase 3: Review
- **Input**: Code from `code/*/`
- **Output**: Reviews in `reviews/review-XXX.json`
- **Agent**: QA-Agent

### Phase 4: Git
- **Input**: Approved code
- **Output**: Git commits
- **Agent**: QA-Agent (triggers), PM-Architect (tags)

### Phase 5: Integration
- **Input**: Complete system
- **Output**: Test results and metrics
- **Agent**: QA-Agent + All

## Code Quality Standards
```python
MAX_FILE_LINES = 400
MAX_NESTING_DEPTH = 3
MIN_COMMENT_RATIO = 0.2
MAX_FUNCTION_LINES = 50
```

## Agent Quick Reference

| Agent | Model | Primary Role | Key Outputs |
|-------|-------|--------------|-------------|
| PM-Architect | Opus | Planning & Architecture | Tasks, Contracts |
| Document-RAG | Sonnet | RAG Pipeline | Chunking, Embeddings |
| Backend | Sonnet | API Server | FastAPI, Database |
| Frontend | Sonnet | UI | Gradio/Svelte |
| QA | Sonnet | Quality | Reviews, Tests |
| Super-AI-UltraThink | Opus 4.1 | Emergency Help | Solutions |

## How to Start

1. **Identify your role**: Check which agent you should be
2. **Check pending work**: Look in `.claude-bus/tasks/` for your assignments
3. **Review standards**: Ensure code follows quality rules
4. **Update status**: Mark tasks as in-progress when starting
5. **Log actions**: Append to `events.jsonl`
6. **Request help**: Create files in `help/` if blocked

## Example First Commands
```bash
# See current tasks
ls .claude-bus/tasks/*.json

# Check recent activity
tail -n 20 .claude-bus/events.jsonl

# Find your assignments (replace Backend with your agent)
grep -l "Backend" .claude-bus/tasks/*.json
```

## Critical Rules
1. **Never commit directly** - QA-Agent handles git after approval
2. **Always log actions** - Append to events.jsonl
3. **Follow standards** - Max 400 lines, nesting < 3
4. **Update task status** - pending → in_progress → completed
5. **Request help when blocked** - Use Super-AI-UltraThink

## Need Help?
- **Blocked on task**: Create `.claude-bus/help/request-XXX.json`
- **Architecture question**: Ask PM-Architect-Agent
- **Complex problem**: Invoke Super-AI-UltraThink-Agent

---
*Last Updated: 2024-11-15*
*Project Location: D:\gpt-oss*
*Status: Bootstrap Phase*