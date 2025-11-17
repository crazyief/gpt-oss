# Phase Transition Verification Gates

## Purpose
This document defines the verification gates that must pass before transitioning from one phase to the next. These gates prevent premature phase transitions that could lead to workflow breakage.

**Key Principle**: "Don't start what you can't finish" - Each phase must verify its prerequisites before starting and its deliverables before completing.

---

## Phase 1 → Phase 2 Transition Gate

### Prerequisites (Must be TRUE to proceed)
- [x] All 3 Planning Phase inputs verified (i1, i2, i3)
- [ ] All 5 Planning Phase outputs created (o1-o5)
- [ ] PM-Architect approval obtained
- [ ] Super-AI-UltraThink validation complete (if required)
- [ ] Development agents acknowledge task assignments

### Verification Checklist
```json
{
  "gate_id": "phase1_to_phase2",
  "checks": [
    {
      "id": "g1",
      "check": "Stage{N}-task-*.json files exist in .claude-bus/tasks/",
      "command": "ls .claude-bus/tasks/Stage1-task-*.json | wc -l",
      "expected": "> 0",
      "critical": true
    },
    {
      "id": "g2",
      "check": "Stage{N}-api-*.json files exist in .claude-bus/contracts/",
      "command": "ls .claude-bus/contracts/Stage1-api-*.json | wc -l",
      "expected": "> 0",
      "critical": true
    },
    {
      "id": "g3",
      "check": "Stage{N}-dep-*.json files exist in .claude-bus/dependencies/",
      "command": "ls .claude-bus/dependencies/Stage1-dep-*.json | wc -l",
      "expected": "> 0",
      "critical": true
    },
    {
      "id": "g4",
      "check": "Architecture decisions documented",
      "artifact": ".claude-bus/planning/Stage1-architecture.json",
      "critical": true
    },
    {
      "id": "g5",
      "check": "Coding standards defined",
      "artifact": ".claude-bus/config/Stage1-standards.json",
      "critical": true
    },
    {
      "id": "g6",
      "check": "Artifacts registered in artifact registry",
      "artifact": ".claude-bus/registry/artifact-registry.json",
      "validation": "Contains Stage 1 artifact entries",
      "critical": true
    },
    {
      "id": "g7",
      "check": "Phase 2 prerequisites can be met",
      "validation": "Phase 2 inputs (i1-i5) match Phase 1 outputs (o1-o5)",
      "critical": true
    }
  ]
}
```

### Actions on Gate Pass
1. Update `phase1-planning-checklist.json` status to `completed`
2. Update `phase2-development-checklist.json` status to `in_progress`
3. Log phase transition to `.claude-bus/events.jsonl`
4. Notify all development agents (Backend, Frontend, Document-RAG)

### Actions on Gate Fail
1. Keep Phase 1 status as `in_progress`
2. Create blocker issue in `.claude-bus/blockers/`
3. Notify PM-Architect
4. Do NOT proceed to Phase 2

---

## Phase 2 → Phase 3 Transition Gate

### Prerequisites (Must be TRUE to proceed)
- [ ] All assigned tasks have status `completed` or `testing`
- [ ] Code files exist in `.claude-bus/code/Stage{N}-*/`
- [ ] Unit tests exist for all new code
- [ ] Unit tests pass locally
- [ ] Service readiness signals published
- [ ] No blocking errors in development

### Verification Checklist
```json
{
  "gate_id": "phase2_to_phase3",
  "checks": [
    {
      "id": "g1",
      "check": "Backend code files exist",
      "command": "find .claude-bus/code/Stage1-backend/ -name '*.py' | wc -l",
      "expected": "> 0",
      "critical": true
    },
    {
      "id": "g2",
      "check": "Frontend code files exist",
      "command": "find .claude-bus/code/Stage1-frontend/ -name '*.svelte' -o -name '*.ts' | wc -l",
      "expected": "> 0",
      "critical": true
    },
    {
      "id": "g3",
      "check": "Unit test files exist",
      "command": "find .claude-bus/code/Stage1-tests/ -name 'test_*.py' -o -name '*.test.ts' | wc -l",
      "expected": "> 0",
      "critical": true
    },
    {
      "id": "g4",
      "check": "Unit tests pass",
      "command": "pytest .claude-bus/code/Stage1-tests/ (or appropriate test runner)",
      "expected": "All tests pass",
      "critical": true
    },
    {
      "id": "g5",
      "check": "All tasks completed or blocked",
      "validation": "No tasks in 'in_progress' status",
      "critical": true
    },
    {
      "id": "g6",
      "check": "API contracts implemented",
      "validation": "All endpoints in contracts/*.json have corresponding code",
      "critical": true
    }
  ]
}
```

