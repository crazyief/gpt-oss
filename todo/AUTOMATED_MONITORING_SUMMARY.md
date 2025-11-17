# Automated Monitoring & Alerting - User Guide

**Status**: ✅ FULLY AUTOMATED
**Date**: 2025-11-17
**Answer to Your Question**: YES, issues are now auto-tracked and you get auto-alerts! 🎉

---

## The Answer: YES, Fully Automated! ✅

Your question was: *"Does the new fix you provided here, will related issue get auto tracking, and raise the issue to me automatically if need?"*

**Answer**: **YES!** The workflow now has:
- ✅ **Auto-detection** of issues
- ✅ **Auto-tracking** in appropriate files
- ✅ **Auto-alerts** to you when critical
- ✅ **Auto-actions** (like service restarts)

You don't need to ask or check manually. The system will notify you proactively.

---

## What Gets Auto-Detected

### 1. Technical Debt (Auto-Detected During Code Review)

**When**: Phase 3 (Review Phase)
**Who Detects**: QA-Agent
**How It Works**:

QA-Agent **automatically scans code** for:
- ✅ Functions 200-399 lines (passes limit but complex)
- ✅ Cyclomatic complexity > 10 (hard to maintain)
- ✅ Code duplication (>10 similar lines)
- ✅ Missing docstrings on public functions
- ✅ TODO/FIXME/HACK comments
- ✅ Test coverage 20-50% (low but passes minimum)
- ✅ Magic numbers/hardcoded values

**Auto-Actions**:
1. Creates debt file: `.claude-bus/tech-debt/Stage1-debt-{N}.json`
2. If critical severity → **Creates USER ALERT**
3. Logs to `events.jsonl`

**You Get Notified When**: Critical tech debt detected

---

### 2. Service Health (Auto-Monitored Every 5 Minutes)

**When**: Phase 2-5 (During Development)
**Who Monitors**: PM-Architect-Agent (background)
**How It Works**:

System **automatically checks** every 5 minutes:
- ✅ llama.cpp (LLM Service) - http://localhost:8080
- ✅ Neo4j (Knowledge Graph) - http://localhost:7474
- ✅ ChromaDB (Vector Store) - http://localhost:8001
- ✅ Backend API (if exists) - http://localhost:8000

**Auto-Actions**:
1. If service down → **Attempts auto-restart** (up to 3 times)
2. If restart fails → **Creates USER ALERT**
3. Logs failure to `.claude-bus/monitoring/service-failures.jsonl`
4. If recovered → Logs recovery, notifies PM

**You Get Notified When**: Service fails to restart after 3 attempts

---

### 3. Blockers (Auto-Detected When Stuck)

**When**: Any phase
**Who Detects**: PM-Architect-Agent
**How It Works**:

System **automatically detects**:
- ✅ Phase blocked > 4 hours
- ✅ Task stuck in `blocked` status
- ✅ Review rejected 3 times (same task)
- ✅ Integration tests failed 5 times

**Auto-Actions**:
1. Creates blocker file: `.claude-bus/blockers/Stage1-blocker-{N}.json`
2. **Creates USER ALERT** (high severity)
3. PM-Architect evaluates resolution options

**You Get Notified When**: Critical blocker persists > 4 hours

---

### 4. Security Issues (Auto-Flagged During Review)

**When**: Phase 3 (Review Phase)
**Who Detects**: QA-Agent
**How It Works**:

QA-Agent **automatically scans** for:
- ✅ SQL injection risks
- ✅ XSS vulnerabilities
- ✅ Insecure authentication
- ✅ Missing input validation
- ✅ Hardcoded credentials
- ✅ OWASP Top 10 issues

**Auto-Actions**:
1. Review status → `rejected` (blocks progress)
2. **Creates CRITICAL USER ALERT**
3. Creates security feedback file
4. Must fix before proceeding

**You Get Notified When**: ANY security vulnerability detected (always critical)

---

### 5. Performance Issues (Auto-Checked in Phase 5)

**When**: Phase 5 (Integration Testing)
**Who Detects**: QA-Agent
**How It Works**:

System **automatically compares** actual vs baseline:
- ✅ LLM first token latency (target: < 2s)
- ✅ API response time (target: < 500ms)
- ✅ Database query performance
- ✅ UI responsiveness

**Auto-Actions**:
1. If performance < 50% of baseline → **Creates USER ALERT**
2. Creates performance feedback file
3. Returns to Phase 2 for optimization

