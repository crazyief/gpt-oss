# Playwright E2E Testing Guide

## Overview

This document provides guidance for writing and running Playwright E2E tests for GPT-OSS frontend development.

**Why Playwright?**
- Browser-based testing catches SSR bugs that API-only tests miss
- Multi-browser support (Chromium, Firefox, Safari)
- Auto-waiting reduces flaky tests
- Rich debugging tools (screenshots, videos, traces)
- Fast parallel execution

## Quick Start

### Running Tests

```bash
# Run all E2E tests (headless)
npm run test:e2e

# Run with UI mode (interactive)
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed

# Run only Chromium tests
npm run test:e2e:chromium

# Debug mode (step through tests)
npm run test:e2e:debug

# View HTML test report
npm run test:report
```

### Running Tests Against Docker

**IMPORTANT**: Tests run against `http://localhost:5173`, so the frontend must be running:

```powershell
# Start all services including frontend
docker-compose up -d

# Wait for frontend to be ready
# Then run tests
cd frontend
npm run test:e2e
```

## Test Organization

```
frontend/
├── tests/
│   └── e2e/
│       ├── 01-ssr-rendering.spec.ts     # SSR bug detection
│       ├── 02-user-workflow.spec.ts     # User journey tests
│       └── 03-navigation.spec.ts        # Navigation & keyboard
├── test-results/                        # Test artifacts
│   ├── *.png                            # Screenshots on failure
│   └── *.webm                           # Videos on failure
└── playwright-report/                   # HTML report
```

## Writing New Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: navigate to page
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should do something specific', async ({ page }) => {
    // Arrange
    const button = page.locator('button:has-text("Click Me")');

    // Act
    await button.click();

    // Assert
    await expect(page.locator('text=Success')).toBeVisible();
  });
});
```

### SSR Testing Pattern

**CRITICAL**: Always test SSR rendering to catch `window is not defined` bugs:

```typescript
test('component renders without SSR errors', async ({ page }) => {
  // Capture console errors
  const consoleErrors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  // Capture page errors
  const pageErrors: string[] = [];
  page.on('pageerror', (error) => {
    pageErrors.push(error.message);
  });

  // Navigate
  const response = await page.goto('/your-route');

  // Assert: No SSR crashes
  expect(response?.status()).toBe(200);
  expect(consoleErrors).toEqual([]);
  expect(pageErrors).toEqual([]);
});
```

### User Workflow Pattern

Test complete user journeys, not just individual components:

```typescript
test('complete user flow: create project → add document → chat', async ({ page }) => {
  // Step 1: Create project
  await page.locator('button:has-text("New Project")').click();
  await page.locator('input[name="name"]').fill('Test Project');
  await page.locator('button[type="submit"]').click();
  await expect(page.locator('text=Test Project')).toBeVisible();

  // Step 2: Upload document
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('./test-fixtures/sample.pdf');
  await expect(page.locator('text=sample.pdf')).toBeVisible();

  // Step 3: Send chat message
  await page.locator('textarea[placeholder*="message"]').fill('What is this document about?');
  await page.keyboard.press('Enter');
  await expect(page.locator('.message').last()).toContainText('This document');
});
```

### Keyboard Navigation Pattern

Ensure accessibility:

```typescript
test('keyboard navigation works', async ({ page }) => {
  await page.goto('/');

  // Tab through interactive elements
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');

  // Verify focus
  const focused = page.locator(':focus');
  await expect(focused).toBeVisible();

  // Test keyboard shortcuts
  await page.keyboard.press('Control+K'); // Search
  await expect(page.locator('input[type="search"]')).toBeFocused();
});
```

## Locator Best Practices

### Recommended Selectors (in order of preference)

1. **Test IDs** (best for stability):
   ```typescript
   page.locator('[data-testid="project-list"]')
   ```

2. **Role + Name** (best for accessibility):
   ```typescript
   page.locator('role=button[name="Create Project"]')
   ```

3. **Text Content** (good for unique text):
   ```typescript
   page.locator('button:has-text("New Project")')
   ```

4. **CSS Selectors** (last resort, brittle):
   ```typescript
   page.locator('.project-card button.create')
   ```

### Avoid These Patterns

❌ **Don't use fragile selectors**:
```typescript
// BAD: Breaks if class names change
page.locator('.btn-primary.text-lg.px-4.py-2')

// GOOD: Use semantic attributes
page.locator('button[aria-label="Create Project"]')
```

❌ **Don't hardcode delays**:
```typescript
// BAD: Race conditions
await page.click('button');
await page.waitForTimeout(3000);

