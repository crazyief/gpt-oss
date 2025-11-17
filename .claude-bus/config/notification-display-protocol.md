# In-Session Notification Display Protocol

**Purpose**: Ensure user SEES warnings in Claude Code session, not just in JSON files

**Last Updated**: 2025-11-17

---

## The Problem This Solves

**Before**: Warnings written to JSON files, user must remember to check manually
**After**: Warnings displayed directly in chat session, blocking critical issues

---

## Protocol: Dual Notification System

### 1. Write to File (For History/Logging)
```bash
echo '{...}' >> .claude-bus/notifications/user-alerts.jsonl
```

### 2. Display to User (MANDATORY)
Output text message in the current chat session

---

## When Warnings Are Displayed

### During Agent Execution
If agent detects issue → **Immediate text output**

### Before Phase Transitions
PM-Architect **MUST** check alerts and display summary

### After Phase Completion
PM-Architect displays summary of issues found

---

## Display Formats by Severity

### 🔴 CRITICAL (Blocks Progress)

**What user sees**:
```
⚠️ CANNOT PROCEED TO PHASE 3

I've detected critical issues that must be resolved first:

🔴 CRITICAL: llama.cpp service down (notify-001)
   - Service failed to restart after 3 attempts
   - Suggested action: docker-compose restart llama

🔴 SECURITY: SQL injection risk (notify-003)
   - File: backend/api/chat.py:42
   - Suggested action: Use parameterized queries

Status: Phase 2 → Phase 3 transition is BLOCKED
Resolution required before continuing.

Would you like me to help troubleshoot these issues?
```

**Behavior**:
- Phase transition BLOCKED
- PM-Architect waits for user resolution
- No automated proceeding

---

### ⚠️ HIGH (Warning, Can Proceed with Confirmation)

**What user sees**:
```
⚠️ WARNING: High-priority issues detected

Before proceeding to Phase 4, please review:

⚠️ HIGH: Phase 3 blocked for 4 hours (notify-002)
   - Task Stage1-task-005 is blocked
   - Suggested action: Review blocker, assign resources

⚠️ HIGH: Critical tech debt detected (notify-004)
   - Chat endpoint is 387 lines (complex)
   - Suggested action: Refactor before Stage 2

These issues should be addressed soon, but aren't blocking.

Options:
1. Proceed to Phase 4 (warnings acknowledged)
2. Stop and resolve issues now
3. Get more details

Your choice?
```

**Behavior**:
- PM-Architect asks for confirmation
- User can proceed or stop
- Warnings logged for later

---

### 📘 MEDIUM/LOW (Info Only)

**What user sees**:
```
📘 Phase 3 Review Complete

Summary:
✅ All code approved
✅ Quality standards met
✅ Tests passing

Notes:
- 2 medium-priority tech debt items detected
- 1 low-priority suggestion from QA

Details: .claude-bus/notifications/user-alerts.jsonl

Proceeding to Phase 4: Git Integration...
```

**Behavior**:
- Info displayed but doesn't block
- User can check details if interested
- Automatic progression

---

## Phase Transition Checklist Display

**Before every phase transition, user sees**:

```
═══════════════════════════════════════════════════════
  PHASE 2 → PHASE 3 TRANSITION CHECKLIST
═══════════════════════════════════════════════════════

Pre-Transition Checks:
✅ All code files created (3 files)
✅ Unit tests exist and passing (15/15 tests)
✅ Service readiness signals published
✅ No blocking errors

Active Alerts:
📘 2 medium-priority tech debt items detected

Phase 2 Status: COMPLETE ✓
Phase 3 Status: READY TO START

═══════════════════════════════════════════════════════

Proceeding to Phase 3: Review Phase...
```

---

## Tech Debt Detection Display

**When QA-Agent detects tech debt during review**:

```
Phase 3 Review: Reviewing backend/api/chat.py...

⚠️ Technical Debt Detected

File: backend/api/chat.py
Issue: Function length 387 lines (complex but passes 400 limit)
Severity: MEDIUM
Recommendation: Extract helper functions for better maintainability

Auto-created: .claude-bus/tech-debt/Stage1-debt-001.json

This doesn't block approval, but should be addressed in Stage 2.

Continuing review...
```

---

## Service Health Issue Display

**When service goes down during development**:

```
🔴 SERVICE HEALTH ALERT

llama.cpp service health check failed at 14:20:00

Auto-recovery attempt 1/3: FAILED
Auto-recovery attempt 2/3: FAILED
Auto-recovery attempt 3/3: FAILED

Status: Service is DOWN
Impact: Phase 2 Development is BLOCKED

Troubleshooting steps:
1. Check logs: docker-compose logs llama
   Output: [Connection refused on port 8080]

2. Check GPU: nvidia-smi
   Run this command to verify GPU is available

3. Manual restart: docker-compose restart llama
   Try this to restart the service

Alert logged: .claude-bus/notifications/user-alerts.jsonl (notify-001)

Should I wait while you investigate, or would you like me to help troubleshoot?
```

