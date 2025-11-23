# Frontend Test Implementation Guide

**Generated**: 2025-11-23
**Purpose**: Actionable guide for implementing missing test cases identified in gap analysis

## Quick Start: What to Test First

### Week 1: Security & Stability (15 hours)

#### Day 1-2: Security Tests (5 hours)
```typescript
// tests/security/xss-prevention.spec.ts
import { test, expect } from '@playwright/test';

test.describe('XSS Prevention', () => {
  test('should sanitize script tags in markdown', async ({ page }) => {
    await page.goto('/');

    // Send malicious markdown
    const attacks = [
      '<script>alert("XSS")</script>',
      '[link](javascript:alert("XSS"))',
      '![](x" onerror="alert("XSS")',
      '<img src=x onerror=alert("XSS")>',
      '`<script>alert("XSS")</script>`'
    ];

    for (const attack of attacks) {
      await page.locator('[data-testid="message-input"]').fill(attack);
      await page.locator('[data-testid="send-button"]').click();

      // Verify no alerts triggered
      let alertTriggered = false;
      page.on('dialog', () => { alertTriggered = true; });
      await page.waitForTimeout(1000);
      expect(alertTriggered).toBe(false);

      // Verify content is sanitized in DOM
      const messageContent = await page.locator('.message-content').last().innerHTML();
      expect(messageContent).not.toContain('<script');
      expect(messageContent).not.toContain('javascript:');
      expect(messageContent).not.toContain('onerror');
    }
  });

  test('should prevent CSRF attacks', async ({ page }) => {
    // Verify CSRF token is present
    await page.goto('/');
    const token = await page.evaluate(() => {
      return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    });
    expect(token).toBeTruthy();

    // Attempt request without token
    const response = await page.evaluate(async () => {
      return await fetch('/api/chat/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: 'test' })
      }).then(r => r.status);
    });
    expect(response).toBe(403); // Should be forbidden
  });
});
```

#### Day 3-4: SSE Streaming Resilience (4 hours)
```typescript
// tests/streaming/network-resilience.spec.ts
import { test, expect } from '@playwright/test';

test.describe('SSE Streaming Resilience', () => {
  test('should handle network interruption during stream', async ({ page, context }) => {
    await page.goto('/');

    // Start a stream
    await page.locator('[data-testid="message-input"]').fill('Generate a long response');
    await page.locator('[data-testid="send-button"]').click();

    // Wait for stream to start
    await page.waitForSelector('.streaming-indicator');

    // Simulate network interruption
    await context.setOffline(true);
    await page.waitForTimeout(2000);

    // Restore network
    await context.setOffline(false);
    await page.waitForTimeout(2000);

    // Verify stream recovered or error shown
    const hasError = await page.locator('.stream-error').isVisible();
    const hasRetry = await page.locator('[data-testid="retry-button"]').isVisible();
    const streamCompleted = await page.locator('.message-complete').isVisible();

    expect(hasError || hasRetry || streamCompleted).toBe(true);
  });

  test('should handle stream cancellation', async ({ page }) => {
    await page.goto('/');

    // Start a stream
    await page.locator('[data-testid="message-input"]').fill('Generate response');
    await page.locator('[data-testid="send-button"]').click();

    // Wait for stream to start
    await page.waitForSelector('.streaming-indicator');

    // Cancel stream
    await page.locator('[data-testid="cancel-stream"]').click();

    // Verify stream stopped
    await expect(page.locator('.streaming-indicator')).not.toBeVisible();

    // Verify can send new message
    await page.locator('[data-testid="message-input"]').fill('New message');
    await page.locator('[data-testid="send-button"]').click();
    await expect(page.locator('.streaming-indicator')).toBeVisible();
  });
});
```

