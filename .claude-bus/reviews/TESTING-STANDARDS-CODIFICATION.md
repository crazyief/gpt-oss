# Testing Standards Codification - Complete

**Date**: 2025-11-24
**Requested By**: User
**Created By**: PM-Architect-Agent
**Status**: ✅ COMPLETE

---

## User Request

> "Can you ensure we follow the similiar appraoch when comes to test in the future??? you can write such rule in some files???"

**Context**: User approved Option B-2 (MCP-Enhanced Hybrid) testing approach for Stage 1 refactoring and wanted this approach to be **standardized for ALL future stages** (Stage 2-6).

---

## What Was Created

### 1. Developer Guide (40+ pages)

**File**: `docs/TESTING-STANDARDS.md`
**Purpose**: Comprehensive testing guidelines for developers and agents
**Audience**: All team members, external contributors, agents

**Key Sections**:
- Executive Summary (MCP-Enhanced Hybrid approach)
- Testing Pyramid (60% unit, 20% integration, 10% component, 10% E2E)
- Tool Selection Guide (decision tree for Vitest/Playwright/Chrome DevTools)
- Coverage Requirements (52%-80% by stage)
- File Organization (directory structure, naming conventions)
- Quality Gates (pre-commit, pre-PR, pre-production)
- Test Templates (copy-paste ready examples)
- Performance Thresholds (Core Web Vitals)
- Test Execution (local dev, CI/CD pipeline)
- Anti-Patterns (what NOT to do)
- Glossary and References

**Example Content**:

```typescript
// Template: Vitest Unit Test
describe('functionUnderTest', () => {
  it('should return expected value for valid input', () => {
    const result = functionUnderTest('valid input');
    expect(result).toBe('expected output');
  });
});
```

```typescript
// Template: Playwright Component Test
test('should handle user interaction', async ({ page }) => {
  await page.locator('[data-testid="button"]').click();
  await expect(page.locator('[data-testid="result"]')).toHaveText('Expected');
});
```

```typescript
// Template: Chrome DevTools Visual Regression
test('Chat interface - empty state', async ({ page }) => {
  const screenshot = await page.screenshot({ fullPage: true });
  await expect(screenshot).toMatchSnapshot('chat-empty.png', {
    maxDiffPixels: 100,
    threshold: 0.01
  });
});
```

**Impact**: All developers and agents now have clear, actionable guidance on testing.

---

### 2. Agent Rules (20+ pages)

**File**: `.claude-bus/standards/TESTING-RULES.md`
**Purpose**: Enforceable testing rules with automated monitoring
**Audience**: PM-Architect, QA-Agent, Frontend-Agent, Backend-Agent, Super-AI

**Key Sections**:
- Critical Rules (6 mandatory rules with automatic enforcement)
- Agent-Specific Responsibilities (PM-Architect, Frontend, Backend, QA, Super-AI)
- Tool Usage Rules (when to use Vitest vs Playwright vs Chrome DevTools)
- Automated Monitoring Rules (4 auto-monitoring rules)
- Phase Transition Gates (what must pass before proceeding)
- Test Data Management (fixtures, mocks, test database)
- Enforcement Summary (severity levels, actions)

**Enforcement Rules**:

```json
{
  "rule_id": "auto-test-001",
  "severity": "critical",
  "trigger": "Phase 3 complete",
  "condition": "test_coverage < stage_threshold",
  "action": "BLOCK phase transition",
  "notification": {
    "type": "user_alert",
    "message": "Coverage {coverage}% below {threshold}%"
  }
}
```

**Agent Responsibilities**:

**PM-Architect-Agent**:
- Phase 1: Define test scenarios, estimate test count, allocate 30% time for testing
- Phase 3: Review QA results, verify coverage meets threshold, check pyramid compliance
- Phase 4: Coordinate test execution, monitor failures, decide proceed or return