---

## Security Issue Display

**When security vulnerability found**:

```
🔴 SECURITY VULNERABILITY DETECTED

Phase 3 Review: REJECTED

Critical Issue Found:
- Type: SQL Injection Risk
- File: backend/api/chat.py:42
- Severity: CRITICAL
- Status: MUST FIX BEFORE PROCEEDING

Code snippet:
```python
# Line 42 - UNSAFE
query = f"SELECT * FROM messages WHERE project_id = {project_id}"
```

Required fix:
Use parameterized queries or ORM:
```python
# Safe approach
query = "SELECT * FROM messages WHERE project_id = ?"
cursor.execute(query, (project_id,))
```

Reference: OWASP Top 10 - A03:2021 Injection

Action taken:
✅ Review status → REJECTED
✅ Feedback file created: .claude-bus/feedback/Stage1-feedback-001.json
✅ Task status → needs_revision
✅ Critical alert created: notify-005

Phase 3 → Phase 4 transition is BLOCKED until this is fixed.

Returning to Phase 2 for revision...
```

---

## Performance Issue Display

**When performance below baseline in Phase 5**:

```
Phase 5: Integration Testing

⚠️ PERFORMANCE ISSUE DETECTED

Test: LLM First Token Latency
Expected: < 2 seconds
Actual: 4.2 seconds
Status: ❌ FAILED (110% over baseline)

Test: API Response Time
Expected: < 500ms
Actual: 320ms
Status: ✅ PASSED

Overall Performance: BELOW BASELINE

Suggested actions:
1. Profile LLM service for bottlenecks
2. Check GPU memory allocation
3. Review batch size settings
4. Consider model quantization

Impact: Phase 5 → Stage Complete transition is BLOCKED

Options:
1. Optimize now (return to Phase 2)
2. Accept current performance (requires your approval)
3. Reduce scope (smaller model)

Your decision?
```

---

## Example: Complete Phase Transition Flow

**User's Claude Code session shows**:

```
You: "Let's proceed to Phase 3"

PM-Architect: Let me check the Phase 2 → Phase 3 transition requirements...

═══════════════════════════════════════════════════════
  PHASE 2 → PHASE 3 TRANSITION GATE
═══════════════════════════════════════════════════════

Checking Phase 2 completion...

✅ Backend code: 5 files created
✅ Frontend code: 8 files created
✅ Unit tests: 23 tests, all passing
✅ Service readiness: backend-ready.json, frontend-ready.json
✅ Task status: All tasks completed
✅ No blocking dependencies

Checking for active alerts...

📘 INFO: 2 medium-priority tech debt items detected
   - Detail: Function complexity in 2 files
   - Action: Review before Stage 2

⚠️ HIGH: Test coverage is 45% (target: 80%)
   - Status: Passes minimum (20%) but low
   - Recommendation: Add more tests in Stage 2

═══════════════════════════════════════════════════════

Phase 2 Status: COMPLETE ✓
Phase 3 Status: READY TO START
Warnings: 2 (none critical)

Proceed to Phase 3: Review Phase? (y/n)

You: "y"

PM-Architect: Proceeding to Phase 3: Review Phase

Invoking QA-Agent for code review...
```

---

## Rules for Agents

### PM-Architect-Agent MUST:
1. **Check alerts before every phase transition**
2. **Display summary to user** (don't skip this!)
3. **Block if critical** (no bypass without user approval)
4. **Ask for confirmation** if warnings exist
5. **Log to file AND output to chat**

### QA-Agent MUST:
1. **Display tech debt when detected** (not just write to file)
2. **Show security issues immediately** with code snippets
3. **Explain why** something is flagged
4. **Provide actionable suggestions**

### All Agents MUST:
1. **Write to file first** (for logging)
2. **Output to user second** (for visibility)
3. **Never silently log** critical issues
4. **Always provide suggested actions**

---

## Quick Reference: Display Checklist

Before phase transition, PM-Architect outputs:

```markdown
- [ ] Read user-alerts.jsonl for active alerts
- [ ] Count by severity (critical, high, medium, low)
- [ ] Display header: "PHASE {N} → PHASE {N+1} TRANSITION"
- [ ] Show completion checks for current phase
- [ ] Display active alerts with severity indicators
- [ ] If critical → Block with "CANNOT PROCEED"
- [ ] If high → Ask "Proceed? (y/n)"
- [ ] If medium/low → Show info, auto-proceed
- [ ] Log transition to events.jsonl
```

---

## Summary

### Dual System:
1. **Files** = History/logging/automation
2. **Chat output** = User visibility/awareness

### Critical Rule:
**NEVER write to file without also displaying to user for critical/high issues**

### User Experience:
- Sees warnings in real-time
- Can't miss critical issues
- Gets actionable suggestions
- Can make informed decisions

---

**Last Updated**: 2025-11-17
**Mandatory**: All agents must follow this protocol
**Verified By**: PM-Architect-Agent ensures compliance