**You Get Notified When**: Performance significantly below baseline

---

## How You Get Notified

### 🔔 PRIMARY: Direct In-Session Warnings (You WILL See These!)

**Critical/High issues are displayed directly in your Claude Code chat session.**

**Example - What you see when service fails**:
```
PM-Architect: 🔴 SERVICE HEALTH ALERT

llama.cpp service health check failed

Auto-recovery attempts: FAILED (3/3)
Status: Service is DOWN
Impact: Phase 2 Development is BLOCKED

Suggested actions:
1. Check logs: docker-compose logs llama
2. Check GPU: nvidia-smi
3. Manual restart: docker-compose restart llama

Alert logged: .claude-bus/notifications/user-alerts.jsonl (notify-001)

Should I wait while you investigate?
```

**Example - What you see at phase transition**:
```
PM-Architect: Before proceeding to Phase 3, let me check for issues...

═══════════════════════════════════════════════════════
  PHASE 2 → PHASE 3 TRANSITION GATE
═══════════════════════════════════════════════════════

✅ All code files created
✅ Unit tests passing
⚠️ WARNING: 1 high-priority issue detected

Active Warnings:
- ⚠️ Test coverage is 45% (target: 80%)

You can proceed, but this should be addressed soon.
Proceed to Phase 3? (y/n)
```

**You DON'T need to check files manually - warnings appear automatically!**

---

### 📂 SECONDARY: Alert Files (For History/Reference)

**File**: `.claude-bus/notifications/user-alerts.jsonl`

These files are for:
- Historical reference
- Automation (agents read these)
- Troubleshooting later

**Optional - Check if you want details**:
```powershell
# Last 20 alerts
tail -20 .claude-bus/notifications/user-alerts.jsonl

# Critical only
grep '"severity":"critical"' .claude-bus/notifications/user-alerts.jsonl
```

**But you don't NEED to check files - agents will tell you!**

---

### 📊 TERTIARY: Project Status File

**File**: `todo/PROJECT_STATUS.md`

Critical alerts also logged here for reference:
```markdown
## 🔔 Important Notes

### Active Alerts (2)
- 🔴 CRITICAL: llama.cpp service down (notify-001)
- ⚠️ HIGH: Phase 3 blocked for 5 hours (notify-003)
```

---

## Alert Severity Levels

| Emoji | Severity | Response Time | Blocks Progress? |
|-------|----------|---------------|------------------|
| 🔴 | **CRITICAL** | Immediate | YES - Blocks phase |
| ⚠️ | **HIGH** | Within 4 hours | NO - But escalates |
| 📘 | **MEDIUM** | Within 24 hours | NO |
| 💡 | **LOW** | When convenient | NO |

---

## Alert Types & Examples

### 🔴 CRITICAL Alerts

**service_down**
```json
{
  "message": "🔴 CRITICAL: llama.cpp failed to restart after 3 attempts. Manual intervention required.",
  "suggested_actions": [
    "Check docker logs: docker-compose logs llama",
    "Check GPU: nvidia-smi",
    "Restart: docker-compose restart llama"
  ]
}
```

**security_alert**
```json
{
  "message": "🔴 SECURITY: SQL injection risk in backend/api/chat.py:42. Must fix before proceeding.",
  "suggested_actions": [
    "Use parameterized queries",
    "Review OWASP guidelines",
    "Test with security scanner"
  ]
}
```

**test_loop**
```json
{
  "message": "🔴 CRITICAL: Integration tests failed 5 times. Scope review required.",
  "suggested_actions": [
    "Review test failures in .claude-bus/feedback/",
    "Consider reducing scope",
    "Consult PM-Architect for decision"
  ]
}
```

---

### ⚠️ HIGH Alerts

**blocker_alert**
```json
{
  "message": "⚠️ Phase 3 blocked for 5 hours. Blocker: Waiting for external API approval.",
  "suggested_actions": [
    "Review blocker: .claude-bus/blockers/Stage1-blocker-001.json",
    "Can we mock the API?",
    "Escalate to API provider"
  ]
}
```

**tech_debt_alert**
```json
{
  "message": "⚠️ Critical technical debt: Chat endpoint 387 lines (complex). Should refactor before Stage 2.",
  "suggested_actions": [
    "Extract helper functions",
    "Split into multiple endpoints",
    "Add to Stage 2 planning"
  ]
}
```

---

## Automatic Actions Taken By System

