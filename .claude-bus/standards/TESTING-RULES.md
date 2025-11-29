# Testing Rules for GPT-OSS Agents

**Version**: 1.0
**Effective Date**: 2025-11-24
**Applies To**: All agents (PM-Architect, Backend, Frontend, Document-RAG, QA, Super-AI)
**Status**: MANDATORY - Non-negotiable enforcement

---

## Critical Rules (Automatic Enforcement)

### Rule 1: MCP-Enhanced Hybrid Approach

**REQUIREMENT**: All stages MUST use the MCP-Enhanced Hybrid testing approach.

**Implementation**:
- 60% unit tests (Vitest)
- 20% integration tests (Vitest + MSW)
- 10% component tests (Playwright MCP)
- 10% E2E tests (Playwright MCP)
- 3-5 visual regression tests (Chrome DevTools MCP)
- 2-3 performance tests (Chrome DevTools MCP)

**Enforcement**:
```json
{
  "rule_id": "test-001",
  "severity": "critical",
  "condition": "Phase 3 (Review) AND test coverage < target",
  "action": "BLOCK phase transition, create user alert"
}
```

**Violations**:
- ❌ Using only Vitest (missing browser testing)
- ❌ Using only Playwright (too slow, poor pyramid)
- ❌ Skipping visual regression tests
- ❌ Skipping performance tests
- ❌ Test pyramid inverted (more E2E than unit tests)

---

### Rule 2: Coverage Thresholds

**REQUIREMENT**: All stages MUST meet or exceed coverage thresholds.

**Coverage Threshold (All Stages)**:
All stages require **≥ 70% coverage** (consistent quality standard).

| Stage | Coverage | Total Tests | Rationale |
|-------|----------|-------------|-----------|
| All | ≥ 70% | Varies | Each stage is individual deliverable with same quality expectations |

**Enforcement**:
- Git commit BLOCKED if coverage < threshold
- Pull request BLOCKED if coverage decreased
- Phase 3 (Review) BLOCKED if coverage < threshold

**QA-Agent Responsibilities**:
1. Run `npm run test:coverage` during Phase 3
2. If coverage < threshold:
   - Create CRITICAL alert in `.claude-bus/notifications/user-alerts.jsonl`
   - BLOCK phase transition
   - List untested files/functions in review report
3. Verify coverage report includes all test types

**Example Alert**:
```json
{
  "id": "notify-coverage-001",
  "timestamp": "2025-11-24T10:00:00Z",
  "severity": "critical",
  "notification_type": "coverage_gate",
  "message": "🔴 CRITICAL: Test coverage 65% is below required threshold (70%)",
  "details": {
    "current_coverage": 65,
    "required_coverage": 70,
    "missing_coverage": 5,
    "untested_files": [
      "src/lib/services/api/messages.ts (50% coverage)",
      "src/lib/services/csrf.ts (60% coverage)"
    ]
  },
  "suggested_actions": [
    "Add 12 unit tests to messages.ts",
    "Add 8 unit tests to csrf.ts",
    "Run: npm run test:coverage to verify"
  ],
  "status": "active"
}
```

---

### Rule 3: File Size Limit (Tiered by File Type)

**REQUIREMENT**: Files MUST respect tiered line limits based on file type.

**Tiered File Size Limits** (Approved 2025-11-30):

| File Type | Limit | Rationale |
|-----------|-------|-----------|
| `*.svelte` | **500 lines** | Svelte SFCs bundle 3 concerns: script + template + style |
| `*.ts` / `*.js` | **400 lines** | Single concern (logic only) |
| `*.py` | **400 lines** | Single concern (logic only) |
| `*.test.ts` | **500 lines** | Test files include setup, fixtures, multiple scenarios |
| `*.css` / `*.scss` | **600 lines** | Style files can be long by nature |

**Why Tiered Limits?**
- Svelte Single-File Components (SFCs) are architecturally different from pure logic files
- A `.svelte` file contains script + HTML template + CSS styles (3 concerns vs 1)
- A 25% increase (400 → 500) for Svelte is proportional to the additional concerns
- This aligns with Vue.js community standards for similar SFC architecture

