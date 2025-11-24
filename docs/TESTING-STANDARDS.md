# GPT-OSS Testing Standards

**Version**: 1.0
**Effective Date**: 2025-11-24
**Status**: MANDATORY for all development stages
**Authority**: Established by PM-Architect-Agent, approved by user

---

## Executive Summary

This document defines the **MCP-Enhanced Hybrid Testing Approach** as the official testing standard for the GPT-OSS project. All stages (Stage 1-6) MUST follow these guidelines to ensure consistent quality, maintainability, and production readiness.

**Key Principle**: Use the right tool for each testing layer - fast unit tests for logic, browser automation for UI, visual regression for appearance, and performance tests for Core Web Vitals.

---

## Testing Strategy Overview

### MCP-Enhanced Hybrid Approach

The GPT-OSS testing strategy combines:
- **Vitest** for fast unit and integration tests
- **Mock Service Worker (MSW)** for realistic API mocking
- **Playwright MCP** for component and E2E browser tests
- **Chrome DevTools MCP** for visual regression and performance validation

**Why this approach?**
- **Speed**: Vitest provides instant feedback (unit tests run in <5 seconds)
- **Realism**: Playwright MCP tests in real browsers with real user interactions
- **Quality**: Chrome DevTools MCP catches visual regressions and performance degradation
- **Efficiency**: 5-minute full test suite vs 30+ minutes with browser-only testing

---

## Testing Pyramid

All stages MUST follow this testing pyramid structure:

```
           /\
          /  \  E2E Tests (10%)
         /    \  ← Playwright MCP
        /------\
       / Comp. \  Component Tests (10%)
      /  Tests  \  ← Playwright MCP
     /----------\
    / Integration\  Integration Tests (20%)
   /    Tests     \  ← Vitest + MSW
  /--------------\
 /   Unit Tests   \  Unit Tests (60%)
/                  \  ← Vitest
--------------------
```

**Distribution Requirements**:
- **Unit Tests**: 60% of total tests (Vitest, <50 lines per test)
- **Integration Tests**: 20% of total tests (Vitest + MSW, multi-module workflows)
- **Component Tests**: 10% of total tests (Playwright MCP, isolated components)
- **E2E Tests**: 10% of total tests (Playwright MCP, full user flows)

**Additional Quality Layers**:
- **Visual Regression**: 3-5 critical UI states (Chrome DevTools MCP)
- **Performance Tests**: 2-3 key user journeys (Chrome DevTools MCP, Core Web Vitals)

---

## Tool Selection Guide

### Decision Tree

```
Start: What are you testing?
│
├─ Pure JavaScript logic (no DOM, no network)?
│  └─ Use: Vitest unit test
│
├─ Multiple modules with API calls?
│  └─ Use: Vitest integration test + MSW for API mocking
│
├─ Svelte component behavior (clicks, inputs, state)?
│  └─ Use: Playwright MCP component test
│
├─ Full user workflow (login → upload → chat)?
│  └─ Use: Playwright MCP E2E test
│
├─ UI appearance (layout, colors, spacing)?
│  └─ Use: Chrome DevTools MCP visual regression test
│
└─ Page speed (load time, interaction latency)?
   └─ Use: Chrome DevTools MCP performance test
```

### Vitest (Unit Tests)

**Use for**:
- Pure functions (utilities, helpers, formatters)
- Business logic (validation, calculation, transformation)
- Store logic (Svelte stores, state management)
- Single-module functionality

**Example**:
```typescript
// src/lib/utils/date.test.ts
import { describe, it, expect } from 'vitest';
import { formatTimestamp, isToday } from './date';

describe('formatTimestamp', () => {
  it('should format UTC timestamp in GMT+8', () => {
    const timestamp = '2025-11-24T06:30:00Z'; // UTC
    const result = formatTimestamp(timestamp);
    expect(result).toBe('2025-11-24 14:30:00'); // GMT+8
  });
});
```

