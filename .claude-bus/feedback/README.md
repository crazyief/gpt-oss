# Feedback Loop Mechanism

## Purpose
This directory contains feedback files created when code review or testing failures require rework. Feedback files provide specific, actionable instructions for revision.

## When Feedback Files Are Created

### Phase 3 → Phase 2 (Review Failures)
- **Trigger**: QA-Agent marks review status as `needs_revision` or `rejected`
- **File Format**: `Stage{N}-feedback-{task-id}-v{revision-number}.json`
- **Example**: `Stage1-feedback-task-001-v1.json`

### Phase 5 → Phase 2 (Integration Test Failures)
- **Trigger**: Integration tests fail in Phase 5
- **File Format**: `Stage{N}-bug-{number}.json`
- **Example**: `Stage1-bug-001.json`

## Feedback File Structure

```json
{
  "id": "Stage1-feedback-task-001-v1",
  "type": "code_review_revision" | "integration_bug" | "security_issue",
  "task_id": "Stage1-task-001",
  "from_phase": 3,
  "to_phase": 2,
  "severity": "critical" | "high" | "medium" | "low",
  "created_at": "2025-11-17T10:00:00+08:00",
  "created_by": "QA-Agent",
  "assigned_to": "Backend-Agent",

  "issues": [
    {
      "file": "backend/api/chat.py",
      "line_number": 42,
      "issue_type": "security_vulnerability",
      "description": "SQL injection risk in query construction",
      "current_code": "SELECT * FROM messages WHERE project_id = {project_id}",
      "required_fix": "Use parameterized queries or ORM",
      "reference": "OWASP Top 10 - A03:2021 Injection"
    },
    {
      "file": "backend/api/chat.py",
      "line_number": 87,
      "issue_type": "code_quality",
      "description": "Function exceeds 50 lines (found 73 lines)",
      "required_fix": "Split into smaller functions",
      "suggestion": "Extract streaming logic into separate helper function"
    }
  ],

  "required_changes": [
    "Fix SQL injection vulnerability using parameterized queries",
    "Refactor chat endpoint to stay under 50 lines per function",
    "Add input validation for all user-provided parameters"
  ],

  "revision_deadline": "2025-11-17T18:00:00+08:00",
  "max_revision_attempts": 3,
  "current_attempt": 1,

  "status": "pending_revision" | "in_revision" | "resolved" | "escalated",
  "resolved_at": null,
  "resolution_notes": null
}
```

## Workflow

1. **QA-Agent detects issue** (Phase 3 or Phase 5)
2. **QA-Agent creates feedback file** in `.claude-bus/feedback/`
3. **QA-Agent updates task status** to `needs_revision`
4. **PM-Architect notifies developer agent** via message bus
5. **Developer agent reads feedback file**
6. **Developer agent fixes issues**
7. **Developer agent updates task status** to `in_progress`
8. **Workflow returns to Phase 2** → Phase 3 → (re-review)
9. **If approved**: QA marks feedback as `resolved`
10. **If still failing**: Increment `current_attempt`
11. **If attempt > max_attempts**: Escalate to PM-Architect

## Escalation Process

If revision attempts exceed maximum (3 for code review, 5 for integration):
1. Create escalation file in `.claude-bus/escalations/`
2. Notify PM-Architect
3. PM-Architect decides:
   - Redesign approach (create new task)
   - Extend max attempts (if close to solution)
   - Cancel task (if infeasible)
   - Simplify requirements (reduce scope)

## Example Feedback Scenarios

### Scenario 1: Security Vulnerability
```json
{
  "severity": "critical",
  "issue_type": "security_vulnerability",
  "required_fix": "Immediately fix SQL injection before proceeding"
}
```

### Scenario 2: Code Quality
```json
{
  "severity": "medium",
  "issue_type": "code_quality",
  "required_fix": "Refactor to meet 400 line limit"
}
```

### Scenario 3: Integration Bug
```json
{
  "severity": "high",
  "issue_type": "integration_bug",
  "description": "WebSocket disconnects after 30 seconds of streaming",
  "reproduction_steps": ["Start chat", "Ask long question", "Observe disconnect at 30s"],
  "expected_behavior": "Stream continues until complete",
  "actual_behavior": "Connection drops mid-stream"
}
```

## File Naming Convention

- **Code Review Feedback**: `Stage{N}-feedback-{task-id}-v{revision}.json`
- **Integration Bugs**: `Stage{N}-bug-{number}.json`
- **Security Issues**: `Stage{N}-security-{number}.json`
- **Performance Issues**: `Stage{N}-perf-{number}.json`

## Retention Policy

- **Active feedback**: Kept until resolved
- **Resolved feedback**: Archived to `.claude-bus/feedback/archive/`
- **Archive retention**: Keep for entire project (reference for future stages)

## Notes

This feedback mechanism prevents workflow breakage while maintaining quality. It's a critical part of the iterative development process.