**Enforcement**:
- Phase 3 (QA Review) scans all changed files against their type-specific limits
- If file exceeds its limit:
  - Create HIGH alert
  - Require refactoring plan
  - BLOCK phase approval until fixed OR justified as technical debt

**QA-Agent Responsibilities**:
```bash
# Scan for oversized files (tiered limits)
check_file_size() {
  file="$1"
  lines=$(wc -l < "$file")

  case "$file" in
    *.svelte)     limit=500 ;;
    *.test.ts)    limit=500 ;;
    *.css|*.scss) limit=600 ;;
    *)            limit=400 ;;
  esac

  if [ $lines -gt $limit ]; then
    echo "❌ VIOLATION: $file ($lines lines) exceeds $limit-line limit"
  fi
}

find src -type f \( -name "*.ts" -o -name "*.svelte" -o -name "*.py" \) | while read file; do
  check_file_size "$file"
done
```

**Exceptions** (require PM-Architect approval):
- Files with 95%+ auto-generated code
- Third-party library integration code
- Files scheduled for refactoring in next phase

---

### Rule 4: Test Pyramid Compliance

**REQUIREMENT**: Test distribution MUST follow pyramid structure.

**Valid Distribution** (example for 140 tests):
- Unit: 84 tests (60%)
- Integration: 28 tests (20%)
- Component: 14 tests (10%)
- E2E: 14 tests (10%)

**Invalid Distribution** (inverted pyramid):
- Unit: 20 tests (14%)
- Integration: 20 tests (14%)
- Component: 40 tests (29%)
- E2E: 60 tests (43%) ❌ TOO MANY

**QA-Agent Enforcement**:
```typescript
// .claude-bus/scripts/validate-test-pyramid.ts
function validateTestPyramid(testCounts: TestCounts): ValidationResult {
  const total = testCounts.unit + testCounts.integration + testCounts.component + testCounts.e2e;

  const unitPercent = (testCounts.unit / total) * 100;
  const integrationPercent = (testCounts.integration / total) * 100;
  const componentPercent = (testCounts.component / total) * 100;
  const e2ePercent = (testCounts.e2e / total) * 100;

  if (unitPercent < 55 || unitPercent > 65) {
    return { valid: false, reason: `Unit tests ${unitPercent.toFixed(0)}% not in range 55-65%` };
  }

  if (integrationPercent < 15 || integrationPercent > 25) {
    return { valid: false, reason: `Integration tests ${integrationPercent.toFixed(0)}% not in range 15-25%` };
  }

  if (componentPercent < 5 || componentPercent > 15) {
    return { valid: false, reason: `Component tests ${componentPercent.toFixed(0)}% not in range 5-15%` };
  }

  if (e2ePercent < 5 || e2ePercent > 15) {
    return { valid: false, reason: `E2E tests ${e2ePercent.toFixed(0)}% not in range 5-15%` };
  }

  return { valid: true };
}
```

---

### Rule 5: Performance Thresholds

**REQUIREMENT**: All pages MUST achieve "Good" Core Web Vitals.

**Thresholds** (Chrome DevTools MCP):
- LCP (Largest Contentful Paint) ≤ 2.5s
- FCP (First Contentful Paint) ≤ 1.8s
- CLS (Cumulative Layout Shift) ≤ 0.1
- Bundle size (gzipped): ≤ 60 KB (Stage 1)

**QA-Agent Responsibilities**:
1. Run performance tests during Phase 4 (Integration Testing)
2. If any metric fails:
   - Create HIGH alert
   - Identify performance bottlenecks
   - Recommend optimizations (lazy loading, code splitting, caching)
3. BLOCK production deployment if LCP > 4.0s (Poor)

**Performance Test Template**:
```typescript
// tests/performance/core-web-vitals.spec.ts
test('Page load performance', async ({ page }) => {
  await page.goto('http://localhost:5173');

  const metrics = await page.evaluate(() => {
    const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    const paintData = performance.getEntriesByType('paint');
    return {
      FCP: paintData.find(e => e.name === 'first-contentful-paint')?.startTime || 0,
      DOMContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart
    };
  });

  expect(metrics.FCP).toBeLessThan(1800);  // MANDATORY
  expect(metrics.DOMContentLoaded).toBeLessThan(1000);  // RECOMMENDED
});
```

---

### Rule 6: Visual Regression