### Actions on Gate Pass
1. Update `phase2-development-checklist.json` status to `completed`
2. Update `phase3-review-checklist.json` status to `in_progress`
3. Invoke QA-Agent for code review
4. Log transition to events.jsonl

### Actions on Gate Fail
1. Keep Phase 2 status as `in_progress` or `blocked`
2. Identify which check failed
3. Create task to resolve blocker
4. Notify responsible agent

---

## Phase 3 → Phase 4 Transition Gate

### Prerequisites (Must be TRUE to proceed)
- [ ] All code files reviewed by QA-Agent
- [ ] All reviews have status `approved` or `approved_with_comments`
- [ ] No `rejected` or `needs_revision` status
- [ ] Quality metrics meet standards
- [ ] PM-Architect sign-off obtained

### Verification Checklist
```json
{
  "gate_id": "phase3_to_phase4",
  "checks": [
    {
      "id": "g1",
      "check": "All review files have approved status",
      "command": "jq -r '.status' .claude-bus/reviews/Stage1-review-*.json",
      "expected": "All 'approved' or 'approved_with_comments'",
      "critical": true
    },
    {
      "id": "g2",
      "check": "No code exceeds 400 lines",
      "validation": "Check metrics in reviews/*.json",
      "critical": true
    },
    {
      "id": "g3",
      "check": "No code exceeds 3 levels of nesting",
      "validation": "Check metrics in reviews/*.json",
      "critical": true
    },
    {
      "id": "g4",
      "check": "Comment coverage >= 20%",
      "validation": "Check metrics in reviews/*.json",
      "critical": true
    },
    {
      "id": "g5",
      "check": "No security vulnerabilities detected",
      "validation": "Check security scan results in reviews/*.json",
      "critical": true
    },
    {
      "id": "g6",
      "check": "PM-Architect approval recorded",
      "artifact": ".claude-bus/reviews/Stage1-pm-approval.json",
      "critical": true
    }
  ]
}
```

### Actions on Gate Pass
1. Update `phase3-review-checklist.json` status to `completed`
2. Update `phase4-git-checklist.json` status to `in_progress`
3. Create git commit authorization
4. Invoke QA-Agent for git operations

### Actions on Gate Fail (FEEDBACK LOOP)
1. Keep Phase 3 status as `revision_cycle`
2. Create feedback file in `.claude-bus/feedback/`
3. Update failed tasks to `needs_revision` status
4. Return to Phase 2 Development
5. Increment revision attempt counter
6. If attempts > max (3), escalate to PM-Architect

---

## Phase 4 → Phase 5 Transition Gate

### Prerequisites (Must be TRUE to proceed)
- [ ] All approved code moved from sandbox to src/
- [ ] Git commits created successfully
- [ ] No merge conflicts
- [ ] Version tags created (if milestone)
- [ ] Commit log recorded

### Verification Checklist
```json
{
  "gate_id": "phase4_to_phase5",
  "checks": [
    {
      "id": "g1",
      "check": "Code moved to src/ directories",
      "command": "ls backend/ frontend/ (check for new files)",
      "critical": true
    },
    {
      "id": "g2",
      "check": "Git commits exist",
      "command": "git log --oneline -n 10",
      "expected": "Recent commits visible",
      "critical": true
    },
    {
      "id": "g3",
      "check": "No merge conflicts",
      "command": "git status",
      "expected": "No conflicts reported",
      "critical": true
    },
    {
      "id": "g4",
      "check": "Sandbox cleaned up",
      "validation": "Approved files removed from .claude-bus/code/",
      "critical": false
    },
    {
      "id": "g5",
      "check": "Commit messages follow format",
      "validation": "feat|fix|refactor: description format",
      "critical": true
    }
  ]
}
```

### Actions on Gate Pass
1. Update `phase4-git-checklist.json` status to `completed`
2. Update `phase5-integration-checklist.json` status to `in_progress`
3. Invoke QA-Agent for integration testing
4. Prepare test environment