**Requirements**:
- Test file naming: `*.test.ts` or `*.spec.ts`
- Coverage: ≥80% for utility modules
- Speed: Each test suite < 100ms
- Max nesting: 3 levels (describe → describe → it)

### Vitest + MSW (Integration Tests)

**Use for**:
- Multi-module workflows (API client + store + component logic)
- Network request/response handling
- Error handling across layers
- CSRF token flow

**Example**:
```typescript
// src/lib/services/api-client.integration.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { createProject, getProjects } from './projects';

const server = setupServer(
  http.post('/api/projects/create', async () => {
    return HttpResponse.json({
      id: 1,
      name: 'Test Project'
    }, { status: 201 });
  })
);

beforeAll(() => server.listen());
afterAll(() => server.close());

describe('Project API Integration', () => {
  it('should create project and update store', async () => {
    const project = await createProject('Test Project');
    expect(project.id).toBe(1);
    expect(project.name).toBe('Test Project');
  });
});
```

**Requirements**:
- File naming: `*.integration.test.ts`
- Coverage: ≥60% for service modules
- Speed: Each test suite < 500ms
- MSW handlers: Reset between tests

### Playwright MCP (Component Tests)

**Use for**:
- Svelte component interactions (clicks, inputs, form submissions)
- Component state changes (loading, error, success states)
- DOM manipulation (show/hide, add/remove elements)
- Accessibility validation (keyboard navigation, ARIA labels)

**Example**:
```typescript
// tests/component/ChatInput.spec.ts
import { test, expect } from '@playwright/test';

test('ChatInput - submit on Enter key', async ({ page }) => {
  await page.goto('http://localhost:5173/test/chat-input');

  // Type message
  await page.locator('textarea[name="message"]').fill('Hello world');

  // Press Enter
  await page.locator('textarea[name="message"]').press('Enter');

  // Verify message sent (mock intercepted)
  await expect(page.locator('.message-sent')).toBeVisible();
  await expect(page.locator('textarea[name="message"]')).toHaveValue('');
});
```

**Requirements**:
- File naming: `tests/component/*.spec.ts`
- Coverage: All interactive components
- Speed: Each test < 5 seconds
- Selectors: Prefer data-testid over CSS selectors
- Isolation: Each test starts with fresh page state

### Playwright MCP (E2E Tests)

**Use for**:
- Full user workflows (multi-page, multi-step)
- Real backend integration (using test database)
- File upload/download scenarios
- WebSocket/SSE streaming validation

**Example**:
```typescript
// tests/e2e/chat-workflow.spec.ts
import { test, expect } from '@playwright/test';

test('Complete chat workflow', async ({ page }) => {
  // 1. Create project
  await page.goto('http://localhost:5173');
  await page.locator('button:text("New Project")').click();
  await page.locator('input[name="project-name"]').fill('E2E Test');
  await page.locator('button:text("Create")').click();

  // 2. Upload document
  await page.locator('button:text("Upload Document")').click();
  await page.locator('input[type="file"]').setInputFiles('./test-data/sample.pdf');
  await expect(page.locator('.upload-success')).toBeVisible();

  // 3. Start chat
  await page.locator('textarea[name="message"]').fill('What is IEC 62443?');
  await page.locator('button:text("Send")').click();

  // 4. Verify streaming response
  await expect(page.locator('.assistant-message')).toBeVisible({ timeout: 10000 });
  const response = await page.locator('.assistant-message').textContent();
  expect(response).toContain('IEC 62443');
});
```

**Requirements**:
- File naming: `tests/e2e/*.spec.ts`
- Coverage: All critical user journeys
- Speed: Each test < 30 seconds
- Database: Use test database, reset before each test
- Cleanup: Delete test data after test

### Chrome DevTools MCP (Visual Regression)

**Use for**:
- UI layout verification (spacing, alignment, responsiveness)
- Visual appearance (colors, fonts, borders)
- Cross-browser consistency
- Design system compliance