**REQUIREMENT**: All critical UI states MUST have visual regression tests.

**Critical UI States**:
1. Empty state (no data)
2. Loading state (spinner/skeleton)
3. Error state (error message)
4. Success state (data loaded)
5. Populated state (typical data)

**QA-Agent Responsibilities**:
1. Identify 3-5 critical UI states per stage
2. Create baseline screenshots during Phase 2
3. Run visual regression tests during Phase 3
4. If diff > 1% threshold:
   - Review diff manually
   - If intentional: Update baseline
   - If unintentional: Create BUG alert

**Visual Regression Test Template**:
```typescript
// tests/visual/chat-interface.spec.ts
test('Chat interface - empty state', async ({ page }) => {
  await page.goto('http://localhost:5173/chat/new');
  await page.waitForLoadState('networkidle');

  const screenshot = await page.screenshot({
    fullPage: true,
    animations: 'disabled'
  });

  await expect(screenshot).toMatchSnapshot('chat-empty.png', {
    maxDiffPixels: 100,
    threshold: 0.01
  });
});
```

---

### Rule 7: User Journey Testing (Feature Accessibility Verification)

**REQUIREMENT**: All features defined in requirements MUST be accessible from the UI.

**Problem This Solves**:
This rule was added after Stage 2 revealed a critical gap: components were created but never integrated into the UI. Users could not access:
- Create Project functionality (component existed, no UI trigger)
- Document upload (component existed, not rendered in layout)
- Document download/delete (components existed, not visible)

Code quality tests passed, but features were invisible to users.

**Feature Accessibility Checklist**:
For EVERY feature in the stage requirements, verify:
1. ✅ **UI Entry Point Exists**: Button, link, or menu item to access the feature
2. ✅ **Entry Point is Visible**: Not hidden by CSS, not behind unreachable state
3. ✅ **Entry Point is Labeled**: Clear text or icon indicating the action
4. ✅ **User Can Complete the Flow**: Start-to-finish journey works
5. ✅ **Feedback is Provided**: Success/error states are visible

**QA-Agent Responsibilities**:
1. **Extract Feature List**: Read requirements file, list ALL user-facing features
2. **Map Features to UI**: For each feature, identify the UI entry point
3. **Manual Navigation Test**: Attempt to access each feature as a user would
4. **Create E2E Test**: Write Playwright test for each user journey
5. **Report Missing UI**: Create CRITICAL alert for features without UI access

**User Journey Test Template**:
```typescript
// tests/e2e/feature-accessibility.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Feature Accessibility Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:35173');
    await page.waitForLoadState('networkidle');
  });

  // Stage 2 Feature: Create Project
  test('User can access Create Project feature', async ({ page }) => {
    // 1. UI entry point exists and is visible
    const createButton = page.locator('[data-testid="create-project-btn"], button:has-text("Create Project"), button:has-text("New Project")');
    await expect(createButton).toBeVisible({ timeout: 5000 });

    // 2. User can trigger the feature
    await createButton.click();

    // 3. Feature UI appears (modal, form, etc.)
    const projectForm = page.locator('[data-testid="project-form"], .project-modal, input[name="project-name"]');
    await expect(projectForm).toBeVisible({ timeout: 3000 });
  });

  // Stage 2 Feature: Upload Document
  test('User can access Document Upload feature', async ({ page }) => {
    // Navigate to a project first
    const projectSelector = page.locator('.project-select');
    await expect(projectSelector).toBeVisible();

    // 1. UI entry point exists
    const uploadButton = page.locator('[data-testid="upload-btn"], button:has-text("Upload"), .upload-trigger');
    await expect(uploadButton).toBeVisible({ timeout: 5000 });

    // 2. User can trigger upload
    await uploadButton.click();

    // 3. Upload interface appears
    const uploadArea = page.locator('[data-testid="upload-area"], input[type="file"], .upload-dropzone');
    await expect(uploadArea).toBeVisible({ timeout: 3000 });
  });
});
```