### Actions on Gate Fail (ROLLBACK)
1. Keep Phase 4 status as `blocked`
2. Revert to code backup in `.claude-bus/code-backup/`
3. Investigate git operation failure
4. Notify PM-Architect
5. Create issue in `.claude-bus/blockers/`

---

## Phase 5 → Stage N+1 Transition Gate

### Prerequisites (Must be TRUE to proceed)
- [ ] All integration tests pass
- [ ] Performance meets baselines
- [ ] All Stage N acceptance criteria met
- [ ] No critical bugs
- [ ] Documentation complete
- [ ] PM-Architect final approval

### Verification Checklist
```json
{
  "gate_id": "phase5_to_stageN_plus_1",
  "checks": [
    {
      "id": "g1",
      "check": "All integration tests pass",
      "artifact": ".claude-bus/test-results/Stage1-integration.json",
      "expected": "status: passed",
      "critical": true
    },
    {
      "id": "g2",
      "check": "Performance meets baselines",
      "artifact": ".claude-bus/metrics/Stage1-performance.json",
      "validation": "Compare against acceptance criteria",
      "critical": true
    },
    {
      "id": "g3",
      "check": "All acceptance criteria satisfied",
      "artifact": ".claude-bus/planning/Stage1-req-001.json",
      "validation": "All requirements marked complete",
      "critical": true
    },
    {
      "id": "g4",
      "check": "No critical or high-severity bugs",
      "command": "grep -r 'severity.*critical\\|high' .claude-bus/feedback/",
      "expected": "No results",
      "critical": true
    },
    {
      "id": "g5",
      "check": "Documentation complete",
      "validation": "User manual, API docs, setup guide exist",
      "critical": true
    },
    {
      "id": "g6",
      "check": "Deployment readiness report approved",
      "artifact": ".claude-bus/reports/Stage1-deployment-ready.json",
      "critical": true
    },
    {
      "id": "g7",
      "check": "Artifact registry updated for Stage 2",
      "artifact": ".claude-bus/registry/artifact-registry.json",
      "validation": "Stage 1 artifacts marked complete, Stage 2 inputs identified",
      "critical": true
    }
  ]
}
```

### Actions on Gate Pass (STAGE COMPLETE!)
1. Update `phase5-integration-checklist.json` status to `completed`
2. Update Stage 1 status to `completed` in artifact registry
3. Create Stage 1 completion report
4. Draft Stage 2 requirements (`.claude-bus/planning/Stage2-req-001.json`)
5. Update `PROJECT_STATUS.md`
6. Celebrate milestone! 🎉

### Actions on Gate Fail (FEEDBACK LOOP)
1. Keep Phase 5 status as `revision_cycle`
2. Create bug reports in `.claude-bus/feedback/`
3. Categorize failures (code bugs, performance, missing features)
4. Return to Phase 2 for bug fixes
5. Increment iteration counter
6. If iterations > max (5), escalate for scope review

---

## General Gate Principles

### Critical vs Non-Critical Checks
- **Critical checks**: Must pass to proceed (gate blocks)
- **Non-critical checks**: Warning only (gate passes with notation)

### Automated vs Manual Verification
- **Automated**: Use commands/scripts where possible
- **Manual**: PM-Architect approval for subjective decisions

### Gate Enforcement
- PM-Architect is responsible for running gate checks
- Gates can be overridden only by PM-Architect with documented reason
- All gate results logged to `.claude-bus/events.jsonl`

### Gate Failure Protocol
1. Identify which check(s) failed
2. Determine root cause
3. Create remediation task
4. Assign to appropriate agent
5. Re-run gate after remediation

---

## Quick Reference

| Transition | Critical Files | Key Command | Fallback Action |
|------------|----------------|-------------|-----------------|
| Phase 1→2 | tasks, contracts, deps | `ls .claude-bus/tasks/Stage*` | Block, notify PM |
| Phase 2→3 | code, tests | `pytest .claude-bus/code/tests/` | Block, fix bugs |
| Phase 3→4 | reviews, approvals | `jq '.status' reviews/*.json` | Feedback loop to Phase 2 |
| Phase 4→5 | git commits | `git log -n 5` | Rollback, retry |
| Phase 5→Next | test results, metrics | `cat test-results/integration.json` | Feedback loop to Phase 2 |

---

**Last Updated**: 2025-11-17
**Maintained By**: PM-Architect-Agent
**Referenced By**: All phase checklists
