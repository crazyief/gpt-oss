# GPT-OSS Agent Quick Reference

## Agent Selection Guide

| Need to... | Use Agent | Model | Color |
|------------|-----------|-------|-------|
| Plan project stages, create tasks, assign work | `gpt-oss-pm-architect` | Opus | Purple |
| Build APIs, databases, backend services | `gpt-oss-backend` | Sonnet | Blue |
| Create UI components, frontend features | `gpt-oss-frontend` | Sonnet | Orange |
| Setup RAG pipeline, process documents | `gpt-oss-document-rag` | Sonnet | Green |
| Review code, write tests, ensure quality | `gpt-oss-qa` | Sonnet | Red |
| Solve complex problems, deep analysis | `super-ai-ultrathink` | Opus | Green |

## Quick Commands

### Check Current Status
```bash
# See active tasks
ls D:\gpt-oss\.claude-bus\tasks\*.json

# View recent activity
tail -20 D:\gpt-oss\.claude-bus\events.jsonl

# Check project status
cat D:\gpt-oss\todo\PROJECT_STATUS.md
```

### Switch Agent in Claude Code
1. Press `Ctrl+Shift+P` (or click agent dropdown)
2. Type agent name or select from list
3. Agent loads automatically

### Verify Setup
```powershell
.\setup-agents.ps1
```

## Message Bus Directories

| Directory | Purpose | Who Writes | Who Reads |
|-----------|---------|------------|-----------|
| `planning/` | Requirements docs | PM-Architect | All |
| `tasks/` | Work assignments | PM-Architect | Assigned agent |
| `contracts/` | API specifications | PM-Architect | Backend, Frontend |
| `code/` | Implementation | Backend, Frontend, RAG | QA |
| `reviews/` | QA results | QA | All |
| `help/` | Help requests | Any agent | PM-Architect, Super-AI |
| `events.jsonl` | Activity log | All | All |

## Task Naming Convention

Format: `Stage[N]-task-[agent]-[number].json`

Examples:
- `Stage1-task-backend-001.json`
- `Stage1-task-frontend-002.json`
- `Stage2-task-rag-001.json`

## Event Logging Format

```json
{
  "timestamp": "2024-11-15T10:30:00",
  "agent": "gpt-oss-backend",
  "event": "task_completed",
  "task_id": "Stage1-task-backend-001",
  "message": "Implemented /api/projects/create endpoint"
}
```

## Workflow Cycle

```
1. PM-Architect creates requirements → planning/
2. PM-Architect creates tasks → tasks/
3. Agents claim and work on tasks → code/
4. QA reviews completed work → reviews/
5. PM-Architect approves → git commit
6. Repeat for next stage
```

## Emergency Protocols

### Stuck on Complex Problem
1. Create help request in `help/`
2. Tag for `super-ai-ultrathink`
3. Wait for deep analysis response

### Task Blocked
1. Log blocker in `events.jsonl`
2. Create dependency in `dependencies/`
3. PM-Architect will reassign/unblock

### Quality Issue Found
1. QA creates review in `reviews/`
2. Original developer fixes
3. QA re-reviews
4. Cycle until approved

## Remember

- **Always log actions** to events.jsonl
- **Follow role boundaries** - don't do other agents' work
- **Check tasks regularly** for new assignments
- **Communicate via message bus** - never directly
- **Quality over speed** - follow standards

---

*Keep this reference handy when working with the multi-agent system!*