**Example**:
```typescript
// tests/visual/chat-interface.spec.ts
import { test, expect } from '@playwright/test';

test('Chat interface - empty state', async ({ page }) => {
  await page.goto('http://localhost:5173/chat/new');

  // Wait for page to stabilize
  await page.waitForLoadState('networkidle');

  // Take screenshot
  const screenshot = await page.screenshot({
    fullPage: true,
    animations: 'disabled' // Prevent animation flicker
  });

  // Compare with baseline
  await expect(screenshot).toMatchSnapshot('chat-empty.png', {
    maxDiffPixels: 100,      // Allow 100 pixels difference
    threshold: 0.01          // 1% threshold
  });
});
```

**Requirements**:
- File naming: `tests/visual/*.spec.ts`
- Coverage: 3-5 critical UI states (empty, loading, error, success, populated)
- Speed: Each test < 10 seconds
- Baseline: Store baseline screenshots in `tests/visual/baselines/`
- Updates: Regenerate baselines on intentional design changes

### Chrome DevTools MCP (Performance Tests)

**Use for**:
- Page load speed (FCP, LCP)
- Interaction latency (FID, INP)
- Layout stability (CLS)
- Bundle size validation

**Example**:
```typescript
// tests/performance/core-web-vitals.spec.ts
import { test, expect } from '@playwright/test';

test('Chat interface - Core Web Vitals', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Measure Web Vitals
  const metrics = await page.evaluate(() => {
    const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    const paintData = performance.getEntriesByType('paint');

    const fcp = paintData.find(e => e.name === 'first-contentful-paint')?.startTime || 0;
    const lcp = 0; // TODO: Measure LCP via PerformanceObserver
    const cls = 0; // TODO: Measure CLS via PerformanceObserver

    return {
      FCP: fcp,
      LCP: lcp,
      CLS: cls,
      DOMContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart
    };
  });

  // Validate against thresholds
  expect(metrics.FCP).toBeLessThan(1800);  // 1.8s (good)
  expect(metrics.LCP).toBeLessThan(2500);  // 2.5s (good)
  expect(metrics.CLS).toBeLessThan(0.1);   // 0.1 (good)
  expect(metrics.DOMContentLoaded).toBeLessThan(1000); // 1s
});
```

**Requirements**:
- File naming: `tests/performance/*.spec.ts`
- Coverage: 2-3 key user journeys (initial load, navigation, chat interaction)
- Speed: Each test < 15 seconds
- Thresholds: Follow Core Web Vitals "Good" thresholds
- Network: Test with throttling (Fast 3G, Slow 4G)

---

## Coverage Requirements

### Overall Coverage Targets

**All stages require ≥ 70% coverage** (consistent quality standard, not progressive).

| Stage | Unit | Integration | Component | E2E | Overall | Total Tests |
|-------|------|-------------|-----------|-----|---------|-------------|
| Stage 1 | 56% | 14% | 7% | 7% | **70%** | **188** |
| Stage 2 | 56% | 14% | 7% | 7% | **70%** | **280** |
| Stage 3 | 56% | 14% | 7% | 7% | **70%** | **380** |
| Stage 4 | 56% | 14% | 7% | 7% | **70%** | **480** |
| Stage 5 | 56% | 14% | 7% | 7% | **70%** | **580** |
| Stage 6 | 56% | 14% | 7% | 7% | **70%** | **680** |

**Rationale**: Each stage is an individual deliverable with the same quality expectations. Progressive thresholds create inconsistent quality standards across stages.

### Module-Specific Requirements

- **Critical modules** (auth, payment, security): ≥90% coverage
- **Business logic**: ≥80% coverage
- **UI components**: ≥60% coverage
- **Utilities**: ≥80% coverage
- **Configuration**: ≥50% coverage

### Coverage Enforcement

```json
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      statements: 70,  // All stages minimum
      branches: 65,
      functions: 65,
      lines: 70,
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.config.ts',
        '**/*.d.ts'
      ]
    }
  }
});
```

**Enforcement Gates**:
- ❌ Build fails if coverage < target
- ⚠️ Warning if coverage decreased from previous commit
- ✅ Git commit allowed only if coverage ≥ target

---

## File Organization