#### Day 5: Core Functionality (6 hours)
```typescript
// tests/core/token-limits.spec.ts
test('should enforce 22,800 token limit', async ({ page }) => {
  await page.goto('/');

  // Generate large message approaching limit
  const largeMessage = 'x'.repeat(20000);
  await page.locator('[data-testid="message-input"]').fill(largeMessage);
  await page.locator('[data-testid="send-button"]').click();

  // Add another message that would exceed
  await page.locator('[data-testid="message-input"]').fill(largeMessage);
  await page.locator('[data-testid="send-button"]').click();

  // Verify warning or prevention
  const warning = await page.locator('.token-limit-warning').isVisible();
  const blocked = await page.locator('[data-testid="send-button"]').isDisabled();
  expect(warning || blocked).toBe(true);
});

// tests/core/concurrent-messages.spec.ts
test('should handle concurrent message sending', async ({ page }) => {
  await page.goto('/');

  // Send first message
  await page.locator('[data-testid="message-input"]').fill('First message');
  const promise1 = page.locator('[data-testid="send-button"]').click();

  // Immediately send second
  await page.locator('[data-testid="message-input"]').fill('Second message');
  const promise2 = page.locator('[data-testid="send-button"]').click();

  await Promise.all([promise1, promise2]);

  // Verify both messages appear
  const messages = await page.locator('.user-message').count();
  expect(messages).toBeGreaterThanOrEqual(2);

  // Verify no duplicates
  const messageTexts = await page.locator('.user-message').allTextContents();
  const uniqueMessages = new Set(messageTexts);
  expect(uniqueMessages.size).toBe(messageTexts.length);
});
```

### Week 2-4: Extended Coverage (26 hours)

#### Browser Compatibility Suite
```typescript
// tests/compatibility/multi-tab.spec.ts
test('should sync between multiple tabs', async ({ browser }) => {
  const context = await browser.newContext();
  const page1 = await context.newPage();
  const page2 = await context.newPage();

  await page1.goto('/');
  await page2.goto('/');

  // Create conversation in tab 1
  await page1.locator('[data-testid="new-conversation"]').click();
  await page1.locator('input[name="title"]').fill('Multi-tab test');
  await page1.locator('button[type="submit"]').click();

  // Verify appears in tab 2 (may need refresh or WebSocket)
  await page2.reload();
  await expect(page2.locator('text=Multi-tab test')).toBeVisible();
});
```

#### Performance Testing
```typescript
// tests/performance/memory-leaks.spec.ts
test('should not leak memory over long sessions', async ({ page }) => {
  await page.goto('/');

  // Monitor memory
  const getMemory = () => page.evaluate(() => {
    if (performance.memory) {
      return performance.memory.usedJSHeapSize;
    }
    return 0;
  });

  const initialMemory = await getMemory();

  // Simulate long session
  for (let i = 0; i < 50; i++) {
    // Send message
    await page.locator('[data-testid="message-input"]').fill(`Message ${i}`);
    await page.locator('[data-testid="send-button"]').click();
    await page.waitForTimeout(100);

    // Switch conversations
    if (i % 10 === 0) {
      await page.locator('[data-testid="new-conversation"]').click();
    }
  }

  // Force garbage collection if available
  await page.evaluate(() => {
    if (window.gc) window.gc();
  });

  const finalMemory = await getMemory();
  const memoryGrowth = finalMemory - initialMemory;

  // Allow some growth but not excessive (e.g., <50MB)
  expect(memoryGrowth).toBeLessThan(50 * 1024 * 1024);
});
```

## Test Data Generators

```typescript
// tests/utils/test-data.ts
export function generateLargeConversation(messageCount = 100) {
  return Array.from({ length: messageCount }, (_, i) => ({
    role: i % 2 === 0 ? 'user' : 'assistant',
    content: `Test message ${i}: ${faker.lorem.paragraphs(3)}`,
    timestamp: new Date(Date.now() - (messageCount - i) * 60000).toISOString()
  }));
}

export function generateProjects(count = 10) {
  return Array.from({ length: count }, (_, i) => ({
    id: `project-${i}`,
    name: `Test Project ${i}`,
    description: faker.lorem.sentence(),
    created_at: faker.date.past().toISOString()
  }));
}

export function generateMaliciousInputs() {
  return [
    // XSS attempts
    '<script>alert("XSS")</script>',
    '"><script>alert("XSS")</script>',
    "';alert(String.fromCharCode(88,83,83))//",

    // SQL injection
    "'; DROP TABLE users; --",
    "1' OR '1' = '1",

    // Command injection
    "; ls -la",
    "| whoami",

    // Unicode edge cases
    "\u0000null byte",
    "\u202Eright-to-left override",
    "🔥📝✨ emoji overload 🚀💻🎉"
  ];
}
```