**QA-Agent**:
- Phase 3: Run all tests, generate coverage report, validate pyramid, create review report
- Enforcement: BLOCK transition if coverage < threshold OR pyramid inverted

**Frontend-Agent**:
- Phase 2: Write unit tests (co-located), integration tests (MSW), add data-testid attributes
- Requirement: All functions ≥1 unit test, all API functions ≥1 integration test

**Impact**: Agents now have clear rules with automated enforcement and no ambiguity.

---

### 3. CLAUDE.md Integration

**File**: `CLAUDE.md` (updated)
**Purpose**: Make testing standards discoverable in main project guide
**Location**: New "Testing Standards (MANDATORY)" section (lines 285-350)

**Key Content**:
- Direct references to both documentation files
- Testing pyramid summary (quick reference)
- Coverage thresholds table (Stage 1-6)
- Tool selection rules (one-line guidance)
- Quality gates (automatic enforcement)
- Performance thresholds (Core Web Vitals)
- Responsibilities summary (QA-Agent, PM-Architect, All Agents)

**Example Quick Reference**:

```
Coverage Thresholds (enforced gates):
| Stage | Minimum Coverage |
|-------|-----------------|
| 1     | 52%             |
| 2     | 60%             |
| 3     | 65%             |
| 4     | 70%             |
| 5     | 75%             |
| 6     | 80%             |
```

**Impact**: All agents automatically see testing standards when reading CLAUDE.md.

---

## How This Ensures Future Compliance

### Automatic Discovery

**When agents read CLAUDE.md**, they now see:
1. Testing Standards section (lines 285-350)
2. Links to detailed docs (@docs/TESTING-STANDARDS.md, @.claude-bus/standards/TESTING-RULES.md)
3. Quick reference tables (coverage thresholds, tool selection)
4. Enforcement rules (quality gates)

**No manual reminders needed** - it's baked into the project guide.

---

### Automated Enforcement

**Phase Transition Gates** prevent non-compliant code from advancing:

**Phase 2 → Phase 3**:
- ✅ Git checkpoint created
- ✅ All new code has co-located tests
- ✅ TypeScript compilation succeeds

**Phase 3 → Phase 4**:
- ✅ All tests passing (100%)
- ✅ Coverage ≥ threshold (CRITICAL gate)
- ✅ Test pyramid compliant (HIGH gate)
- ✅ All files ≤ 400 lines

**Phase 4 → Phase 5**:
- ✅ All integration tests passing
- ✅ Visual regression passing
- ✅ Performance tests passing (LCP ≤ 2.5s)
- ✅ No CRITICAL/HIGH alerts

**QA-Agent automatically enforces** these gates and creates CRITICAL alerts if violated.

---

### Agent Invocation Protocol

**During Phase 1 (Planning)**, PM-Architect MUST:
1. Read test plan template from TESTING-RULES.md
2. Create `.claude-bus/planning/stages/stage{N}/test-plan.json`
3. Define test scenarios for new features
4. Estimate test count to meet coverage threshold
5. Allocate 30% of development time for testing

**During Phase 3 (Review)**, QA-Agent MUST:
1. Read enforcement rules from TESTING-RULES.md
2. Run all tests (`npm run test && npm run test:e2e && npm run test:visual && npm run test:performance`)
3. Generate coverage report
4. Validate test pyramid compliance
5. If violations: Create alerts, BLOCK transition

**No manual checklist needed** - agents follow standardized protocol.

---

## Coverage Progression (Stage 1-6)

| Stage | Coverage | New Tests | Total Tests | Key Features |
|-------|----------|-----------|-------------|--------------|
| **Stage 1** | 52% | 140 | 140 | Foundation (projects, chat, documents) |
| **Stage 2** | 60% | +80 | 220 | RAG Core (retrieval, generation, citations) |
| **Stage 3** | 65% | +100 | 320 | Standards (IEC 62443, ETSI, EN 18031) |
| **Stage 4** | 70% | +120 | 440 | Intelligence (knowledge graphs, entity extraction) |
| **Stage 5** | 75% | +140 | 580 | Production (audit trails, performance optimization) |
| **Stage 6** | 80% | +160 | 740 | Advanced (multi-user, fine-tuning, deployment) |

