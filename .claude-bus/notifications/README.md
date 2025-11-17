# Automated User Notifications

## Purpose
This directory contains **automated alerts and notifications** that are **automatically created** by the workflow when critical issues arise. You don't need to ask - the system will notify you proactively.

## How It Works

### Automatic Detection
The workflow continuously monitors for issues:
- **Tech Debt**: Auto-detected during code review (Phase 3)
- **Service Health**: Monitored every 5 minutes (Phase 2-5)
- **Blockers**: Detected when tasks/phases get stuck
- **Security**: Auto-flagged during review
- **Performance**: Auto-checked in integration tests

### Automatic Escalation
When critical issues are detected, **you are automatically notified**:
1. Issue detected by agent (QA-Agent, PM-Architect-Agent)
2. Severity evaluated (critical/high/medium/low)
3. If critical or high → **Automatic notification created**
4. Notification written to `user-alerts.jsonl`
5. Critical alerts also added to `todo/PROJECT_STATUS.md`

### Reading Your Notifications

**Quick Check** (last 20 alerts):
```powershell
tail -20 .claude-bus/notifications/user-alerts.jsonl
```

**Check for Critical Only**:
```powershell
grep '"severity":"critical"' .claude-bus/notifications/user-alerts.jsonl
```

**Count Unresolved Alerts**:
```powershell
grep '"status":"active"' .claude-bus/notifications/user-alerts.jsonl | wc -l
```

**Filter by Type**:
```powershell
# Service issues
grep '"notification_type":"service_down"' user-alerts.jsonl

# Security alerts
grep '"notification_type":"security_alert"' user-alerts.jsonl

# Blockers
grep '"notification_type":"blocker_alert"' user-alerts.jsonl
```

## Notification Types

### 🔴 CRITICAL (Requires Immediate Action)

**service_down**
```
Service failed to restart after 3 attempts
Action: Check docker logs, restart manually if needed
```

**security_alert**
```
Security vulnerability detected (SQL injection, XSS, etc.)
Action: Must fix before proceeding to next phase
```

**test_loop**
```
Integration tests failed 5 times
Action: Review scope, may need to reduce requirements
```

### ⚠️ HIGH (Action Needed Soon)

**blocker_alert**
```
Phase blocked for > 4 hours
Action: Review blocker, assign resources to unblock
```

**review_loop**
```
Task rejected 3 times by QA
Action: May need redesign or scope change
```

**tech_debt_alert**
```
Critical technical debt detected
Action: Should address before stage completion
```

**performance_alert**
```
Performance below baseline by >50%
Action: Optimization or scope reduction needed
```

**debt_accumulation**
```
Too many critical debt items (>3)
Action: Review debt, plan paydown
```

### 📘 INFO (For Awareness)

**tech_debt_created**
```
Medium/low severity debt detected
Action: Review during stage planning
```

**service_recovered**
```
Service recovered after failure
Action: Monitor for stability
```

**phase_completed**
```
Phase successfully completed
Action: Review summary, proceed to next
```

## Notification Format

Each notification in `user-alerts.jsonl`:
```json
{
  "id": "notify-001",
  "timestamp": "2025-11-17T14:30:00+08:00",
  "severity": "critical",
  "notification_type": "service_down",
  "trigger": "Service restart failed 3 times",
  "message": "🔴 CRITICAL: llama.cpp failed to restart after 3 attempts. Manual intervention required.",
  "details": {
    "service": "llama.cpp",
    "failure_count": 3,
    "last_error": "Connection refused",
    "restart_attempts": ["14:20:00", "14:22:00", "14:25:00"]
  },
  "suggested_actions": [
    "Check docker logs: docker-compose logs llama",
    "Check GPU status: nvidia-smi",
    "Restart manually: docker-compose restart llama",
    "Check model file exists and accessible"
  ],
  "status": "active",
  "resolved_at": null,
  "resolved_by": null
}
```

## Automatic Actions Taken

When an alert is created, the system **automatically**:

1. **Logs to File**: Writes to `user-alerts.jsonl`
2. **Updates Status**: Adds to `todo/PROJECT_STATUS.md` (critical only)
3. **Creates Blocker**: Creates blocker file if needed
4. **Attempts Recovery**: Auto-restart services if possible
5. **Escalates**: Notifies PM-Architect for decision

## Resolving Notifications

### Manual Resolution
When you fix an issue:
```json
// Update the notification status
{
  "id": "notify-001",
  "status": "resolved",
  "resolved_at": "2025-11-17T15:00:00+08:00",
  "resolved_by": "user",
  "resolution_notes": "Manually restarted service, increased GPU memory allocation"
}
```

### Automatic Resolution
System auto-resolves when:
- Service recovers (service_down → service_recovered)
- Blocker removed (blocker_alert → auto-resolved)
- Test passes (test_loop → auto-resolved when tests succeed)

## Monitoring Dashboard

Check `todo/PROJECT_STATUS.md` for:
```markdown
## 🔔 Important Notes

### Active Alerts (2)
- 🔴 CRITICAL: llama.cpp service down (notify-001)
- ⚠️ HIGH: Phase 3 blocked for 5 hours (notify-003)

### Resolved Today (1)
- ✅ Service recovered: neo4j (notify-002)
```

## Configuration

Enable/disable monitoring in `.claude-bus/config/auto-monitoring.json`:
```json
{
  "enabled": true,  // Set to false to disable all auto-monitoring
  "automated_service_health_monitoring": {
    "enabled": true  // Disable specific monitors
  }
}
```

## Alert Severity Guide

| Severity | Response Time | Can Skip? | Escalation |
|----------|---------------|-----------|------------|
| **Critical** | Immediate | No | Blocks phase transition |
| **High** | Within 4 hours | No | Escalates after 4 hours |
| **Medium** | Within 24 hours | Yes | Advisory only |
| **Low** | When convenient | Yes | No escalation |

## Best Practices

✅ **Do**:
- Check `user-alerts.jsonl` daily (or after each phase)
- Resolve critical alerts immediately
- Review high alerts within 4 hours
- Use suggested actions as starting point

❌ **Don't**:
- Ignore critical alerts (they block progress)
- Disable monitoring without understanding impact
- Delete unresolved notifications (mark resolved instead)

## Emergency Contact

If overwhelmed by alerts:
1. Check `PROJECT_STATUS.md` for summary
2. Filter by severity: focus on critical first
3. PM-Architect-Agent can help prioritize
4. Can defer medium/low to next stage

---

**Last Updated**: 2025-11-17
**Auto-Generated**: This notification system is fully automated
**Your Action Required**: Check this file regularly, especially after phase transitions
