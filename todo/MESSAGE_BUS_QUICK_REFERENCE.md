# 🚀 Message Bus Quick Reference Card

## Essential Commands - Copy & Use

### 1️⃣ Start Your Session
```bash
# Who am I?
cat .claude-bus/agents/current-agent.txt

# What's my work?
grep -l "Backend-Agent" .claude-bus/tasks/Stage1-*.json

# What's happening?
tail -10 .claude-bus/events.jsonl
```

### 2️⃣ Claim a Task
```bash
# Read task
cat .claude-bus/tasks/Stage1-task-001.json

# Edit to set status: "in_progress"
# Update: updated_at with current timestamp
```

### 3️⃣ Write Your Code
```bash
# Create code in your area
.claude-bus/code/Stage1-backend/your-file.py
.claude-bus/code/Stage1-frontend/your-file.html
.claude-bus/code/Stage1-rag/your-file.py
```

### 4️⃣ Complete Task
```bash
# Update task file:
# - status: "completed"
# - output.files: ["your-file.py"]
# - updated_at: current timestamp
```

### 5️⃣ Log Everything
```bash
# Append to events (NEVER overwrite)
echo '{"timestamp":"2024-11-15T10:00:00Z","agent":"Your-Agent","action":"task_completed","details":{"task_id":"Stage1-task-001"}}' >> .claude-bus/events.jsonl
```

---

## File Locations Cheat Sheet

| What | Where | Format |
|------|-------|--------|
| **Your Role** | `.claude-bus/agents/current-agent.txt` | Text |
| **Your Tasks** | `.claude-bus/tasks/Stage*-task-*.json` | JSON |
| **Your Code** | `.claude-bus/code/Stage*-{agent}/` | Any |
| **Get Help** | `.claude-bus/help/Stage*-help-*.json` | JSON |
| **Log Events** | `.claude-bus/events.jsonl` | JSONL |
| **API Specs** | `.claude-bus/contracts/Stage*-api-*.json` | JSON |

---

## Status Flow
```
pending → in_progress → completed
              ↓
           blocked
```

---

## JSON Templates

### Update Task Status
```json
{
  "status": "in_progress",
  "updated_at": "2024-11-15T10:00:00Z"
}
```

### Complete Task
```json
{
  "status": "completed",
  "updated_at": "2024-11-15T12:00:00Z",
  "output": {
    "files": ["Stage1-backend/upload.py"],
    "tests": ["Stage1-backend/test_upload.py"]
  }
}
```

### Request Help
```json
{
  "id": "Stage1-help-001",
  "from": "Your-Agent",
  "task_id": "Stage1-task-001",
  "urgency": "high",
  "problem": "Describe issue",
  "need_help_from": "Super-AI-UltraThink-Agent"
}
```

### Log Event
```json
{"timestamp":"ISO8601","agent":"Your-Agent","action":"action_name","details":{}}
```

---

## Rules - NEVER Break These

1. ❌ **NEVER** overwrite `events.jsonl` - only append
2. ❌ **NEVER** modify someone else's `in_progress` task
3. ❌ **NEVER** delete files - move to `archive/`
4. ❌ **NEVER** skip logging your actions
5. ❌ **NEVER** use wrong Stage prefix

---

## Quick Monitoring

```bash
# Watch events live
tail -f .claude-bus/events.jsonl

# Count pending tasks
grep -c '"status": "pending"' .claude-bus/tasks/*.json

# Find blocked tasks
grep -l '"status": "blocked"' .claude-bus/tasks/*.json

# Check help requests
ls .claude-bus/help/*.json 2>/dev/null

# Run monitor
powershell .\monitor.ps1
```

---

## When Stuck

1. **Can't find task?** → Check stage prefix
2. **Task blocked?** → Create help request
3. **Dependency not ready?** → Check ready/ folder
4. **Need complex help?** → Call Super-AI-UltraThink
5. **Conflict?** → PM-Architect decides

---

## Stage Prefix Format
```
Stage1-task-001.json     ✅
Stage2-api-003.json      ✅
task-001.json           ❌ (missing stage)
S1-task-001.json        ❌ (wrong format)
```

---

*Print this card for quick reference during development!*