### Directory Structure

```
D:\gpt-oss\
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── utils/
│   │   │   │   ├── date.ts
│   │   │   │   └── date.test.ts              # Unit tests (co-located)
│   │   │   ├── services/
│   │   │   │   ├── api/
│   │   │   │   │   ├── base.ts
│   │   │   │   │   ├── base.test.ts           # Unit tests
│   │   │   │   │   └── projects.integration.test.ts  # Integration tests
│   │   └── routes/
│   │       └── +page.svelte
│   ├── tests/
│   │   ├── component/
│   │   │   ├── ChatInput.spec.ts              # Playwright component tests
│   │   │   └── Sidebar.spec.ts
│   │   ├── e2e/
│   │   │   ├── chat-workflow.spec.ts          # Playwright E2E tests
│   │   │   └── document-upload.spec.ts
│   │   ├── visual/
│   │   │   ├── chat-interface.spec.ts         # Chrome DevTools visual
│   │   │   └── baselines/                     # Screenshot baselines
│   │   │       ├── chat-empty.png
│   │   │       └── chat-populated.png
│   │   ├── performance/
│   │   │   ├── core-web-vitals.spec.ts        # Chrome DevTools perf
│   │   │   └── bundle-size.spec.ts
│   │   └── setup/
│   │       ├── msw-handlers.ts                 # MSW mock handlers
│   │       └── test-utils.ts                   # Shared test utilities
│   ├── playwright.config.ts
│   └── vitest.config.ts
├── backend/
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── e2e/
└── docs/
    └── TESTING-STANDARDS.md                    # This file
```

### Naming Conventions

| Test Type | File Pattern | Location |
|-----------|-------------|----------|
| Unit | `*.test.ts` | Co-located with source |
| Integration | `*.integration.test.ts` | Co-located with source |
| Component | `*.spec.ts` | `tests/component/` |
| E2E | `*.spec.ts` | `tests/e2e/` |
| Visual | `*.spec.ts` | `tests/visual/` |
| Performance | `*.spec.ts` | `tests/performance/` |

---

## Quality Gates

### Pre-Commit Gates

All commits MUST pass:
1. ✅ All unit tests passing (Vitest < 5s)
2. ✅ TypeScript compilation succeeds (no errors)
3. ✅ Linting passes (ESLint, Prettier)
4. ✅ Coverage ≥ target threshold

### Pre-PR Gates

All pull requests MUST pass:
1. ✅ All tests passing (unit + integration + component + E2E)
2. ✅ Coverage ≥ target threshold
3. ✅ Visual regression tests passing (no unexpected diffs)
4. ✅ Performance tests passing (Core Web Vitals within thresholds)
5. ✅ All files ≤ 400 lines
6. ✅ No console.error() or console.warn() in production code
7. ✅ QA-Agent code review approval

### Pre-Production Gates

Before deploying to production:
1. ✅ All E2E tests passing in staging environment
2. ✅ Performance tests passing with real backend
3. ✅ Visual regression tests passing in all target browsers
4. ✅ Load testing passed (100 concurrent users)
5. ✅ Security scan passed (no HIGH/CRITICAL vulnerabilities)
6. ✅ User acceptance testing completed
7. ✅ PM-Architect-Agent final approval

---

## Test Templates

### Vitest Unit Test Template

```typescript
// src/lib/utils/example.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { functionUnderTest } from './example';

describe('functionUnderTest', () => {
  // Setup
  beforeEach(() => {
    // Initialize test state
  });

  // Teardown
  afterEach(() => {
    // Clean up test state
  });

  // Happy path
  it('should return expected value for valid input', () => {
    const result = functionUnderTest('valid input');
    expect(result).toBe('expected output');
  });

  // Edge cases
  it('should handle empty input', () => {
    const result = functionUnderTest('');
    expect(result).toBe('');
  });

  // Error cases
  it('should throw error for invalid input', () => {
    expect(() => functionUnderTest(null)).toThrow('Invalid input');
  });
});
```

### Vitest + MSW Integration Test Template