**Feature Accessibility Report Template**:
```markdown
# Feature Accessibility Report - Stage {N}

## Requirements Checklist

| Feature | UI Entry Point | Visible | Test | Status |
|---------|---------------|---------|------|--------|
| Create Project | "New Project" button | YES | test-001 | ✅ PASS |
| Upload Document | "Upload" button | NO | - | ❌ FAIL |
| Delete Document | Context menu | NO | - | ❌ FAIL |

## Missing UI Entry Points (CRITICAL)

1. **Upload Document**
   - Component: `DocumentUpload.svelte` EXISTS
   - Problem: Not rendered in any layout
   - Fix: Add to project detail page or sidebar

2. **Delete Document**
   - Component: `DocumentActions.svelte` EXISTS
   - Problem: Component not imported in document list
   - Fix: Import and render in DocumentList.svelte
```

**Enforcement**:
```json
{
  "rule_id": "test-007",
  "severity": "critical",
  "trigger": "Phase 3 (Review) complete",
  "condition": "feature_without_ui_access > 0",
  "action": "BLOCK phase transition, create user alert",
  "notification": {
    "type": "user_alert",
    "message": "🔴 CRITICAL: {count} features have no UI access",
    "details": "Features exist in code but users cannot access them",
    "suggested_actions": [
      "Review Feature Accessibility Report",
      "Add UI entry points for missing features",
      "Run feature accessibility E2E tests"
    ]
  }
}
```

**Phase Gate Integration**:
- ❌ Phase 3 → Phase 4: BLOCKED if any feature lacks UI access
- ❌ Phase 4 → Phase 5: BLOCKED if feature accessibility tests fail
- ⚠️ Phase 2 → Phase 3: WARNING if no feature accessibility tests written

---

### Rule 8: Store Interface Synchronization

**REQUIREMENT**: Any store interface change MUST synchronize all dependent files.

**Problem This Solves**:
This rule was added after Stage 2 UI restructuring revealed a critical gap: the `documents` store was refactored from separate stores to a unified state pattern, but 15 unit tests still used the old interface, causing all tests to fail silently until QA review.

**Root Cause Analysis (Stage 2 Incident)**:
```
Old Interface (separate stores):
- documents: Writable<Document[]>
- documentsLoading: Writable<boolean>
- documentsError: Writable<string | null>

New Interface (unified state):
- documents: Writable<{ documents: Document[], isLoading: boolean, error: string | null }>

Impact: 15 tests failed because they accessed get(documents) expecting an array
```

**Store Change Checklist**:
When modifying ANY store interface, verify:
1. ✅ **Test files updated**: All `*.test.ts` files using the store
2. ✅ **Components updated**: All `.svelte` files subscribing to the store
3. ✅ **Services updated**: All service files importing the store
4. ✅ **TypeScript compiles**: No type errors after changes
5. ✅ **Tests pass**: Run `npm run test` before committing

**QA-Agent Responsibilities**:
1. **Detect store changes**: Check git diff for modifications to `stores/*.ts`
2. **Verify test synchronization**: For each modified store, verify corresponding `.test.ts` updated
3. **Run type check**: Execute `npm run type-check` to catch interface mismatches
4. **Create alert if mismatch**: If store changed but tests not updated, create CRITICAL alert

**Store Interface Documentation Requirement**:
All stores MUST include JSDoc interface documentation at the top:

```typescript
/**
 * Documents store
 *
 * @interface DocumentsState
 * @property {Document[]} documents - List of documents
 * @property {boolean} isLoading - Loading state
 * @property {string | null} error - Error message or null
 *
 * @example
 * // Accessing state
 * const state = get(documents);
 * console.log(state.documents.length);
 * console.log(state.isLoading);
 */
export const documents = writable<DocumentsState>({
  documents: [],
  isLoading: false,
  error: null
});
```

**Enforcement**:
```json
{
  "rule_id": "test-008",
  "severity": "critical",
  "trigger": "Phase 3 (Review) complete",
  "condition": "store_modified AND corresponding_test_not_modified",
  "action": "BLOCK phase transition, create user alert",
  "notification": {
    "type": "user_alert",
    "message": "🔴 CRITICAL: Store interface changed but tests not synchronized",
    "details": {
      "modified_stores": ["{list of modified store files}"],
      "unmodified_tests": ["{list of test files that should have been updated}"]
    },
    "suggested_actions": [
      "Update test files to use new store interface",
      "Run: npm run test to verify all tests pass",
      "Run: npm run type-check to verify TypeScript compiles"
    ]
  }
}
```

