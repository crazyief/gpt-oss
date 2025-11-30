# Real E2E Testing Plan

**Date**: 2025-11-29
**Status**: Technical Debt - High Priority
**Issue**: Current tests use mocked APIs, missing real integration bugs

---

## Problem Statement

Current Playwright tests mock all API endpoints:
```typescript
// Current approach - MOCKS everything
await page.route('**/api/conversations/create', async route => {
  await route.fulfill({ status: 201, body: JSON.stringify({ id: 1 }) });
});
```

**Bugs missed by mocked tests:**
1. CSRF token not sent with chat stream POST → 403 Forbidden
2. Frontend using PUT, backend expecting PATCH → 405 Method Not Allowed
3. Response structure mismatches (e.g., `{ projects: [] }` vs `[]`)

---

## Solution: Two-Tier E2E Testing

### Tier 1: Mocked E2E Tests (Current - Keep)
- **Purpose**: Fast UI behavior testing
- **Speed**: ~20 seconds for full suite
- **Use for**: Component interactions, UI state, accessibility

### Tier 2: Real Integration E2E Tests (NEW - To Implement)
- **Purpose**: Test actual frontend ↔ backend integration
- **Speed**: ~2-5 minutes for critical paths
- **Use for**: API contracts, CSRF, auth, data persistence

---

## Implementation Plan

### Phase 1: Infrastructure Setup

**1.1 Docker Test Environment**
```yaml
# docker-compose.test.yml
services:
  test-backend:
    build: ./backend
    environment:
      - DATABASE_URL=sqlite:///./data/test.db
      - TESTING=true
    ports:
      - "8001:8000"

  test-db:
    # SQLite file reset between tests
```

**1.2 Playwright Config for Real Backend**
```typescript
// playwright.real.config.ts
export default defineConfig({
  use: {
    baseURL: 'http://localhost:5173',
  },
  webServer: [
    {
      command: 'docker-compose -f docker-compose.test.yml up',
      port: 8001,
      reuseExistingServer: false,
    },
    {
      command: 'npm run dev',
      port: 5173,
      reuseExistingServer: false,
    }
  ],
  projects: [
    {
      name: 'real-e2e',
      testMatch: /.*\.real\.e2e\.ts/,
    }
  ]
});
```

### Phase 2: Database Management

**2.1 Test Database Seeding**
```typescript
// tests/setup/seed-database.ts
export async function seedTestData() {
  // Create test project
  await fetch('http://localhost:8001/api/projects/create', {
    method: 'POST',
    body: JSON.stringify({ name: 'E2E Test Project' })
  });
}

export async function cleanupTestData() {
  // Reset database to clean state
  await fetch('http://localhost:8001/api/test/reset', {
    method: 'POST'
  });
}
```

**2.2 Backend Test Reset Endpoint**
```python
# backend/app/api/test.py (only enabled in TESTING=true)
@router.post("/test/reset")
async def reset_test_database():
    """Reset database to clean state for E2E tests"""
    # Truncate all tables
    # Re-seed with minimal test data
    return {"status": "reset"}
```

### Phase 3: Real E2E Test Examples

**3.1 Chat Flow Real E2E**
```typescript
// tests/e2e/chat-workflow.real.e2e.ts
import { test, expect } from '@playwright/test';
import { seedTestData, cleanupTestData } from '../setup/seed-database';

test.describe('Real E2E: Chat Workflow', () => {
  test.beforeAll(async () => {
    await seedTestData();
  });

  test.afterAll(async () => {
    await cleanupTestData();
  });

  test('should create conversation and send message with real backend', async ({ page }) => {
    // NO MOCKING - real API calls
    await page.goto('http://localhost:5173');

    // Wait for real CSRF token fetch
    await page.waitForResponse(r => r.url().includes('/api/csrf-token'));

    // Click New Chat
    await page.click('button:has-text("New Chat")');

    // Wait for real conversation creation
    const createResponse = await page.waitForResponse(r =>
      r.url().includes('/api/conversations/create') && r.status() === 201
    );
    expect(createResponse.ok()).toBe(true);

    // Send message
    await page.fill('textarea', 'Hello, test message');
    await page.click('button[aria-label="Send message"]');

    // Wait for real SSE stream to complete
    await page.waitForSelector('.assistant-message', { timeout: 30000 });

    // Verify message persisted in database
    const conversation = await createResponse.json();
    const messagesResponse = await fetch(
      `http://localhost:8001/api/messages/${conversation.id}`
    );
    const messages = await messagesResponse.json();
    expect(messages.length).toBeGreaterThan(0);
  });
});
```

---

## Test Categories

| Category | Mocked | Real E2E | Why |
|----------|--------|----------|-----|
| UI interactions | ✅ | ❌ | Fast, no backend needed |
| API contracts | ❌ | ✅ | Must verify actual requests |
| CSRF protection | ❌ | ✅ | Security critical |
| Auth flows | ❌ | ✅ | Security critical |
| Data persistence | ❌ | ✅ | Must verify DB writes |
| Error handling | ✅ | ✅ | Both UI and backend errors |
| SSE streaming | ❌ | ✅ | Complex protocol |

---

## NPM Scripts

```json
{
  "scripts": {
    "test:e2e": "playwright test --config=playwright.config.ts",
    "test:e2e:real": "playwright test --config=playwright.real.config.ts",
    "test:e2e:all": "npm run test:e2e && npm run test:e2e:real"
  }
}
```

---

## CI/CD Integration

```yaml
# .github/workflows/e2e.yml
jobs:
  e2e-mocked:
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:e2e

  e2e-real:
    runs-on: ubuntu-latest
    services:
      backend:
        image: gpt-oss-backend:test
    steps:
      - run: npm run test:e2e:real
```

---

## Priority Order

1. **High**: CSRF and auth tests (security)
2. **High**: Chat stream E2E (core feature)
3. **Medium**: CRUD operations (data integrity)
4. **Low**: Edge cases (can use mocks)

---

## Timeline Estimate

- Phase 1 (Infrastructure): 1-2 days
- Phase 2 (Database): 1 day
- Phase 3 (Convert tests): 2-3 days
- **Total**: ~1 week

---

## Success Criteria

- [ ] Real E2E catches CSRF bugs
- [ ] Real E2E catches HTTP method mismatches
- [ ] Real E2E verifies database persistence
- [ ] Can run in CI/CD pipeline
- [ ] Total test time < 5 minutes