```typescript
// src/lib/services/example.integration.test.ts
import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { functionUnderTest } from './example';

const server = setupServer(
  http.get('/api/resource', () => {
    return HttpResponse.json({ data: 'mock data' });
  })
);

beforeAll(() => server.listen());
afterAll(() => server.close());
afterEach(() => server.resetHandlers());

describe('API Integration', () => {
  it('should fetch data from API', async () => {
    const result = await functionUnderTest();
    expect(result.data).toBe('mock data');
  });

  it('should handle API errors', async () => {
    server.use(
      http.get('/api/resource', () => {
        return HttpResponse.json({ error: 'Server error' }, { status: 500 });
      })
    );

    await expect(functionUnderTest()).rejects.toThrow('Server error');
  });
});
```

### Playwright Component Test Template

```typescript
// tests/component/Example.spec.ts
import { test, expect } from '@playwright/test';

test.describe('ComponentName', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/test/component-name');
  });

  test('should render with default props', async ({ page }) => {
    await expect(page.locator('[data-testid="component"]')).toBeVisible();
  });

  test('should handle user interaction', async ({ page }) => {
    await page.locator('[data-testid="button"]').click();
    await expect(page.locator('[data-testid="result"]')).toHaveText('Expected text');
  });

  test('should validate accessibility', async ({ page }) => {
    const button = page.locator('[data-testid="button"]');
    await expect(button).toHaveAttribute('aria-label');

    // Keyboard navigation
    await page.keyboard.press('Tab');
    await expect(button).toBeFocused();
  });
});
```

### Playwright E2E Test Template

```typescript
// tests/e2e/workflow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('User Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Clear database, create test data
    await page.goto('http://localhost:5173');
  });

  test.afterEach(async ({ page }) => {
    // Cleanup: Delete test data
  });

  test('should complete workflow successfully', async ({ page }) => {
    // Step 1: Navigate
    await page.goto('http://localhost:5173/workflow');

    // Step 2: Interact
    await page.locator('input[name="field"]').fill('value');
    await page.locator('button[type="submit"]').click();

    // Step 3: Verify
    await expect(page.locator('.success-message')).toBeVisible();
  });
});
```

---

## Performance Thresholds

### Core Web Vitals (Chrome DevTools)

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | 2.5s - 4.0s | > 4.0s |
| **FCP** (First Contentful Paint) | ≤ 1.8s | 1.8s - 3.0s | > 3.0s |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | 0.1 - 0.25 | > 0.25 |
| **FID** (First Input Delay) | ≤ 100ms | 100ms - 300ms | > 300ms |
| **INP** (Interaction to Next Paint) | ≤ 200ms | 200ms - 500ms | > 500ms |
| **TTFB** (Time to First Byte) | ≤ 800ms | 800ms - 1800ms | > 1800ms |

**Enforcement**:
- All pages MUST achieve "Good" on LCP, FCP, CLS
- Performance tests fail if any metric in "Poor" range
- Warning if any metric in "Needs Improvement" range

### Bundle Size Limits

| Bundle | Stage 1 | Stage 2 | Stage 3+ |
|--------|---------|---------|----------|
| **Client JS** (gzipped) | ≤ 60 KB | ≤ 80 KB | ≤ 100 KB |
| **Client CSS** (gzipped) | ≤ 15 KB | ≤ 20 KB | ≤ 25 KB |
| **Initial Load** (total) | ≤ 100 KB | ≤ 120 KB | ≤ 150 KB |

**Enforcement**:
- Build fails if bundle size exceeds limit
- Dynamic imports required for large dependencies (Prism.js, D3.js)

---

## Test Execution

### Local Development

```bash
# Run all unit tests (fast, watch mode)
npm run test:unit

# Run all tests once (CI mode)
npm run test

# Run integration tests
npm run test:integration

# Run component tests (Playwright)
npm run test:component

# Run E2E tests (Playwright)
npm run test:e2e

# Run visual regression tests
npm run test:visual

# Run performance tests
npm run test:performance

# Run all tests with coverage
npm run test:coverage
```

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:unit

      - name: Run integration tests
        run: npm run test:integration

      - name: Run component tests
        run: npm run test:component

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Run visual regression tests
        run: npm run test:visual

      - name: Run performance tests
        run: npm run test:performance

      - name: Check coverage
        run: npm run test:coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Maintenance