**Progression enforced** by automated gates at every phase transition.

---

## Testing Pyramid Consistency (ALL Stages)

Every stage MUST maintain:
- **60% unit tests** (Vitest, fast feedback)
- **20% integration tests** (Vitest + MSW, realistic workflows)
- **10% component tests** (Playwright MCP, real browser)
- **10% E2E tests** (Playwright MCP, full user journeys)
- **3-5 visual regression tests** (Chrome DevTools MCP, UI consistency)
- **2-3 performance tests** (Chrome DevTools MCP, Core Web Vitals)

**Pyramid validated** by QA-Agent during Phase 3.

---

## Performance Consistency (ALL Stages)

Every stage MUST achieve:
- **LCP** ≤ 2.5s (Largest Contentful Paint)
- **FCP** ≤ 1.8s (First Contentful Paint)
- **CLS** ≤ 0.1 (Cumulative Layout Shift)
- **Bundle size** ≤ 60 KB Stage 1, ≤ 100 KB Stage 6 (gzipped)

**Performance tested** by Chrome DevTools MCP during Phase 4.

---

## Tool Selection Decision Tree (ALL Stages)

```
What are you testing?

├─ Pure JavaScript logic (no DOM, no network)?
│  └─ Vitest unit test
│
├─ Multiple modules with API calls?
│  └─ Vitest integration test + MSW
│
├─ Svelte component behavior (clicks, inputs)?
│  └─ Playwright MCP component test
│
├─ Full user workflow (login → upload → chat)?
│  └─ Playwright MCP E2E test
│
├─ UI appearance (layout, colors)?
│  └─ Chrome DevTools MCP visual regression
│
└─ Page speed (load time, latency)?
   └─ Chrome DevTools MCP performance test
```

**Decision tree referenced** by all agents during development.

---

## Benefits for Future Stages

### For Developers

✅ **Clear guidance**: No ambiguity on which tool to use
✅ **Copy-paste templates**: Get started in seconds
✅ **Consistent structure**: All stages follow same pattern
✅ **Automated feedback**: Know immediately if coverage dropped

### For Agents

✅ **Enforceable rules**: Clear gates, no subjective decisions
✅ **Automated monitoring**: Alerts created automatically
✅ **Standardized reports**: Same format every stage
✅ **No context loss**: Rules always in CLAUDE.md

### For Project

✅ **Quality consistency**: Every stage meets same standards
✅ **Faster development**: Less time deciding, more time coding
✅ **Easier maintenance**: Predictable test structure
✅ **Production confidence**: Every stage validated the same way

---

## Example: Stage 2 Will Follow This Process

### Phase 1 (Planning)

**PM-Architect** reads CLAUDE.md → sees Testing Standards section → creates test plan:

```json
{
  "stage": 2,
  "coverage_target": 60,
  "test_counts": {
    "unit": 132,
    "integration": 44,
    "component": 22,
    "e2e": 22
  },
  "test_scenarios": [
    {
      "scenario": "User uploads PDF, retrieves RAG answer with citations",
      "test_type": "e2e",
      "priority": "critical"
    }
  ]
}
```

### Phase 2 (Development)

**Backend-Agent** writes:
- Unit tests for RAG service (co-located: `lightrag_service.test.py`)
- Integration tests for document pipeline (pytest)

**Frontend-Agent** writes:
- Unit tests for citation rendering (co-located: `citations.test.ts`)
- Integration tests for document upload API (MSW)

### Phase 3 (Review)

**QA-Agent** automatically:
1. Runs: `npm run test && npm run test:e2e && npm run test:visual`
2. Checks coverage: 62% ✅ (threshold: 60%)
3. Validates pyramid: 60% unit, 20% integration, 10% component, 10% E2E ✅
4. Checks performance: LCP 2.1s ✅
5. Creates review report: "APPROVE - Stage 2 ready for integration testing"