**Phase Gate Integration**:
- ❌ Phase 2 → Phase 3: BLOCKED if store changed without test update
- ❌ Phase 3 → Phase 4: BLOCKED if store interface tests failing
- ⚠️ All Phases: WARNING if store lacks JSDoc interface documentation

**Git Commit Validation**:
```bash
# Pre-commit hook script (add to .husky/pre-commit)
#!/bin/bash

# Check if any store files were modified
MODIFIED_STORES=$(git diff --cached --name-only | grep "stores/.*\.ts$" | grep -v "\.test\.ts$")

for store in $MODIFIED_STORES; do
  test_file="${store%.ts}.test.ts"
  if ! git diff --cached --name-only | grep -q "$test_file"; then
    echo "❌ ERROR: Store $store modified but $test_file not updated"
    echo "   Please update the test file to match new store interface"
    exit 1
  fi
done
```

---

## Agent-Specific Responsibilities

### PM-Architect-Agent

**Phase 1 (Planning)**:
- [ ] Define test scenarios for new features
- [ ] Estimate test count (target coverage threshold)
- [ ] Allocate testing time (30% of development time)
- [ ] Create `.claude-bus/planning/stages/stage{N}/test-plan.json`

**Phase 3 (Review)**:
- [ ] Review QA-Agent test results
- [ ] Approve OR request additional tests
- [ ] Verify coverage meets threshold
- [ ] Check test pyramid compliance

**Phase 4 (Integration Testing)**:
- [ ] Coordinate test execution across agents
- [ ] Monitor test failures
- [ ] Decide: proceed or return to Phase 2

**Phase 5 (Manual Approval)**:
- [ ] Run smoke tests manually
- [ ] Verify critical user journeys
- [ ] Approve stage completion

**Test Plan Template**:
```json
{
  "stage": 1,
  "coverage_target": 70,
  "test_counts": {
    "unit": 113,
    "integration": 38,
    "component": 19,
    "e2e": 18
  },
  "test_scenarios": [
    {
      "scenario": "User creates project and starts chat",
      "test_type": "e2e",
      "priority": "critical"
    }
  ],
  "performance_targets": {
    "LCP": 2500,
    "FCP": 1800,
    "CLS": 0.1
  }
}
```

---

### Frontend-Agent

**Phase 2 (Development)**:
- [ ] Write unit tests for all new functions (co-located)
- [ ] Write integration tests for API client modules
- [ ] Add `data-testid` attributes to interactive elements
- [ ] Ensure all files ≤ 400 lines

**Test Naming**:
- Unit: `*.test.ts` (co-located with source)
- Integration: `*.integration.test.ts` (co-located)
- Use descriptive test names: `should {expected behavior} when {condition}`

**Example**:
```typescript
// src/lib/services/api/projects.ts
export async function createProject(name: string): Promise<Project> {
  // Implementation
}

// src/lib/services/api/projects.test.ts
describe('createProject', () => {
  it('should create project with valid name', async () => {
    const project = await createProject('Test');
    expect(project.name).toBe('Test');
  });

  it('should throw error for empty name', async () => {
    await expect(createProject('')).rejects.toThrow('Name required');
  });
});
```

**Requirements**:
- All functions MUST have ≥1 unit test
- All API functions MUST have ≥1 integration test (MSW)
- All interactive components MUST have `data-testid`

---

### Backend-Agent

**Phase 2 (Development)**:
- [ ] Write unit tests for all services
- [ ] Write integration tests for all API endpoints
- [ ] Use pytest fixtures for test data
- [ ] Ensure all files ≤ 400 lines

**Test Structure**:
```python
# backend/tests/unit/test_llm_service.py
import pytest
from app.services.llm_service import LLMService

@pytest.fixture
def llm_service():
    return LLMService(model_name="test-model")

def test_generate_response_success(llm_service):
    response = llm_service.generate("Hello")
    assert response is not None
    assert len(response) > 0

def test_generate_response_empty_input(llm_service):
    with pytest.raises(ValueError, match="Input required"):
        llm_service.generate("")
```

**Requirements**:
- All services MUST have ≥80% coverage
- All endpoints MUST have ≥2 tests (success + error)
- All database operations MUST use test database

---

### QA-Agent