### When Service Fails:
1. ✅ **Attempt restart** (3 times, 2 minutes apart)
2. ✅ **Log failure** to monitoring/service-failures.jsonl
3. ✅ **Create blocker** if restart fails
4. ✅ **Alert you** via notification
5. ✅ **Block phase** until resolved

### When Security Issue Found:
1. ✅ **Reject review** immediately
2. ✅ **Create CRITICAL alert**
3. ✅ **Create feedback file** with details
4. ✅ **Block Phase 4** (git integration)
5. ✅ **Return to Phase 2** for fix

### When Tech Debt Detected:
1. ✅ **Create debt file** automatically
2. ✅ **Log to events**
3. ✅ **Update review** with debt reference
4. ✅ **Alert if critical** severity
5. ✅ **Track for paydown** in next stage

### When Blocker Occurs:
1. ✅ **Update task status** to `blocked`
2. ✅ **Create blocker file**
3. ✅ **Monitor duration** (alerts if > 4 hours)
4. ✅ **Suggest resolution** options
5. ✅ **Escalate if persistent**

---

## Quick Check Commands

### Check All Active Issues
```powershell
# All active alerts
grep '"status":"active"' .claude-bus/notifications/user-alerts.jsonl

# Critical only
grep '"severity":"critical"' .claude-bus/notifications/user-alerts.jsonl | grep '"status":"active"'

# Count by type
grep '"notification_type":"service_down"' .claude-bus/notifications/user-alerts.jsonl | wc -l
```

### Check Service Health Right Now
```powershell
# Run health check script
.\.claude-bus\scripts\health-check.ps1

# Or manually check each service
curl http://localhost:8080/v1/models  # llama.cpp
curl http://localhost:7474            # neo4j
curl http://localhost:8001/api/v1/heartbeat  # chroma
```

### Check Tech Debt
```powershell
# All active debt
ls .claude-bus/tech-debt/*.json

# Critical debt only
grep '"severity":"critical"' .claude-bus/tech-debt/*.json
```

### Check Current Phase Status
```powershell
# View project status
cat todo/PROJECT_STATUS.md

# Check for blockers
ls .claude-bus/blockers/*.json
```

---

## What You Need To Do

### Daily (Recommended)
✅ Check alerts: `tail -20 .claude-bus/notifications/user-alerts.jsonl`
✅ Review `PROJECT_STATUS.md` for critical notes
✅ Address any critical (🔴) alerts

### After Each Phase
✅ Check for new notifications
✅ Review tech debt summary
✅ Verify no active blockers

### When Notified
✅ Read alert message
✅ Follow suggested actions
✅ Mark as resolved when fixed:
```json
{
  "id": "notify-001",
  "status": "resolved",
  "resolved_at": "2025-11-17T15:00:00",
  "resolved_by": "user",
  "resolution_notes": "Restarted service manually"
}
```

---

## Configuration

### Enable/Disable Monitoring

Edit `.claude-bus/config/auto-monitoring.json`:

```json
{
  "enabled": true,  // Master switch
  "automated_tech_debt_detection": {
    "enabled": true  // Disable specific monitors
  },
  "automated_service_health_monitoring": {
    "enabled": true
  }
}
```

### Adjust Alert Thresholds

```json
{
  "escalation_triggers": [
    {
      "condition": "Phase blocked for > 4 hours",  // Change to 8 hours
      "severity": "high"
    }
  ]
}
```

---

## Summary: What's Automated vs Manual

| Feature | Automated? | Your Action |
|---------|------------|-------------|
| **Tech Debt Detection** | ✅ Auto | Review alerts |
| **Tech Debt Tracking** | ✅ Auto files created | Approve paydown plan |
| **Service Health Checks** | ✅ Every 5 min | Fix if restart fails |
| **Service Restarts** | ✅ Auto (3 attempts) | Manual if fails |
| **Security Scanning** | ✅ Auto | Fix issues immediately |
| **Performance Testing** | ✅ Auto | Optimize if below baseline |
| **Blocker Detection** | ✅ Auto | Resolve blockers |
| **User Notifications** | ✅ Auto-created | Read and respond |
| **Phase Gates** | ✅ Auto-checked | Approve transitions |
| **Escalation** | ✅ Auto | Provide decisions |

---

## Bottom Line

### Question: Will issues get auto-tracked and raised to you automatically?

### Answer: **YES!** ✅