### Phase 4 (Integration Testing)

**QA-Agent** runs:
- All E2E tests (RAG pipeline end-to-end)
- Visual regression (citation display)
- Performance tests (document processing speed)

### Phase 5 (Manual Approval)

**User** manually tests:
- Upload 3 different PDFs
- Ask 5 RAG questions
- Verify citations link to correct pages
- Approve Stage 2 ✅

**PM-Architect** creates git checkpoint: `stage-2-complete`

---

## Files Created Summary

| File | Lines | Purpose | Audience |
|------|-------|---------|----------|
| `docs/TESTING-STANDARDS.md` | 900+ | Developer guide | All developers, agents |
| `.claude-bus/standards/TESTING-RULES.md` | 600+ | Agent enforcement rules | PM-Architect, QA, agents |
| `CLAUDE.md` (updated) | +65 | Quick reference | All agents (auto-loaded) |
| **TOTAL** | **1,565+** | **Complete testing framework** | **All stakeholders** |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-24 | Initial creation based on Stage 1 MCP-Enhanced Hybrid approach |

---

## Next Steps

### Immediate

✅ **Testing standards codified** - All future stages will automatically follow MCP-Enhanced Hybrid approach
✅ **No manual reminders needed** - Baked into CLAUDE.md, auto-loaded by agents
✅ **Automated enforcement** - QA-Agent enforces gates via `.claude-bus/config/auto-monitoring.json`

### Stage 1 Refactoring (Optional - when user approves)

If user approves, proceed with Stage 1 refactoring execution:
- Day 1: API client refactoring (base.ts, projects.ts, conversations.ts)
- Day 2: Complete API refactoring + CSRF implementation
- Day 3: CSRF integration + Vitest unit tests setup
- Day 4: Write 107 unit tests
- Day 5: Integration tests + Playwright component tests
- Day 6: Visual regression + performance tests + final validation

**Total**: 140 tests, 52% coverage, 6 days (32-38 hours)

### Stage 2 Planning (Future)

When Stage 2 begins:
1. PM-Architect reads CLAUDE.md → automatically follows testing standards
2. Creates test plan with 60% coverage target (220 total tests)
3. QA-Agent enforces same gates (coverage, pyramid, performance)
4. Same MCP-Enhanced Hybrid approach (Vitest + Playwright + Chrome DevTools)

**No additional setup needed** - framework already in place.

---

## Success Criteria

✅ **ACHIEVED**: Testing approach codified for all future stages
✅ **ACHIEVED**: Clear documentation for developers and agents
✅ **ACHIEVED**: Automated enforcement via quality gates
✅ **ACHIEVED**: Integrated into CLAUDE.md (auto-loaded)
✅ **ACHIEVED**: Stage 2-6 will automatically follow same approach

**User request fulfilled**: "Can you ensure we follow the similiar appraoch when comes to test in the future???" - **YES, DONE!**

---

## Recommendations

### For User

1. **Review the docs**: Read `docs/TESTING-STANDARDS.md` to understand the full approach
2. **Approve refactoring** (optional): If ready, say "GO" to start Stage 1 refactoring execution
3. **Stage 2 planning**: When ready for Stage 2, testing framework is already in place

### For Future Agents

1. **Always read CLAUDE.md first** - Testing standards are there
2. **Follow the templates** - Copy-paste from TESTING-STANDARDS.md
3. **Enforce the gates** - QA-Agent blocks non-compliant code
4. **Report violations** - Create CRITICAL alerts for coverage/pyramid issues

---

**Report Generated**: 2025-11-24
**Generated By**: PM-Architect-Agent
**Status**: ✅ COMPLETE
**User Request**: FULFILLED

All future stages (2-6) will automatically follow the MCP-Enhanced Hybrid testing approach established in Stage 1.
