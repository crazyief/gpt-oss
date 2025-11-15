# 📡 Message Bus Protocol Documentation

**Auto-Loaded**: Yes (via @todo/*.md in CLAUDE.md)
**Critical**: This file defines how all agents communicate

---

## 🎯 What is the Message Bus?

The **Message Bus** is a file-based communication system at `.claude-bus/` that enables multiple Claude sessions (acting as different agents) to collaborate asynchronously through structured JSON files.

Think of it as: **Email system but using files instead of network**

---

## 📁 Message Bus Structure

```
.claude-bus/
├── planning/          # INPUT: Requirements from users
├── tasks/             # WORK: Assigned work items
├── contracts/         # SPEC: API/interface definitions
├── dependencies/      # DEPS: Task dependencies
├── code/              # OUTPUT: Actual code files
├── config/            # SETTINGS: Shared configurations
├── ready/             # SIGNALS: Service readiness
├── reviews/           # QA: Code review results
├── test-results/      # TESTS: Test outcomes
├── metrics/           # PERF: Performance data
├── errors/            # ISSUES: Error reports
├── checkpoints/       # SAVES: Progress snapshots
├── audit/             # LOGS: Audit trail schemas
├── help/              # SOS: Blocking issues
├── git/               # VCS: Version control ops
├── archive/           # HISTORY: Completed stages
├── agents/            # CONFIG: Agent definitions
│   ├── PM_AGENT.md
│   ├── AGENT_PROMPTS.md
│   └── current-agent.txt
└── events.jsonl       # TIMELINE: Append-only log
```

---

## 🔄 How It Works

### 1. **Asynchronous Communication**
- Agents don't talk directly
- They read and write files
- Changes are detected by monitoring

### 2. **File-Based Messages**
Each message is a JSON file with:
- Unique ID (Stage1-task-001)
- Timestamp
- Status
- Assignee
- Content

### 3. **Status Flow**
```
pending → in_progress → completed
                    ↓
                  blocked (if issues)
```

---

## 📝 Message Formats

### Task Message (tasks/Stage1-task-001.json)
```json
{
  "id": "Stage1-task-001",
  "stage": 1,
  "type": "development",
  "title": "Create upload API",
  "assignee": "Backend-Agent",
  "status": "pending",
  "priority": "high",
  "created_at": "2024-11-15T10:00:00Z",
  "updated_at": "2024-11-15T10:00:00Z",
  "description": "Implement file upload endpoint",
  "acceptance_criteria": [
    "Handle PDF/Word/Excel",
    "Max 100MB files",
    "Return document_id"
  ],
  "dependencies": ["Stage1-task-000"],
  "output": {
    "files": [".claude-bus/code/Stage1-backend/upload.py"],
    "ready_signal": ".claude-bus/ready/upload-api.json"
  }
}
```

### Contract Message (contracts/Stage1-api-001.json)
```json
{
  "id": "Stage1-api-001",
  "stage": 1,
  "endpoint": "/api/upload",
  "method": "POST",
  "request": {
    "headers": {
      "Content-Type": "multipart/form-data"
    },
    "body": {
      "file": "binary",
      "metadata": {
        "title": "string",
        "tags": ["string"]
      }
    }
  },
  "response": {
    "success": {
      "status": 200,
      "body": {
        "document_id": "string",
        "status": "success"
      }
    },
    "error": {
      "status": 400,
      "body": {
        "error": "string"
      }
    }
  }
}
```

### Help Request (help/Stage1-help-001.json)
```json
{
  "id": "Stage1-help-001",
  "from": "Backend-Agent",
  "task_id": "Stage1-task-001",
  "urgency": "high",
  "problem": "Cannot parse encrypted PDFs",
  "attempted_solutions": [
    "Tried PyPDF2 - failed",
    "Tried pdfplumber - failed"
  ],
  "need_help_from": "Super-AI-UltraThink-Agent"
}
```

### Event Log Entry (events.jsonl)
```json
{"timestamp": "2024-11-15T10:00:00Z", "agent": "PM-Architect", "action": "task_created", "details": {"task_id": "Stage1-task-001"}}
{"timestamp": "2024-11-15T10:01:00Z", "agent": "Backend-Agent", "action": "task_started", "details": {"task_id": "Stage1-task-001"}}
{"timestamp": "2024-11-15T10:30:00Z", "agent": "Backend-Agent", "action": "code_created", "details": {"file": "upload.py", "lines": 234}}
```

---

## 🤖 Agent Behaviors

### Reading Messages
```python
# Agent checks for assigned tasks
tasks = read_json_files(".claude-bus/tasks/Stage1-*.json")
my_tasks = [t for t in tasks if t["assignee"] == "Backend-Agent"]
```

### Writing Messages
```python
# Agent updates task status
task["status"] = "in_progress"
task["updated_at"] = datetime.now()
write_json(".claude-bus/tasks/Stage1-task-001.json", task)
```

### Logging Events
```python
# Append to event log (NEVER overwrite)
event = {
    "timestamp": datetime.now(),
    "agent": "Backend-Agent",
    "action": "task_started",
    "details": {"task_id": "Stage1-task-001"}
}
append_jsonl(".claude-bus/events.jsonl", event)
```

---

## 🔄 Workflow Through Message Bus

### 1. Planning → Tasks
```
PM-Architect reads:  planning/Stage1-req-001.json
PM-Architect writes: tasks/Stage1-task-*.json
```

### 2. Tasks → Code
```
Backend-Agent reads:  tasks/Stage1-task-001.json
Backend-Agent writes: code/Stage1-backend/upload.py
Backend-Agent updates: tasks/Stage1-task-001.json (status: completed)
```

### 3. Code → Review
```
QA-Agent reads:  code/Stage1-backend/*.py
QA-Agent writes: reviews/Stage1-review-001.json
```

### 4. Review → Git
```
QA-Agent reads:  reviews/Stage1-review-001.json (approved)
QA-Agent executes: git add && git commit
QA-Agent writes: git/Stage1-commit-001.json
```

---

## 📋 Rules & Conventions

### File Operations
1. **READ**: Any agent can read any file
2. **WRITE**: Only write to your designated areas
3. **APPEND**: Only append to events.jsonl
4. **DELETE**: Never delete, move to archive/

### Status Updates
1. Always update `updated_at` timestamp
2. Only assignee can change status to `in_progress`
3. Only assignee can change to `completed`
4. Anyone can change to `blocked`

### Naming Rules
1. Use Stage prefix: `Stage1-task-001.json`
2. Sequential numbering: 001, 002, 003
3. Type indicators: task, api, dep, review, test
4. No spaces in filenames

### Concurrency
1. Assume multiple agents work simultaneously
2. Don't modify files being processed by others
3. Use status field to claim ownership
4. Create new files rather than modifying when possible

---

## 🚀 Quick Start for New Claude Session

### Step 1: Identify Your Role
```bash
cat .claude-bus/agents/current-agent.txt
```

### Step 2: Find Your Work
```bash
# Find tasks assigned to you
grep -l "Backend-Agent" .claude-bus/tasks/Stage1-*.json

# Check task status
cat .claude-bus/tasks/Stage1-task-001.json | grep status
```

### Step 3: Claim Your Task
```json
// Update status to in_progress
{
  "status": "in_progress",
  "updated_at": "2024-11-15T10:00:00Z"
}
```

### Step 4: Do The Work
```bash
# Write code to designated area
echo "code" > .claude-bus/code/Stage1-backend/upload.py
```

### Step 5: Complete Task
```json
// Update status to completed
{
  "status": "completed",
  "output": {
    "files": ["Stage1-backend/upload.py"]
  }
}
```

### Step 6: Log Activity
```bash
echo '{"timestamp":"2024-11-15T10:00:00Z","agent":"Backend-Agent","action":"task_completed","details":{"task_id":"Stage1-task-001"}}' >> .claude-bus/events.jsonl
```

---

## 🔍 Monitoring the Bus

### PowerShell Monitor
```powershell
.\monitor.ps1  # Real-time status display
```

### Manual Checks
```bash
# Recent events
tail -20 .claude-bus/events.jsonl

# Pending tasks
grep -l "pending" .claude-bus/tasks/*.json

# Blocked items
grep -l "blocked" .claude-bus/tasks/*.json

# Help requests
ls .claude-bus/help/*.json
```

---

## ⚠️ Common Pitfalls

1. **Don't Overwrite events.jsonl** - Always append
2. **Don't Modify Others' In-Progress Tasks** - Respect ownership
3. **Don't Skip Logging** - Every action should be logged
4. **Don't Use Wrong Stage Prefix** - Check current stage first
5. **Don't Forget Dependencies** - Check before starting

---

## 🔧 Troubleshooting

### Task Stuck?
1. Check dependencies
2. Look for help requests
3. Review error logs
4. Escalate to Super-AI-UltraThink

### Can't Find Files?
1. Check stage prefix
2. Verify directory structure
3. Check archive/ folder
4. Review events.jsonl

### Conflicts?
1. Check who owns task (status: in_progress)
2. Coordinate through help requests
3. PM-Architect resolves conflicts

---

## 📚 Reference

### Key Files
- Task Format: `.claude-bus/TASK_FORMAT.md`
- Agent Configs: `.claude-bus/agents/*.md`
- Current Status: `todo/PROJECT_STATUS.md`
- Stage Definitions: `todo/STAGE_DEFINITIONS.md`

### Commands Reference
```bash
# Count tasks
ls .claude-bus/tasks/*.json | wc -l

# Find by assignee
grep -l "Backend-Agent" .claude-bus/tasks/*.json

# Check recent activity
tail -f .claude-bus/events.jsonl

# Archive completed stage
mv .claude-bus/tasks/Stage1-*.json .claude-bus/archive/Stage1/
```

---

*This protocol ensures consistent communication between all agents across all Claude sessions.*