**Auto-Tracked**:
- Technical debt → `.claude-bus/tech-debt/`
- Service health → `.claude-bus/monitoring/`
- Blockers → `.claude-bus/blockers/`
- All issues → `.claude-bus/events.jsonl`

**Auto-Alerted**:
- Critical issues → `.claude-bus/notifications/user-alerts.jsonl`
- Also in → `todo/PROJECT_STATUS.md` (🔔 section)
- Emoji indicators → 🔴 CRITICAL, ⚠️ HIGH, 📘 INFO

**Auto-Actions**:
- Service restarts (3 attempts)
- Blocker creation
- Phase blocking (if critical)
- PM-Architect escalation

**You Only Need To**:
- Check alerts daily (or after phases)
- Respond to critical (🔴) issues
- Approve or reject PM-Architect recommendations

---

## Your Question Answered: How Notifications Work

### Question:
> "So the warning will be in some kind of json file? when I process to next phase, will the currently claude code cli session show me some kind of warning?"

### Answer:

**Warnings appear in BOTH places**:

#### 1. IN YOUR CHAT SESSION (Primary) ✅
**YES, you WILL see warnings directly in the Claude Code CLI session!**

- **Critical issues**: Displayed immediately with 🔴 emoji
- **Phase transitions**: Show summary before proceeding
- **Service failures**: Auto-display with suggested fixes
- **Security issues**: Block with visible message

**You don't need to check files manually.**

#### 2. In JSON Files (Secondary) ✅
**YES, also logged to files for history/automation:**

- `.claude-bus/notifications/user-alerts.jsonl` (all alerts)
- `todo/PROJECT_STATUS.md` (critical alerts only)
- For automation, agents, and reference

---

### What You'll Actually See

**Scenario 1: Service goes down during Phase 2**

You'll see in your chat:
```
PM-Architect: 🔴 SERVICE HEALTH ALERT

llama.cpp service failed to restart after 3 attempts

Status: Phase 2 Development is BLOCKED

Suggested actions:
1. docker-compose logs llama
2. nvidia-smi
3. docker-compose restart llama

Should I wait while you investigate?
```

**You type**: "Let me check the logs..."

---

**Scenario 2: Trying to proceed to Phase 3 with warnings**

You type: "Let's move to Phase 3"

You'll see:
```
PM-Architect: Let me check Phase 2 completion status first...

═══════════════════════════════════════════════════════
  PHASE 2 → PHASE 3 TRANSITION GATE
═══════════════════════════════════════════════════════

✅ Code files created
✅ Tests passing
⚠️ WARNING: 2 tech debt items detected

Active Warnings:
- ⚠️ Function complexity high in chat.py (notify-002)
- ⚠️ Test coverage 45% (target: 80%) (notify-003)

You can proceed, but these should be addressed in Stage 2.

Proceed to Phase 3? (y/n)
```

**You type**: "y"

```
PM-Architect: Acknowledged. Proceeding to Phase 3...
```

---

**Scenario 3: Critical security issue found**

During Phase 3 review:
```
QA-Agent: Reviewing backend/api/chat.py...

🔴 SECURITY VULNERABILITY DETECTED

Type: SQL Injection Risk
File: backend/api/chat.py:42
Severity: CRITICAL

Code:
  query = f"SELECT * FROM messages WHERE project_id = {project_id}"

Required fix:
  Use parameterized queries

Status: Review REJECTED
Phase 3 → Phase 4 transition is BLOCKED

Feedback created: .claude-bus/feedback/Stage1-feedback-001.json
Returning to Phase 2 for revision...
```

---

### Summary Table

| Notification Type | In Chat? | In File? | Blocks Progress? |
|-------------------|----------|----------|------------------|
| 🔴 Critical | ✅ YES - Immediate | ✅ YES | ✅ YES |
| ⚠️ High | ✅ YES - At transition | ✅ YES | ⚠️ Asks confirmation |
| 📘 Medium | ✅ YES - Summary only | ✅ YES | ❌ NO |
| 💡 Low | ⚠️ Mentioned briefly | ✅ YES | ❌ NO |

---

### Bottom Line

**Files**: For automation, history, reference
**Chat**: For YOU to see warnings in real-time

**You will NOT miss critical issues** - they appear directly in your chat session and block progress until resolved.

---

**Last Updated**: 2025-11-17
**Confidence**: 100% - Fully implemented with in-session display protocol
**Status**: ✅ READY FOR PRODUCTION USE