### Updating Baselines

When UI intentionally changes:

```bash
# Update all visual regression baselines
npm run test:visual -- --update-snapshots

# Update specific baseline
npm run test:visual -- --update-snapshots tests/visual/chat-interface.spec.ts
```

### Test Debugging

```bash
# Run tests in debug mode (Playwright)
npm run test:e2e -- --debug

# Run tests in headed mode (see browser)
npm run test:e2e -- --headed

# Run specific test file
npm run test:unit src/lib/utils/date.test.ts

# Run tests matching pattern
npm run test:unit -- --grep "formatTimestamp"
```

### Test Data Management

- **Test fixtures**: Store in `tests/fixtures/`
- **Mock data**: Store in `tests/mocks/`
- **Test database**: Use separate SQLite file (`data/test.db`)
- **Cleanup**: Reset database before each E2E test

---

## Anti-Patterns (DO NOT DO)

### ❌ Testing Implementation Details

```typescript
// BAD: Testing internal state
test('should set loading to true', async () => {
  const component = mount(ChatInput);
  expect(component.vm.loading).toBe(true);  // Implementation detail
});

// GOOD: Testing user-visible behavior
test('should show loading indicator', async ({ page }) => {
  await page.locator('button').click();
  await expect(page.locator('.loading-spinner')).toBeVisible();
});
```

### ❌ Flaky Tests

```typescript
// BAD: Time-dependent test
test('should update after 1 second', async () => {
  triggerUpdate();
  await new Promise(resolve => setTimeout(resolve, 1000));
  expect(value).toBe('updated');  // Flaky!
});

// GOOD: Wait for specific condition
test('should update when data loaded', async ({ page }) => {
  await page.locator('button').click();
  await expect(page.locator('.data')).toHaveText('updated', { timeout: 5000 });
});
```

### ❌ Overly Broad Selectors

```typescript
// BAD: Fragile CSS selector
await page.locator('div > div > span.text').click();

// GOOD: Semantic selector
await page.locator('[data-testid="submit-button"]').click();
```

### ❌ Testing Too Much in One Test

```typescript
// BAD: Mega test
test('should do everything', async ({ page }) => {
  // 100 lines of test code testing multiple features
});

// GOOD: Focused tests
test('should create project', async ({ page }) => {
  // 10 lines testing project creation only
});

test('should upload document', async ({ page }) => {
  // 10 lines testing document upload only
});
```

### ❌ Not Cleaning Up

```typescript
// BAD: Leaves test data in database
test('should create project', async ({ page }) => {
  await createProject('Test');
  // No cleanup!
});

// GOOD: Cleanup after test
test('should create project', async ({ page }) => {
  const projectId = await createProject('Test');
  // ... test logic ...
  await deleteProject(projectId);  // Cleanup
});
```

---

## Glossary

- **Unit Test**: Tests a single function or module in isolation
- **Integration Test**: Tests multiple modules working together
- **Component Test**: Tests a UI component in isolation (Playwright)
- **E2E Test**: Tests a complete user workflow from start to finish
- **Visual Regression**: Compares screenshots to detect UI changes
- **Performance Test**: Measures Core Web Vitals and page speed
- **MSW**: Mock Service Worker, network-level API mocking
- **Core Web Vitals**: Google's page experience metrics (LCP, FCP, CLS)
- **MCP**: Model Context Protocol, integration for Playwright and Chrome DevTools

---

## References

- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [MSW Documentation](https://mswjs.io/)
- [Core Web Vitals Guide](https://web.dev/vitals/)
- [Testing Library Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

---

**Document Owner**: PM-Architect-Agent
**Review Schedule**: Every stage completion
**Last Updated**: 2025-11-24 (Stage 1 completion)