**Phase 3 (Review)**:
- [ ] Run all tests: `npm run test && cd backend && pytest`
- [ ] Generate coverage report
- [ ] Validate test pyramid compliance
- [ ] Run visual regression tests
- [ ] Run performance tests
- [ ] Create review report

**Review Report Template**:
```markdown
# QA Review Report - Stage {N}

**Date**: 2025-11-24
**Git Commit**: abc1234

## Test Results Summary

| Test Type | Passed | Failed | Total | Pass Rate |
|-----------|--------|--------|-------|-----------|
| Unit | 84 | 0 | 84 | 100% |
| Integration | 28 | 0 | 28 | 100% |
| Component | 14 | 0 | 14 | 100% |
| E2E | 14 | 0 | 14 | 100% |
| Visual | 5 | 0 | 5 | 100% |
| Performance | 3 | 0 | 3 | 100% |
| **TOTAL** | **148** | **0** | **148** | **100%** |

## Coverage Report

- Overall: 70% ✅ (threshold: 70%)
- Unit: 56%
- Integration: 14%
- Component: 7%
- E2E: 7%

## Test Pyramid Compliance

- Unit: 113 tests (60%) ✅ (target: 55-65%)
- Integration: 38 tests (20%) ✅ (target: 15-25%)
- Component: 19 tests (10%) ✅ (target: 5-15%)
- E2E: 18 tests (10%) ✅ (target: 5-15%)

**Verdict**: COMPLIANT ✅

## Performance Metrics

- LCP: 2.3s ✅ (threshold: 2.5s)
- FCP: 1.5s ✅ (threshold: 1.8s)
- CLS: 0.08 ✅ (threshold: 0.1)
- Bundle size: 58 KB ✅ (threshold: 60 KB)

**Verdict**: ALL GOOD ✅

## Visual Regression

All 5 screenshots matched baseline (0 diffs).

**Verdict**: PASS ✅

## Recommendations

None. All tests passing, coverage met, performance good.

## Approval Decision

✅ **APPROVE** - Stage {N} ready for integration testing.
```

**Enforcement Actions**:
```typescript
// If coverage < threshold
if (coverage < threshold) {
  createAlert({
    severity: "critical",
    message: `Coverage ${coverage}% below threshold ${threshold}%`,
    action: "BLOCK phase transition"
  });
}

// If test pyramid violated
if (!isValidPyramid(testCounts)) {
  createAlert({
    severity: "high",
    message: "Test pyramid inverted - too many E2E tests",
    action: "Refactor to add more unit tests"
  });
}

// If performance failed
if (metrics.LCP > 4000) {
  createAlert({
    severity: "critical",
    message: "LCP 4.2s exceeds 4.0s (Poor)",
    action: "BLOCK production deployment"
  });
}
```

---

### Super-AI-UltraThink-Agent

**Phase 1 (Planning Review)**:
- [ ] Review test plan created by PM-Architect
- [ ] Validate test scenarios cover all critical paths
- [ ] Suggest additional edge cases
- [ ] Approve OR request revisions

**Phase 3 (Code Review)**:
- [ ] Review test code quality
- [ ] Identify missing test cases
- [ ] Suggest refactoring for testability
- [ ] Validate test pyramid compliance

**Critical Evaluation Questions**:
1. Are all critical user journeys covered by E2E tests?
2. Are all error paths tested (network errors, validation errors)?
3. Are all edge cases covered (empty data, max data, special characters)?
4. Is the test pyramid balanced (not inverted)?
5. Are tests maintainable (no brittle selectors, no hard-coded delays)?
6. Are performance thresholds realistic and achievable?

---

## Tool Usage Rules

### When to Use Vitest

**ALWAYS use for**:
- Pure functions (utilities, helpers, formatters)
- Business logic (validation, calculation)
- Store logic (Svelte stores, state management)
- API client functions (with MSW for integration)

**NEVER use for**:
- Browser-specific features (DOM manipulation, WebSocket)
- Visual appearance (use Chrome DevTools MCP)
- User interactions (use Playwright MCP)

### When to Use Playwright MCP

**ALWAYS use for**:
- Component interactions (clicks, inputs, form submissions)
- User workflows (multi-step, multi-page)
- WebSocket/SSE streaming
- File upload/download