## Setting Up Test Infrastructure

### 1. Install Testing Dependencies
```bash
npm install -D vitest @testing-library/svelte @testing-library/user-event
npm install -D @vitest/ui happy-dom msw @faker-js/faker
npm install -D @axe-core/playwright lighthouse puppeteer
```

### 2. Configure Vitest
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte({ hot: !process.env.VITEST })],
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules', 'tests']
    }
  }
});
```

### 3. Create Test Setup
```typescript
// tests/setup.ts
import { beforeAll, afterAll, afterEach } from 'vitest';
import { setupServer } from 'msw/node';
import { handlers } from './mocks/handlers';

const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        test-type: [unit, integration, e2e, security, performance]

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Run ${{ matrix.test-type }} tests
        run: npm run test:${{ matrix.test-type }}

      - name: Upload coverage
        if: matrix.test-type == 'unit'
        uses: codecov/codecov-action@v3

      - name: Performance metrics
        if: matrix.test-type == 'performance'
        run: |
          npm run lighthouse
          npm run bundle-analyze
```

## Test Execution Commands

```json
// package.json
{
  "scripts": {
    "test": "npm run test:unit && npm run test:e2e",
    "test:unit": "vitest run",
    "test:unit:watch": "vitest",
    "test:unit:coverage": "vitest run --coverage",
    "test:e2e": "playwright test",
    "test:e2e:headed": "playwright test --headed",
    "test:security": "playwright test tests/security",
    "test:performance": "playwright test tests/performance",
    "test:a11y": "playwright test tests/accessibility",
    "test:all": "npm run test:unit && npm run test:e2e && npm run test:security",
    "test:ci": "npm run test:all -- --reporter=json"
  }
}
```

## Monitoring Production Issues

```typescript
// src/lib/monitoring/error-tracker.ts
export function setupErrorTracking() {
  // Sentry or similar
  window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    // Send to monitoring service
    trackError({
      message: event.message,
      source: event.filename,
      line: event.lineno,
      stack: event.error?.stack
    });
  });

  // Track unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled rejection:', event.reason);
    trackError({
      type: 'unhandledRejection',
      reason: event.reason
    });
  });
}
```

## Priority Matrix for Implementation

### Must Have (Week 1)
- [x] Security test suite (XSS, CSRF)
- [x] SSE streaming resilience
- [x] Token limit enforcement
- [x] Concurrent message handling
- [x] Basic memory leak detection

### Should Have (Week 2-4)
- [ ] Multi-tab synchronization
- [ ] Browser navigation tests
- [ ] Large dataset performance
- [ ] Code block functionality
- [ ] Stream cancellation
- [ ] Unit test framework setup

### Nice to Have (Month 2+)
- [ ] Full accessibility audit
- [ ] Visual regression tests
- [ ] Load testing suite
- [ ] Browser compatibility matrix
- [ ] Internationalization tests

## Success Metrics

Track these metrics weekly:
1. **Test Coverage**: Target 40% → 60% → 80%
2. **Bug Detection Rate**: >90% before production
3. **Test Execution Time**: <10 minutes for CI
4. **False Positive Rate**: <2% of runs
5. **Production Error Rate**: <0.1% of sessions

## Next Steps

1. **Today**: Implement TC-002 (XSS Prevention)
2. **Tomorrow**: Implement TC-001 (SSE Resilience)
3. **This Week**: Complete all Phase 1 critical tests
4. **Next Week**: Set up Vitest and begin unit tests
5. **Month 1**: Achieve 60% code coverage

---

*Remember: Test code is production code. Write it with the same care and attention to quality.*