// GOOD: Wait for specific condition
await page.click('button');
await expect(page.locator('.success-message')).toBeVisible();
```

## Debugging Failed Tests

### 1. View Screenshots

Failed tests automatically capture screenshots:

```bash
# Check test-results/ directory
ls test-results/*.png
```

### 2. View Videos

Videos are recorded for failed tests:

```bash
# Check test-results/ directory for .webm files
ls test-results/*.webm
```

### 3. View HTML Report

```bash
npm run test:report
# Opens http://localhost:9323 with interactive report
```

### 4. Run in Debug Mode

```bash
npm run test:e2e:debug
# Opens Playwright Inspector for step-by-step debugging
```

### 5. Run in Headed Mode

```bash
npm run test:e2e:headed
# See the browser window as tests run
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: |
          cd frontend
          npm ci
          npx playwright install --with-deps

      - name: Start Docker services
        run: docker-compose up -d

      - name: Wait for frontend
        run: npx wait-on http://localhost:5173 --timeout 60000

      - name: Run Playwright tests
        run: |
          cd frontend
          npm run test:e2e

      - name: Upload artifacts
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/test-results/
          retention-days: 30
```

## Test Coverage Guidelines

### Stage 2 Testing Checklist

When adding new features in Stage 2, ensure you have:

- [ ] **SSR Rendering Test**: Verify no `window`/`document` errors during SSR
- [ ] **User Workflow Test**: Test complete end-to-end user journey
- [ ] **Navigation Test**: Verify routing and page transitions
- [ ] **Keyboard Navigation**: Test tab navigation and shortcuts
- [ ] **Mobile Viewport**: Test on mobile screen sizes
- [ ] **Error Handling**: Test error states and validation
- [ ] **Loading States**: Test skeleton screens and spinners
- [ ] **Real-Time Updates**: Test SSE/WebSocket streaming

### Critical Test Categories

1. **SSR Rendering** (100% required)
   - All routes must load without SSR errors
   - All components must handle browser-only APIs correctly

2. **Core User Workflows** (80% coverage target)
   - Project creation
   - Document upload
   - Chat interaction
   - Knowledge graph viewing

3. **Accessibility** (WCAG 2.1 AA compliance)
   - Keyboard navigation
   - Screen reader compatibility
   - Focus management

4. **Cross-Browser** (Chromium + Firefox minimum)
   - Desktop Chrome/Edge
   - Desktop Firefox
   - Mobile Safari (iPhone)
   - Mobile Chrome (Android)

## Performance Testing

### Measuring Page Load Time

```typescript
test('homepage loads within 3 seconds', async ({ page }) => {
  const startTime = Date.now();
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  const loadTime = Date.now() - startTime;

  expect(loadTime).toBeLessThan(3000);
});
```

### Measuring SSE Streaming Performance

```typescript
test('chat response streams within 2 seconds', async ({ page }) => {
  await page.goto('/project/1');

  const messageInput = page.locator('textarea[placeholder*="message"]');
  await messageInput.fill('Test query');

  const startTime = Date.now();
  await page.keyboard.press('Enter');

  // Wait for first token to appear
  await expect(page.locator('.message').last()).toContainText(/\w+/);
  const firstTokenTime = Date.now() - startTime;

  expect(firstTokenTime).toBeLessThan(2000);
});
```

## Common Pitfalls

### 1. Forgetting to Check Browser Context

❌ **Wrong**:
```typescript
onMount(() => {
  window.addEventListener('keydown', handler);  // SSR crash!
});
```

✅ **Correct**:
```typescript
import { browser } from '$app/environment';

onMount(() => {
  if (browser) {
    window.addEventListener('keydown', handler);
  }
});
```

### 2. Not Waiting for Network Requests

❌ **Wrong**:
```typescript
await page.click('button');
expect(page.locator('.result')).toBeVisible();  // Might fail!
```

✅ **Correct**:
```typescript
await page.click('button');
await expect(page.locator('.result')).toBeVisible({ timeout: 10000 });
```

### 3. Using Fragile Selectors

❌ **Wrong**:
```typescript
page.locator('div > div > button:nth-child(3)')  // Breaks easily!
```

✅ **Correct**:
```typescript
page.locator('button[aria-label="Create Project"]')  // Semantic!
```

## Stage 2 Recommendations

### New Test Files to Create

1. **Document Processing Tests** (`04-document-processing.spec.ts`)
   - Upload various file formats
   - Verify parsing and chunking
   - Test OCR for scanned PDFs

2. **Knowledge Graph Tests** (`05-knowledge-graph.spec.ts`)
   - Verify graph visualization renders
   - Test entity highlighting
   - Test relationship navigation

3. **Standards Compliance Tests** (`06-standards.spec.ts`)
   - Test IEC 62443 queries
   - Test cross-standard comparisons
   - Verify citation accuracy

4. **Advanced Search Tests** (`07-search.spec.ts`)
   - Test semantic search
   - Test filters and facets
   - Test search result ranking

### Performance Benchmarks

Set baseline performance targets:

- **Page Load**: < 3 seconds (networkidle)
- **First Contentful Paint**: < 1.5 seconds
- **Time to Interactive**: < 5 seconds
- **First Token (SSE)**: < 2 seconds
- **Full Response (SSE)**: < 10 seconds

### Browser Matrix for Stage 2

| Browser | Version | Priority |
|---------|---------|----------|
| Chrome | Latest | High |
| Firefox | Latest | High |
| Safari | Latest | Medium |
| Edge | Latest | Medium |
| Mobile Safari | iOS 15+ | Medium |
| Mobile Chrome | Latest | Medium |

## Resources

- **Playwright Docs**: https://playwright.dev/docs/intro
- **Best Practices**: https://playwright.dev/docs/best-practices
- **Debugging Guide**: https://playwright.dev/docs/debug
- **CI/CD Examples**: https://playwright.dev/docs/ci

## Proof of Value

**The SSR bug we fixed would have been caught by these tests BEFORE deployment:**

```typescript
// This test failed when window bug existed:
test('homepage loads without SSR errors', async ({ page }) => {
  const response = await page.goto('/');
  expect(response?.status()).toBe(200);  // ❌ Got 500 before fix, ✅ 200 after
});

// This test specifically caught the window error:
test('window-dependent code only runs in browser', async ({ page }) => {
  const windowErrors: string[] = [];
  page.on('pageerror', (error) => {
    if (error.message.includes('window is not defined')) {
      windowErrors.push(error.message);
    }
  });

  await page.goto('/');
  expect(windowErrors.length).toBe(0);  // ❌ Failed before fix, ✅ Passes now
});
```

**Lesson**: Browser-based E2E tests catch runtime bugs that API-only tests and build checks miss.