**NEVER use for**:
- Pure JavaScript logic (too slow, use Vitest)
- Visual appearance (use Chrome DevTools MCP)

### When to Use Chrome DevTools MCP

**ALWAYS use for**:
- Visual regression (layout, spacing, colors)
- Performance testing (Core Web Vitals)
- Screenshot comparison
- Network waterfall analysis

**NEVER use for**:
- Business logic testing (use Vitest)
- Functional testing (use Playwright MCP)

---

## Automated Monitoring Rules

### Rule AUTO-TEST-001: Coverage Gate

```json
{
  "rule_id": "auto-test-001",
  "severity": "critical",
  "trigger": "Phase 3 complete",
  "condition": "test_coverage < stage_threshold",
  "action": "BLOCK phase transition",
  "notification": {
    "type": "user_alert",
    "message": "Coverage {coverage}% below {threshold}%",
    "suggested_actions": [
      "Run: npm run test:coverage",
      "Identify untested files",
      "Add tests to reach threshold"
    ]
  }
}
```

### Rule AUTO-TEST-002: Test Pyramid Violation

```json
{
  "rule_id": "auto-test-002",
  "severity": "high",
  "trigger": "Phase 3 complete",
  "condition": "e2e_tests > unit_tests",
  "action": "Create alert, request refactoring",
  "notification": {
    "type": "user_alert",
    "message": "Test pyramid inverted: {e2e_count} E2E > {unit_count} unit",
    "suggested_actions": [
      "Convert E2E tests to integration tests where possible",
      "Add more unit tests for business logic"
    ]
  }
}
```

### Rule AUTO-TEST-003: Performance Degradation

```json
{
  "rule_id": "auto-test-003",
  "severity": "high",
  "trigger": "Phase 4 complete",
  "condition": "LCP > 2500 OR FCP > 1800 OR CLS > 0.1",
  "action": "Create alert, analyze bottlenecks",
  "notification": {
    "type": "user_alert",
    "message": "Performance degraded: LCP {lcp}ms exceeds 2500ms",
    "suggested_actions": [
      "Profile bundle size",
      "Check for render-blocking resources",
      "Add lazy loading for heavy components"
    ]
  }
}
```

### Rule AUTO-TEST-004: Visual Regression Detected

```json
{
  "rule_id": "auto-test-004",
  "severity": "medium",
  "trigger": "Phase 3 complete",
  "condition": "screenshot_diff > 1%",
  "action": "Manual review required",
  "notification": {
    "type": "user_alert",
    "message": "Visual diff detected in {screenshot_name}",
    "suggested_actions": [
      "Review diff image in tests/visual/__diff_output__/",
      "If intentional: npm run test:visual -- --update-snapshots",
      "If bug: Fix CSS/layout issue"
    ]
  }
}
```

### Rule AUTO-TEST-005: Feature Accessibility Violation

```json
{
  "rule_id": "auto-test-005",
  "severity": "critical",
  "trigger": "Phase 3 complete",
  "condition": "feature_count_in_requirements > feature_count_accessible_from_ui",
  "action": "BLOCK phase transition",
  "notification": {
    "type": "user_alert",
    "message": "🔴 CRITICAL: {missing_count} features have no UI access point",
    "details": {
      "total_features": "{total}",
      "accessible_features": "{accessible}",
      "missing_features": ["{list of feature names}"]
    },
    "suggested_actions": [
      "Review Feature Accessibility Report",
      "Add UI entry points (buttons, links, menu items) for missing features",
      "Verify components are imported and rendered in layouts",
      "Run: npm run test:e2e -- --grep 'Feature Accessibility'"
    ]
  }
}
```

---

## Phase Transition Gates

### Phase 2 → Phase 3

**Required**:
- ✅ Git checkpoint created
- ✅ All new code has co-located tests
- ✅ TypeScript compilation succeeds
- ✅ No console.error in production code

**QA-Agent verifies**:
```bash
# Check test files exist
find src -name "*.ts" | while read file; do
  test_file="${file%.ts}.test.ts"
  if [ ! -f "$test_file" ]; then
    echo "❌ Missing test: $test_file"
  fi
done

# Check TypeScript
npm run type-check

# Check for console.error
grep -r "console.error" src/ && echo "❌ Remove console.error"
```

### Phase 3 → Phase 4

**Required**:
- ✅ All tests passing (100%)
- ✅ Coverage ≥ threshold
- ✅ Test pyramid compliant
- ✅ All files ≤ 400 lines

**QA-Agent verifies**:
```bash
# Run all tests
npm run test
npm run test:integration
npm run test:component
npm run test:e2e

# Check coverage
npm run test:coverage | grep "All files" | awk '{print $10}' # Must be ≥ threshold

# Validate pyramid
node .claude-bus/scripts/validate-test-pyramid.ts
```

### Phase 4 → Phase 5

**Required**:
- ✅ All integration tests passing
- ✅ Visual regression tests passing
- ✅ Performance tests passing
- ✅ No CRITICAL/HIGH alerts

**QA-Agent verifies**:
```bash
# Run visual regression
npm run test:visual

# Run performance tests
npm run test:performance

# Check for critical alerts
jq '.severity == "critical"' .claude-bus/notifications/user-alerts.jsonl | grep true && echo "❌ Critical alerts found"
```

### Phase 5 → Stage Complete

**Required**:
- ✅ User manual testing completed
- ✅ All acceptance criteria met
- ✅ User explicit approval
- ✅ Final git checkpoint created

**PM-Architect verifies**:
- User provided explicit "APPROVE" statement
- Manual test checklist completed
- Git tag created: `stage-{N}-complete`

---

## Test Data Management

### Test Fixtures

**Location**: `tests/fixtures/`

**Structure**:
```
tests/fixtures/
├── projects.json          # Sample project data
├── conversations.json     # Sample conversation data
├── messages.json          # Sample message data
├── documents/
│   ├── sample.pdf         # Test PDF
│   └── sample.txt         # Test text file
└── mocks/
    ├── llm-responses.json  # Mock LLM responses
    └── api-responses.json  # Mock API responses
```

**Rules**:
- Use realistic data (not "test", "foo", "bar")
- Include edge cases (empty, max length, special characters)
- Version control fixtures (commit to git)
- Document fixture purpose in README

### Test Database

**SQLite**:
```bash
# Create test database
cp data/gpt_oss.db data/test.db

# Reset before each E2E test
beforeEach(async () => {
  await resetDatabase('data/test.db');
});
```

**PostgreSQL** (Stage 2+):
```bash
# Create test database
createdb gpt_oss_test

# Reset before each E2E test
beforeEach(async () => {
  await resetDatabase('gpt_oss_test');
});
```

---

## Enforcement Summary

| Rule | Severity | Gate | Action |
|------|----------|------|--------|
| Coverage < threshold | CRITICAL | Phase 3→4 | BLOCK transition |
| Pyramid violated | HIGH | Phase 3→4 | Request refactoring |
| Performance fail | HIGH | Phase 4→5 | Analyze + fix |
| Visual diff > 1% | MEDIUM | Phase 3→4 | Manual review |
| File > 400 lines | HIGH | Phase 3→4 | Refactor or justify |
| Test missing | MEDIUM | Phase 2→3 | Add tests |
| Feature without UI access | CRITICAL | Phase 3→4 | BLOCK transition |
| Store interface not synced | CRITICAL | Phase 2→3 | BLOCK transition |

---

## Quick Reference

### Test Commands

```bash
# Run all unit tests (watch mode)
npm run test:unit

# Run all tests once
npm run test

# Run integration tests
npm run test:integration

# Run component tests
npm run test:component

# Run E2E tests
npm run test:e2e

# Run visual regression
npm run test:visual

# Run performance tests
npm run test:performance

# Run all with coverage
npm run test:coverage
```

### Coverage Thresholds

| Stage | Threshold |
|-------|-----------|
| All | 70% |

**Consistent quality standard**: Every stage is treated equally as an individual deliverable.

### Performance Thresholds

| Metric | Good |
|--------|------|
| LCP | ≤ 2.5s |
| FCP | ≤ 1.8s |
| CLS | ≤ 0.1 |
| Bundle | ≤ 60 KB |

---

**Document Owner**: PM-Architect-Agent
**Enforcement**: Automated via `.claude-bus/config/auto-monitoring.json`
**Review Schedule**: Every stage completion
**Last Updated**: 2025-11-24 (Stage 1 completion)
