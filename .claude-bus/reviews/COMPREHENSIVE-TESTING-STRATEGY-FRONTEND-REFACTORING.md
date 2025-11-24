# Comprehensive Testing Strategy: Frontend Refactoring
**Date**: 2025-11-24
**QA Agent**: Claude QA-Agent (Sonnet 4.5)
**Objective**: Achieve 50% frontend test coverage during refactoring without breaking existing functionality

---

## Executive Summary

This strategy ensures that refactoring `api-client.ts` (471 lines) and `sse-client.ts` (458 lines) into modular components achieves 50% coverage while preventing regressions. The plan includes unit tests, integration tests, contract testing, and continuous validation.

**Target Coverage**: 15% → 50% (235% increase)
**Timeline**: 3-4 days for test implementation
**Risk Level**: MEDIUM (refactoring without tests is high-risk; this plan mitigates it)

---

## 1. Testing Strategy Summary

### 1.1 Framework Selection

**RECOMMENDED: Vitest + MSW (Mock Service Worker)**

#### Vitest (Unit Testing)
**Selected**: YES

**Justification**:
- **Vite-native**: Already using Vite, zero config integration
- **Fast**: 10-100x faster than Jest for large suites
- **ESM support**: Native ES modules (no config hacks)
- **Jest-compatible API**: Familiar `describe`, `it`, `expect` syntax
- **Built-in coverage**: Via v8 or istanbul
- **Already installed**: In package.json

**Trade-offs**:
- Newer than Jest (less Stack Overflow answers)
- Smaller ecosystem
- Maturity: 2 years vs Jest's 7 years

**Why NOT Jest**:
- Requires complex config for Vite/SvelteKit
- ESM transformation issues
- Slower test execution
- Redundant with Vitest already installed

#### MSW (Mock Service Worker) for API Mocking
**Selected**: YES

**Justification**:
- **Network-level mocking**: Intercepts `fetch()` calls (tests real API layer)
- **Browser + Node.js**: Same mocks for unit tests and browser tests
- **Type-safe**: TypeScript support for handlers
- **Realistic**: Tests actual fetch logic, not mocked functions
- **No module mocking**: Don't need to mock entire modules

**Trade-offs**:
- Setup complexity (5-10 minutes initial setup)
- Learning curve for handlers

**Why NOT vi.mock()**:
- Module-level mocking (doesn't test fetch logic)
- Doesn't test serialization/deserialization
- Doesn't test HTTP headers

#### @testing-library/svelte (Component Testing)
**Selected**: YES (for toast integration tests only)

**Justification**:
- **Already installed**: In package.json
- **User-centric**: Tests what user sees, not implementation
- **Svelte-specific**: Handles Svelte component lifecycle

**Scope**: Only for testing toast notification triggers

---

### 1.2 Coverage Targets by Module

| Module | Lines | Target Coverage | Priority | Test Count (Est.) |
|--------|-------|----------------|----------|-------------------|
| `projects-api.ts` (NEW) | ~120 | 85% | CRITICAL | 18 tests |
| `conversations-api.ts` (NEW) | ~140 | 85% | CRITICAL | 22 tests |
| `messages-api.ts` (NEW) | ~100 | 85% | CRITICAL | 12 tests |
| `api-base.ts` (NEW) | ~60 | 90% | CRITICAL | 15 tests |
| `sse-client.ts` (NEW) | ~200 | 65% | HIGH | 12 tests |
| `sse-reconnection.ts` (NEW) | ~80 | 90% | HIGH | 10 tests |
| `csrf-client.ts` (NEW) | ~40 | 95% | CRITICAL | 8 tests |
| `toast.ts` (existing) | ~100 | 80% | MEDIUM | 10 tests |
| `date.ts` (existing) | ~50 | 90% | LOW | Already covered |
| **TOTAL** | ~890 | **52%** | - | **107 tests** |

**Calculation**:
- New code: ~640 lines (targets 80-95% coverage)
- Existing code: ~250 lines (already ~30% covered)
- Weighted average: (640 * 0.85 + 250 * 0.30) / 890 = **52% total coverage**

**Coverage Gates (MUST PASS)**:
- Overall frontend: ≥ 50%
- Critical modules (api-base, csrf-client): ≥ 90%
- API modules (projects, conversations, messages): ≥ 85%
- SSE modules: ≥ 65%

---

### 1.3 Test Types

**Unit Tests** (75 tests, ~70% of total):
- Test individual functions in isolation
- Mock all dependencies (API, stores, services)
- Fast execution (< 10ms per test)
- Co-located with source files (`*.test.ts`)

**Integration Tests** (20 tests, ~18% of total):
- Test interactions between modules
- Use real MSW server
- Test complete workflows (create → list → delete)
- Located in `tests/integration/`

**Component Tests** (12 tests, ~12% of total):
- Test Svelte components with toast integration
- Verify UI feedback for API calls
- Use @testing-library/svelte
- Located in `tests/component/`

---

## 2. Detailed Test Specifications

### 2.1 Unit Tests: `projects-api.ts`

**File**: `src/lib/services/projects-api.test.ts`

**Coverage Target**: 85%

```typescript
import { describe, it, expect, beforeAll, afterAll, afterEach, vi } from 'vitest';
import { server } from '../../../tests/helpers/mock-server';
import { http, HttpResponse } from 'msw';
import * as projectsApi from './projects-api';
import { toast } from '$lib/stores/toast';

// Mock toast (don't show real notifications during tests)
vi.mock('$lib/stores/toast', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  },
  getErrorMessage: vi.fn((err) => err.detail || 'Error')
}));

describe('projects-api', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  describe('createProject', () => {
    it('should create project successfully', async () => {
      const result = await projectsApi.createProject({
        name: 'Test Project',
        description: 'Test Description'
      });

      expect(result.id).toBeDefined();
      expect(result.name).toBe('Test Project');
      expect(toast.success).toHaveBeenCalledWith(
        expect.stringContaining('created successfully')
      );
    });

    it('should handle 400 validation error', async () => {
      server.use(
        http.post('/api/projects/create', () => {
          return HttpResponse.json(
            { detail: 'Name is required' },
            { status: 400 }
          );
        })
      );

      await expect(
        projectsApi.createProject({ name: '', description: 'Desc' })
      ).rejects.toThrow();

      expect(toast.error).toHaveBeenCalledWith(
        expect.stringContaining('Name is required')
      );
    });

    it('should handle 500 server error', async () => {
      server.use(
        http.post('/api/projects/create', () => {
          return HttpResponse.json(
            { detail: 'Internal server error' },
            { status: 500 }
          );
        })
      );

      await expect(
        projectsApi.createProject({ name: 'Test', description: 'Desc' })
      ).rejects.toThrow();

      expect(toast.error).toHaveBeenCalled();
    });

    it('should handle network error (fetch fails)', async () => {
      server.use(
        http.post('/api/projects/create', () => {
          return HttpResponse.error();
        })
      );

      await expect(
        projectsApi.createProject({ name: 'Test', description: 'Desc' })
      ).rejects.toThrow();

      expect(toast.error).toHaveBeenCalledWith(
        expect.stringContaining('Network error')
      );
    });

    it('should include CSRF token in request headers', async () => {
      let capturedHeaders: Headers | null = null;

      server.use(
        http.post('/api/projects/create', async ({ request }) => {
          capturedHeaders = request.headers;
          return HttpResponse.json({ id: 1, name: 'Test', description: 'Desc' });
        })
      );

      await projectsApi.createProject({ name: 'Test', description: 'Desc' });

      expect(capturedHeaders?.get('X-CSRF-Token')).toBeTruthy();
    });

    it('should retry on 403 (expired CSRF token)', async () => {
      let callCount = 0;

      server.use(
        http.post('/api/projects/create', () => {
          callCount++;
          if (callCount === 1) {
            // First call: return 403 (expired token)
            return HttpResponse.json({ detail: 'CSRF token expired' }, { status: 403 });
          } else {
            // Second call: succeed (after token refresh)
            return HttpResponse.json({ id: 1, name: 'Test', description: 'Desc' });
          }
        })
      );

      const result = await projectsApi.createProject({ name: 'Test', description: 'Desc' });

      expect(callCount).toBe(2); // Should retry once
      expect(result.id).toBe(1);
    });

    it('should send correct payload structure', async () => {
      let capturedBody: any = null;

      server.use(
        http.post('/api/projects/create', async ({ request }) => {
          capturedBody = await request.json();
          return HttpResponse.json({ id: 1, ...capturedBody });
        })
      );

      await projectsApi.createProject({
        name: 'Test Project',
        description: 'Test Description'
      });

      expect(capturedBody).toEqual({
        name: 'Test Project',
        description: 'Test Description'
      });
    });

    it('should call correct API endpoint', async () => {
      let capturedUrl: string | null = null;

      server.use(
        http.post('/api/projects/create', ({ request }) => {
          capturedUrl = request.url;
          return HttpResponse.json({ id: 1, name: 'Test', description: 'Desc' });
        })
      );

      await projectsApi.createProject({ name: 'Test', description: 'Desc' });

      expect(capturedUrl).toContain('/api/projects/create');
    });
  });

  describe('fetchProjects', () => {
    it('should fetch all projects successfully', async () => {
      const result = await projectsApi.fetchProjects();

      expect(result.projects).toBeDefined();
      expect(result.total).toBeDefined();
      expect(Array.isArray(result.projects)).toBe(true);
    });

    it('should handle empty project list', async () => {
      server.use(
        http.get('/api/projects/list', () => {
          return HttpResponse.json({ projects: [], total: 0 });
        })
      );

      const result = await projectsApi.fetchProjects();

      expect(result.projects).toEqual([]);
      expect(result.total).toBe(0);
    });

    it('should handle 500 error', async () => {
      server.use(
        http.get('/api/projects/list', () => {
          return HttpResponse.json({ detail: 'Database error' }, { status: 500 });
        })
      );

      await expect(projectsApi.fetchProjects()).rejects.toThrow();
      expect(toast.error).toHaveBeenCalled();
    });

    it('should parse project objects correctly', async () => {
      server.use(
        http.get('/api/projects/list', () => {
          return HttpResponse.json({
            projects: [
              {
                id: 1,
                name: 'Project 1',
                description: 'Description 1',
                created_at: '2025-11-24T00:00:00Z'
              }
            ],
            total: 1
          });
        })
      );

      const result = await projectsApi.fetchProjects();

      expect(result.projects[0].id).toBe(1);
      expect(result.projects[0].name).toBe('Project 1');
      expect(result.projects[0].created_at).toBe('2025-11-24T00:00:00Z');
    });
  });

  describe('fetchProject', () => {
    it('should fetch single project by ID', async () => {
      const result = await projectsApi.fetchProject(1);

      expect(result.id).toBe(1);
      expect(result.name).toBeDefined();
    });

    it('should handle 404 not found', async () => {
      server.use(
        http.get('/api/projects/:id', () => {
          return HttpResponse.json({ detail: 'Project not found' }, { status: 404 });
        })
      );

      await expect(projectsApi.fetchProject(999)).rejects.toThrow();
      expect(toast.error).toHaveBeenCalledWith(
        expect.stringContaining('not found')
      );
    });

    it('should use correct endpoint with ID parameter', async () => {
      let capturedUrl: string | null = null;

      server.use(
        http.get('/api/projects/:id', ({ request }) => {
          capturedUrl = request.url;
          return HttpResponse.json({ id: 42, name: 'Test', description: 'Desc' });
        })
      );

      await projectsApi.fetchProject(42);

      expect(capturedUrl).toContain('/api/projects/42');
    });
  });

  describe('deleteProject', () => {
    it('should delete project successfully', async () => {
      await expect(projectsApi.deleteProject(1)).resolves.not.toThrow();
      expect(toast.success).toHaveBeenCalledWith(
        expect.stringContaining('deleted')
      );
    });

    it('should handle 404 when deleting non-existent project', async () => {
      server.use(
        http.delete('/api/projects/:id', () => {
          return HttpResponse.json({ detail: 'Project not found' }, { status: 404 });
        })
      );

      await expect(projectsApi.deleteProject(999)).rejects.toThrow();
      expect(toast.error).toHaveBeenCalled();
    });

    it('should use DELETE HTTP method', async () => {
      let capturedMethod: string | null = null;

      server.use(
        http.delete('/api/projects/:id', ({ request }) => {
          capturedMethod = request.method;
          return new HttpResponse(null, { status: 204 });
        })
      );

      await projectsApi.deleteProject(1);

      expect(capturedMethod).toBe('DELETE');
    });
  });
});
```

**Total Tests**: 18
**Estimated Coverage**: 85-90%

---

### 2.2 Unit Tests: `conversations-api.ts`

**File**: `src/lib/services/conversations-api.test.ts`

**Coverage Target**: 85%

**Test Structure** (similar to projects-api):

```typescript
describe('conversations-api', () => {
  describe('createConversation', () => {
    // 7 tests (success, validation errors, network errors, CSRF, payload verification)
  });

  describe('fetchConversations', () => {
    // 5 tests (success, empty list, pagination, sorting, filtering)
  });

  describe('fetchConversation', () => {
    // 4 tests (success, 404, correct endpoint, payload parsing)
  });

  describe('updateConversation', () => {
    // 4 tests (success, 404, validation, CSRF)
  });

  describe('deleteConversation', () => {
    // 2 tests (success, 404)
  });
});
```

**Total Tests**: 22
**Estimated Coverage**: 85%

---

### 2.3 Unit Tests: `messages-api.ts`

**File**: `src/lib/services/messages-api.test.ts`

**Coverage Target**: 85%

```typescript
describe('messages-api', () => {
  describe('fetchMessages', () => {
    // 6 tests (success, pagination, conversation not found, empty, sorting)
  });

  describe('deleteMessage', () => {
    // 3 tests (success, 404, cascade delete warning)
  });

  describe('reactToMessage', () => {
    // 3 tests (thumbs up, thumbs down, toggle reaction)
  });
});
```

**Total Tests**: 12
**Estimated Coverage**: 85%

---

### 2.4 Unit Tests: `api-base.ts` (Critical Shared Module)

**File**: `src/lib/services/shared/api-base.test.ts`

**Coverage Target**: 90%

```typescript
describe('api-base', () => {
  describe('apiRequest', () => {
    it('should make GET request successfully', async () => {
      const result = await apiRequest('/test', { method: 'GET' });
      expect(result).toBeDefined();
    });

    it('should make POST request with JSON body', async () => {
      const result = await apiRequest('/test', {
        method: 'POST',
        body: { key: 'value' }
      });
      expect(result).toBeDefined();
    });

    it('should automatically add Content-Type header for POST', async () => {
      // Verify Content-Type: application/json is added
    });

    it('should include CSRF token from csrf-client', async () => {
      // Verify X-CSRF-Token header is added
    });

    it('should retry on 403 (CSRF token expired)', async () => {
      // First call returns 403, second succeeds
    });

    it('should throw on non-2xx status codes', async () => {
      // 4xx and 5xx should throw
    });

    it('should call toast.error on failure', async () => {
      // Verify toast integration
    });

    it('should handle network errors (TypeError)', async () => {
      // fetch() fails due to network issue
    });

    it('should parse JSON response automatically', async () => {
      // Verify response.json() is called
    });

    it('should handle non-JSON responses gracefully', async () => {
      // Backend returns plain text
    });

    it('should support custom headers', async () => {
      // Pass custom headers in options
    });

    it('should support query parameters', async () => {
      // Append query string to URL
    });

    it('should handle empty response body (204)', async () => {
      // DELETE requests often return 204 No Content
    });

    it('should timeout after 30 seconds (AbortController)', async () => {
      // Long-running request should abort
    });

    it('should allow cancellation via AbortSignal', async () => {
      // External abort signal support
    });
  });
});
```

**Total Tests**: 15
**Estimated Coverage**: 90%

---

### 2.5 Unit Tests: `sse-client.ts`

**File**: `src/lib/services/sse-client.test.ts`

**Coverage Target**: 65% (EventSource is harder to mock)

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SSEClient } from './sse-client';

// Mock EventSource (not natively available in Node.js)
global.EventSource = vi.fn();

describe('SSEClient', () => {
  let client: SSEClient;

  beforeEach(() => {
    client = new SSEClient();
    vi.clearAllMocks();
  });

  describe('connect', () => {
    it('should create EventSource with correct URL', async () => {
      await client.connect(1, 'Hello');
      expect(EventSource).toHaveBeenCalledWith(
        expect.stringContaining('/api/chat/stream')
      );
    });

    it('should send POST request before connecting', async () => {
      // Verify POST /api/chat/stream is called with message payload
    });

    it('should update connection state to "connected"', async () => {
      await client.connect(1, 'Hello');
      expect(client.getState()).toBe('connected');
    });

    it('should close existing connection before new one', async () => {
      await client.connect(1, 'First');
      await client.connect(1, 'Second');
      // Verify first EventSource was closed
    });
  });

  describe('event handlers', () => {
    it('should handle "token" events', async () => {
      const onToken = vi.fn();
      client.onToken(onToken);

      // Simulate EventSource token event
      const event = new MessageEvent('token', {
        data: JSON.stringify({ token: 'Hello' })
      });
      client['eventSource'].dispatchEvent(event);

      expect(onToken).toHaveBeenCalledWith({ token: 'Hello' });
    });

    it('should handle "complete" events', async () => {
      const onComplete = vi.fn();
      client.onComplete(onComplete);

      // Simulate complete event
      const event = new MessageEvent('complete', {
        data: JSON.stringify({ message_id: 123 })
      });
      client['eventSource'].dispatchEvent(event);

      expect(onComplete).toHaveBeenCalledWith({ message_id: 123 });
    });

    it('should handle "error" events', async () => {
      const onError = vi.fn();
      client.onError(onError);

      // Simulate error event
      const event = new Event('error');
      client['eventSource'].dispatchEvent(event);

      expect(onError).toHaveBeenCalled();
    });

    it('should update messages store on token event', async () => {
      // Verify messages store is updated
    });

    it('should update conversations store on complete', async () => {
      // Verify conversations store is updated
    });
  });

  describe('disconnect', () => {
    it('should close EventSource connection', async () => {
      await client.connect(1, 'Hello');
      client.disconnect();

      expect(client['eventSource'].close).toHaveBeenCalled();
    });

    it('should update state to "disconnected"', async () => {
      await client.connect(1, 'Hello');
      client.disconnect();

      expect(client.getState()).toBe('disconnected');
    });

    it('should cleanup event listeners', async () => {
      await client.connect(1, 'Hello');
      client.disconnect();
      // Verify listeners removed
    });
  });

  describe('cancel', () => {
    it('should send POST to cancel endpoint', async () => {
      await client.connect(1, 'Hello');
      await client.cancel();

      // Verify POST /api/chat/cancel/{session_id}
    });

    it('should disconnect after cancel', async () => {
      await client.connect(1, 'Hello');
      await client.cancel();

      expect(client.getState()).toBe('disconnected');
    });
  });
});
```

**Total Tests**: 12
**Estimated Coverage**: 65%

**Note**: EventSource is difficult to test comprehensively without integration tests. Unit tests focus on state management and API calls.

---

### 2.6 Unit Tests: `sse-reconnection.ts`

**File**: `src/lib/services/sse-reconnection.test.ts`

**Coverage Target**: 90%

```typescript
describe('sse-reconnection', () => {
  describe('calculateBackoff', () => {
    it('should calculate exponential backoff correctly', () => {
      expect(calculateBackoff(0)).toBe(1000); // 1st retry: 1s
      expect(calculateBackoff(1)).toBe(2000); // 2nd retry: 2s
      expect(calculateBackoff(2)).toBe(4000); // 3rd retry: 4s
      expect(calculateBackoff(3)).toBe(8000); // 4th retry: 8s
      expect(calculateBackoff(4)).toBe(16000); // 5th retry: 16s
    });

    it('should cap backoff at max value (30s)', () => {
      expect(calculateBackoff(10)).toBe(30000); // Max: 30s
    });

    it('should add jitter to prevent thundering herd', () => {
      const backoff1 = calculateBackoff(2, true);
      const backoff2 = calculateBackoff(2, true);
      // Should be different due to random jitter
      expect(backoff1).not.toBe(backoff2);
    });
  });

  describe('shouldRetry', () => {
    it('should return true when retries < max', () => {
      expect(shouldRetry(0, 5)).toBe(true);
      expect(shouldRetry(4, 5)).toBe(true);
    });

    it('should return false when retries >= max', () => {
      expect(shouldRetry(5, 5)).toBe(false);
      expect(shouldRetry(6, 5)).toBe(false);
    });

    it('should handle edge case: max = 0 (no retries)', () => {
      expect(shouldRetry(0, 0)).toBe(false);
    });
  });

  describe('ReconnectionManager', () => {
    it('should retry with exponential backoff', async () => {
      const manager = new ReconnectionManager(5);
      const attempts: number[] = [];

      await manager.retry(async (attempt) => {
        attempts.push(attempt);
        if (attempt < 3) throw new Error('Retry');
      });

      expect(attempts).toEqual([0, 1, 2, 3]);
    });

    it('should give up after max retries', async () => {
      const manager = new ReconnectionManager(3);

      await expect(
        manager.retry(async () => {
          throw new Error('Always fails');
        })
      ).rejects.toThrow('Max retries exceeded');
    });

    it('should reset retry count on success', async () => {
      const manager = new ReconnectionManager(5);

      await manager.retry(async () => {
        return 'success';
      });

      expect(manager.getRetryCount()).toBe(0);
    });

    it('should call onRetry callback', async () => {
      const onRetry = vi.fn();
      const manager = new ReconnectionManager(5, { onRetry });

      await manager.retry(async (attempt) => {
        if (attempt === 0) throw new Error('Retry');
      });

      expect(onRetry).toHaveBeenCalledWith(0, expect.any(Number));
    });

    it('should call onGiveUp callback after max retries', async () => {
      const onGiveUp = vi.fn();
      const manager = new ReconnectionManager(2, { onGiveUp });

      await expect(
        manager.retry(async () => {
          throw new Error('Always fails');
        })
      ).rejects.toThrow();

      expect(onGiveUp).toHaveBeenCalled();
    });
  });
});
```

**Total Tests**: 10
**Estimated Coverage**: 90%

---

### 2.7 Unit Tests: `csrf-client.ts` (CRITICAL)

**File**: `src/lib/services/csrf-client.test.ts`

**Coverage Target**: 95%

```typescript
describe('csrf-client', () => {
  describe('fetchToken', () => {
    it('should fetch CSRF token from /api/csrf-token', async () => {
      const token = await fetchToken();
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
    });

    it('should cache token after fetching', async () => {
      const token1 = await fetchToken();
      const token2 = await fetchToken();
      expect(token1).toBe(token2); // Same token (cached)
    });

    it('should handle fetch failure gracefully', async () => {
      server.use(
        http.get('/api/csrf-token', () => {
          return HttpResponse.error();
        })
      );

      await expect(fetchToken()).rejects.toThrow();
    });

    it('should extract token from response body', async () => {
      server.use(
        http.get('/api/csrf-token', () => {
          return HttpResponse.json({ token: 'test-csrf-token' });
        })
      );

      const token = await fetchToken();
      expect(token).toBe('test-csrf-token');
    });

    it('should extract token from X-CSRF-Token header (fallback)', async () => {
      server.use(
        http.get('/api/csrf-token', () => {
          return HttpResponse.json(
            {},
            { headers: { 'X-CSRF-Token': 'header-token' } }
          );
        })
      );

      const token = await fetchToken();
      expect(token).toBe('header-token');
    });
  });

  describe('refreshToken', () => {
    it('should fetch new token and update cache', async () => {
      const token1 = await fetchToken();
      const token2 = await refreshToken();
      expect(token2).toBeDefined();
      // Tokens should be different (new token fetched)
    });

    it('should handle refresh failure', async () => {
      server.use(
        http.get('/api/csrf-token', () => {
          return HttpResponse.json({ detail: 'Server error' }, { status: 500 });
        })
      );

      await expect(refreshToken()).rejects.toThrow();
    });
  });

  describe('getToken', () => {
    it('should return cached token if available', async () => {
      await fetchToken();
      const token = getToken();
      expect(token).toBeDefined();
    });

    it('should return null if no token cached', () => {
      clearToken(); // Clear cache
      const token = getToken();
      expect(token).toBeNull();
    });
  });

  describe('clearToken', () => {
    it('should clear cached token', async () => {
      await fetchToken();
      clearToken();
      const token = getToken();
      expect(token).toBeNull();
    });
  });

  describe('auto-refresh on 403', () => {
    it('should auto-refresh token when API returns 403', async () => {
      // This test belongs in api-base.test.ts
      // Verify that 403 triggers refreshToken() and retries request
    });
  });
});
```

**Total Tests**: 8
**Estimated Coverage**: 95%

---

### 2.8 Unit Tests: `toast.ts`

**File**: `src/lib/stores/toast.test.ts`

**Coverage Target**: 80%

```typescript
import { describe, it, expect, vi } from 'vitest';
import { toast, getErrorMessage } from './toast';

// Mock @zerodevx/svelte-toast
vi.mock('@zerodevx/svelte-toast', () => ({
  toast: {
    push: vi.fn(() => 1), // Return toast ID
    pop: vi.fn()
  }
}));

import { toast as svelteToast } from '@zerodevx/svelte-toast';

describe('toast', () => {
  describe('success', () => {
    it('should call svelteToast.push with success theme', () => {
      toast.success('Operation successful');
      expect(svelteToast.push).toHaveBeenCalledWith(
        'Operation successful',
        expect.objectContaining({
          theme: expect.objectContaining({
            '--toastBackground': '#10b981'
          })
        })
      );
    });

    it('should use default duration (3000ms)', () => {
      toast.success('Test');
      expect(svelteToast.push).toHaveBeenCalledWith(
        'Test',
        expect.objectContaining({ duration: 3000 })
      );
    });

    it('should use custom duration if provided', () => {
      toast.success('Test', 5000);
      expect(svelteToast.push).toHaveBeenCalledWith(
        'Test',
        expect.objectContaining({ duration: 5000 })
      );
    });
  });

  describe('error', () => {
    it('should call svelteToast.push with error theme', () => {
      toast.error('Operation failed');
      expect(svelteToast.push).toHaveBeenCalledWith(
        'Operation failed',
        expect.objectContaining({
          theme: expect.objectContaining({
            '--toastBackground': '#ef4444'
          })
        })
      );
    });

    it('should use default duration (5000ms)', () => {
      toast.error('Test');
      expect(svelteToast.push).toHaveBeenCalledWith(
        'Test',
        expect.objectContaining({ duration: 5000 })
      );
    });
  });

  describe('getErrorMessage', () => {
    it('should return user-friendly message for 400', () => {
      expect(getErrorMessage(400)).toContain('Invalid request');
    });

    it('should return user-friendly message for 404', () => {
      expect(getErrorMessage(404)).toContain('not found');
    });

    it('should return user-friendly message for 500', () => {
      expect(getErrorMessage(500)).toContain('Server error');
    });

    it('should extract detail from error object', () => {
      const error = { detail: 'Custom error message' };
      expect(getErrorMessage(error)).toBe('Custom error message');
    });

    it('should extract status from error object', () => {
      const error = { status: 404 };
      expect(getErrorMessage(error)).toContain('not found');
    });

    it('should handle string errors', () => {
      expect(getErrorMessage('Custom error')).toBe('Custom error');
    });

    it('should return default message for unknown errors', () => {
      expect(getErrorMessage({})).toBe('An unexpected error occurred.');
    });
  });
});
```

**Total Tests**: 10
**Estimated Coverage**: 80%

---

## 3. Integration Test Specifications

### 3.1 Integration Test: Complete Chat Flow

**File**: `tests/integration/chat-flow.test.ts`

```typescript
describe('Integration: Complete Chat Flow', () => {
  it('should handle full workflow: create project → conversation → send message → delete', async () => {
    // 1. Create project
    const project = await projectsApi.createProject({
      name: 'Integration Test Project',
      description: 'Testing end-to-end flow'
    });
    expect(project.id).toBeDefined();

    // 2. Create conversation
    const conversation = await conversationsApi.createConversation({
      project_id: project.id,
      title: 'Test Conversation'
    });
    expect(conversation.id).toBeDefined();

    // 3. Send message (SSE stream)
    const client = new SSEClient();
    let receivedTokens: string[] = [];

    client.onToken((event) => {
      receivedTokens.push(event.token);
    });

    await client.connect(conversation.id, 'Hello, test message');

    // Wait for stream to complete
    await new Promise((resolve) => {
      client.onComplete(() => resolve(null));
    });

    expect(receivedTokens.length).toBeGreaterThan(0);

    // 4. Fetch messages
    const messages = await messagesApi.fetchMessages(conversation.id);
    expect(messages.messages.length).toBe(2); // User + assistant

    // 5. Delete conversation
    await conversationsApi.deleteConversation(conversation.id);

    // 6. Verify deleted
    await expect(
      conversationsApi.fetchConversation(conversation.id)
    ).rejects.toThrow();

    // 7. Delete project
    await projectsApi.deleteProject(project.id);
  });
});
```

**Total Tests**: 1 comprehensive integration test
**Execution Time**: ~5 seconds (involves SSE streaming)

---

### 3.2 Integration Test: SSE Reconnection Flow

**File**: `tests/integration/sse-reconnection.test.ts`

```typescript
describe('Integration: SSE Reconnection', () => {
  it('should reconnect after connection loss', async () => {
    const client = new SSEClient();
    let connectionCount = 0;

    // Track connection attempts
    client.onConnect(() => {
      connectionCount++;
    });

    // Connect
    await client.connect(1, 'Test message');

    // Simulate connection drop (server closes EventSource)
    client['eventSource'].dispatchEvent(new Event('error'));

    // Wait for automatic reconnection
    await new Promise((resolve) => setTimeout(resolve, 2000));

    expect(connectionCount).toBeGreaterThan(1); // Reconnected
  });

  it('should use exponential backoff for retries', async () => {
    const client = new SSEClient();
    const retryTimes: number[] = [];

    client.onRetry((attempt, delay) => {
      retryTimes.push(delay);
    });

    // Simulate 3 connection failures
    for (let i = 0; i < 3; i++) {
      client['eventSource'].dispatchEvent(new Event('error'));
      await new Promise((resolve) => setTimeout(resolve, 100));
    }

    // Verify exponential backoff
    expect(retryTimes[0]).toBe(1000); // 1s
    expect(retryTimes[1]).toBe(2000); // 2s
    expect(retryTimes[2]).toBe(4000); // 4s
  });

  it('should give up after max retries (5)', async () => {
    const client = new SSEClient();
    let gaveUp = false;

    client.onGiveUp(() => {
      gaveUp = true;
    });

    // Simulate 6 connection failures
    for (let i = 0; i < 6; i++) {
      client['eventSource'].dispatchEvent(new Event('error'));
      await new Promise((resolve) => setTimeout(resolve, 100));
    }

    expect(gaveUp).toBe(true);
  });
});
```

**Total Tests**: 3
**Execution Time**: ~10 seconds (involves retries)

---

### 3.3 Integration Test: CSRF Token Lifecycle

**File**: `tests/integration/csrf-token-flow.test.ts`

```typescript
describe('Integration: CSRF Token Lifecycle', () => {
  it('should fetch token on app load', async () => {
    const token = await fetchToken();
    expect(token).toBeDefined();
    expect(token.length).toBeGreaterThan(0);
  });

  it('should include token in all API calls', async () => {
    let capturedHeaders: Headers | null = null;

    server.use(
      http.post('/api/projects/create', async ({ request }) => {
        capturedHeaders = request.headers;
        return HttpResponse.json({ id: 1, name: 'Test', description: 'Desc' });
      })
    );

    await projectsApi.createProject({ name: 'Test', description: 'Desc' });

    expect(capturedHeaders?.get('X-CSRF-Token')).toBeTruthy();
  });

  it('should auto-refresh token on 403', async () => {
    let callCount = 0;

    server.use(
      http.post('/api/projects/create', () => {
        callCount++;
        if (callCount === 1) {
          return HttpResponse.json({ detail: 'CSRF token expired' }, { status: 403 });
        } else {
          return HttpResponse.json({ id: 1, name: 'Test', description: 'Desc' });
        }
      })
    );

    const result = await projectsApi.createProject({ name: 'Test', description: 'Desc' });

    expect(callCount).toBe(2); // First call failed, second succeeded
    expect(result.id).toBe(1);
  });

  it('should cache token (no redundant fetches)', async () => {
    let fetchCount = 0;

    server.use(
      http.get('/api/csrf-token', () => {
        fetchCount++;
        return HttpResponse.json({ token: 'test-token' });
      })
    );

    await fetchToken();
    await fetchToken();
    await fetchToken();

    expect(fetchCount).toBe(1); // Only fetched once, then cached
  });
});
```

**Total Tests**: 4
**Execution Time**: ~2 seconds

---

### 3.4 Integration Test: Error Recovery

**File**: `tests/integration/error-recovery.test.ts`

```typescript
describe('Integration: Error Recovery', () => {
  it('should recover from 500 error and retry successfully', async () => {
    let callCount = 0;

    server.use(
      http.post('/api/projects/create', () => {
        callCount++;
        if (callCount === 1) {
          return HttpResponse.json({ detail: 'Server error' }, { status: 500 });
        } else {
          return HttpResponse.json({ id: 1, name: 'Test', description: 'Desc' });
        }
      })
    );

    // First call fails
    await expect(
      projectsApi.createProject({ name: 'Test', description: 'Desc' })
    ).rejects.toThrow();

    // User retries
    const result = await projectsApi.createProject({ name: 'Test', description: 'Desc' });

    expect(result.id).toBe(1);
  });

  it('should show error toast on API failure', async () => {
    server.use(
      http.post('/api/projects/create', () => {
        return HttpResponse.json({ detail: 'Validation failed' }, { status: 400 });
      })
    );

    await expect(
      projectsApi.createProject({ name: '', description: '' })
    ).rejects.toThrow();

    expect(toast.error).toHaveBeenCalledWith(
      expect.stringContaining('Validation failed')
    );
  });

  it('should show success toast on API success', async () => {
    await projectsApi.createProject({ name: 'Test', description: 'Desc' });

    expect(toast.success).toHaveBeenCalledWith(
      expect.stringContaining('created successfully')
    );
  });
});
```

**Total Tests**: 3
**Execution Time**: ~1 second

---

## 4. Mocking Strategy

### 4.1 MSW Server Setup

**File**: `tests/helpers/mock-server.ts`

```typescript
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { createMockProject, createMockConversation, createMockMessage } from './factories';

/**
 * MSW handlers for API mocking
 *
 * These handlers intercept fetch() calls and return mock responses
 */
export const handlers = [
  // Projects API
  http.get('/api/projects/list', () => {
    return HttpResponse.json({
      projects: [
        createMockProject({ id: 1, name: 'Project 1' }),
        createMockProject({ id: 2, name: 'Project 2' })
      ],
      total: 2
    });
  }),

  http.get('/api/projects/:id', ({ params }) => {
    const id = Number(params.id);
    return HttpResponse.json(createMockProject({ id }));
  }),

  http.post('/api/projects/create', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json(
      createMockProject({ id: 1, ...body }),
      { status: 201 }
    );
  }),

  http.delete('/api/projects/:id', () => {
    return new HttpResponse(null, { status: 204 });
  }),

  // Conversations API
  http.get('/api/conversations/list', ({ request }) => {
    const url = new URL(request.url);
    const projectId = Number(url.searchParams.get('project_id'));

    return HttpResponse.json({
      conversations: [
        createMockConversation({ id: 1, project_id: projectId }),
        createMockConversation({ id: 2, project_id: projectId })
      ],
      total: 2
    });
  }),

  http.post('/api/conversations/create', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json(
      createMockConversation({ id: 1, ...body }),
      { status: 201 }
    );
  }),

  http.delete('/api/conversations/:id', () => {
    return new HttpResponse(null, { status: 204 });
  }),

  // Messages API
  http.get('/api/messages/list', ({ request }) => {
    const url = new URL(request.url);
    const conversationId = Number(url.searchParams.get('conversation_id'));

    return HttpResponse.json({
      messages: [
        createMockMessage({ id: 1, conversation_id: conversationId, role: 'user' }),
        createMockMessage({ id: 2, conversation_id: conversationId, role: 'assistant' })
      ],
      total: 2
    });
  }),

  // CSRF Token API
  http.get('/api/csrf-token', () => {
    return HttpResponse.json(
      { token: 'mock-csrf-token-12345' },
      { headers: { 'X-CSRF-Token': 'mock-csrf-token-12345' } }
    );
  }),

  // SSE Chat Stream
  http.post('/api/chat/stream', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      session_id: 'mock-session-123',
      conversation_id: body.conversation_id
    });
  })
];

/**
 * MSW server instance
 *
 * Usage in tests:
 * beforeAll(() => server.listen())
 * afterEach(() => server.resetHandlers())
 * afterAll(() => server.close())
 */
export const server = setupServer(...handlers);
```

---

### 4.2 Mock Data Factories

**File**: `tests/helpers/factories.ts`

```typescript
import type { Project, Conversation, Message } from '$lib/types';

/**
 * Create mock project object
 *
 * Usage: createMockProject({ name: 'Custom Name' })
 */
export function createMockProject(overrides: Partial<Project> = {}): Project {
  return {
    id: 1,
    name: 'Test Project',
    description: 'Test Description',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides
  };
}

/**
 * Create mock conversation object
 */
export function createMockConversation(overrides: Partial<Conversation> = {}): Conversation {
  return {
    id: 1,
    project_id: 1,
    title: 'Test Conversation',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    message_count: 0,
    last_message_at: null,
    ...overrides
  };
}

/**
 * Create mock message object
 */
export function createMockMessage(overrides: Partial<Message> = {}): Message {
  return {
    id: 1,
    conversation_id: 1,
    role: 'user',
    content: 'Test message',
    created_at: new Date().toISOString(),
    reaction: null,
    ...overrides
  };
}

/**
 * Create multiple mock objects
 *
 * Usage: createMockProjects(5)
 */
export function createMockProjects(count: number): Project[] {
  return Array.from({ length: count }, (_, i) =>
    createMockProject({ id: i + 1, name: `Project ${i + 1}` })
  );
}

export function createMockConversations(count: number, projectId: number): Conversation[] {
  return Array.from({ length: count }, (_, i) =>
    createMockConversation({
      id: i + 1,
      project_id: projectId,
      title: `Conversation ${i + 1}`
    })
  );
}

export function createMockMessages(count: number, conversationId: number): Message[] {
  return Array.from({ length: count }, (_, i) =>
    createMockMessage({
      id: i + 1,
      conversation_id: conversationId,
      role: i % 2 === 0 ? 'user' : 'assistant',
      content: `Message ${i + 1}`
    })
  );
}
```

---

### 4.3 Mock Toast Store

**File**: `tests/helpers/mock-toast.ts`

```typescript
import { vi } from 'vitest';

/**
 * Mock toast store for testing
 *
 * Usage in test:
 * vi.mock('$lib/stores/toast', () => ({ toast: mockToast }))
 */
export const mockToast = {
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  info: vi.fn(),
  dismiss: vi.fn(),
  dismissAll: vi.fn()
};

/**
 * Reset mock call history
 *
 * Usage: afterEach(() => resetMockToast())
 */
export function resetMockToast() {
  mockToast.success.mockClear();
  mockToast.error.mockClear();
  mockToast.warning.mockClear();
  mockToast.info.mockClear();
  mockToast.dismiss.mockClear();
  mockToast.dismissAll.mockClear();
}
```

---

## 5. Test Infrastructure

### 5.1 File Organization

```
frontend/
├── src/
│   └── lib/
│       ├── services/
│       │   ├── projects-api.ts
│       │   ├── projects-api.test.ts          ← Unit test (co-located)
│       │   ├── conversations-api.ts
│       │   ├── conversations-api.test.ts
│       │   ├── messages-api.ts
│       │   ├── messages-api.test.ts
│       │   ├── sse-client.ts
│       │   ├── sse-client.test.ts
│       │   ├── sse-reconnection.ts
│       │   ├── sse-reconnection.test.ts
│       │   ├── csrf-client.ts
│       │   ├── csrf-client.test.ts
│       │   └── shared/
│       │       ├── api-base.ts
│       │       └── api-base.test.ts
│       └── stores/
│           ├── toast.ts
│           └── toast.test.ts
└── tests/
    ├── integration/
    │   ├── chat-flow.test.ts                 ← End-to-end flow
    │   ├── sse-reconnection.test.ts
    │   ├── csrf-token-flow.test.ts
    │   └── error-recovery.test.ts
    ├── component/
    │   └── toast-integration.test.ts         ← Component tests
    └── helpers/
        ├── mock-server.ts                     ← MSW server setup
        ├── factories.ts                       ← Mock data factories
        ├── mock-toast.ts                      ← Mock toast store
        └── test-utils.ts                      ← Shared test utilities
```

**Naming Conventions**:
- Unit tests: `*.test.ts` (co-located with source)
- Integration tests: `tests/integration/*.test.ts`
- Component tests: `tests/component/*.test.ts`
- Test helpers: `tests/helpers/*`

---

### 5.2 Vitest Configuration

**File**: `frontend/vitest.config.ts` (CREATE NEW)

```typescript
import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import path from 'path';

export default defineConfig({
  plugins: [svelte({ hot: !process.env.VITEST })],
  test: {
    // Test environment
    environment: 'jsdom', // Browser-like environment for DOM tests
    globals: true, // Use global describe, it, expect (no imports)

    // Coverage configuration
    coverage: {
      provider: 'v8', // Fast coverage (alternative: 'istanbul')
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: './coverage',

      // Coverage thresholds (CI will fail if below these)
      thresholds: {
        global: {
          branches: 50,
          functions: 50,
          lines: 50,
          statements: 50
        }
      },

      // Per-file thresholds (stricter for critical modules)
      include: ['src/lib/services/**/*.ts', 'src/lib/stores/**/*.ts'],
      exclude: [
        'node_modules',
        'tests',
        '**/*.test.ts',
        '**/*.config.ts',
        '**/types.ts'
      ]
    },

    // Test setup
    setupFiles: ['./tests/setup.ts'],

    // Test execution
    testTimeout: 10000, // 10s timeout for tests
    hookTimeout: 10000,

    // File patterns
    include: ['src/**/*.test.ts', 'tests/**/*.test.ts'],
    exclude: ['node_modules', 'dist', '.svelte-kit']
  },

  resolve: {
    alias: {
      $lib: path.resolve('./src/lib'),
      $components: path.resolve('./src/lib/components'),
      $stores: path.resolve('./src/lib/stores'),
      $types: path.resolve('./src/lib/types'),
      $utils: path.resolve('./src/lib/utils'),
      $api: path.resolve('./src/lib/api'),
      $services: path.resolve('./src/lib/services')
    }
  }
});
```

---

### 5.3 Test Setup File

**File**: `frontend/tests/setup.ts` (CREATE NEW)

```typescript
/**
 * Global test setup
 *
 * Runs once before all tests
 */

import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/svelte';
import * as matchers from '@testing-library/jest-dom/matchers';

// Extend Vitest expect with @testing-library/jest-dom matchers
expect.extend(matchers);

// Cleanup after each test (remove rendered components)
afterEach(() => {
  cleanup();
});

// Mock window.matchMedia (not available in jsdom)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn()
  }))
});

// Mock EventSource (not natively available in jsdom)
global.EventSource = vi.fn().mockImplementation(() => ({
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  close: vi.fn(),
  readyState: 0,
  url: '',
  withCredentials: false
}));
```

---

### 5.4 Package.json Scripts

**File**: `frontend/package.json` (ADD NEW SCRIPTS)

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage",
    "test:unit": "vitest run src/",
    "test:integration": "vitest run tests/integration",
    "test:component": "vitest run tests/component",
    "test:ci": "vitest run --coverage --reporter=verbose",
    "test:debug": "vitest --inspect-brk --no-file-parallelization"
  },
  "devDependencies": {
    "vitest": "^1.2.0",
    "@vitest/ui": "^1.2.0",
    "@vitest/coverage-v8": "^1.2.0",
    "msw": "^2.0.0",
    "@testing-library/svelte": "^4.0.5",
    "@testing-library/jest-dom": "^6.1.5",
    "jsdom": "^27.2.0"
  }
}
```

---

### 5.5 MSW Package Installation

**File**: `frontend/package.json` (ADD MSW)

```bash
cd frontend
npm install -D msw@latest
```

**MSW Setup**:
1. Install MSW: `npm install -D msw@latest`
2. Create `tests/helpers/mock-server.ts` (see section 4.1)
3. Import in test setup: `import { server } from './helpers/mock-server'`
4. Add lifecycle hooks in tests:
   ```typescript
   beforeAll(() => server.listen())
   afterEach(() => server.resetHandlers())
   afterAll(() => server.close())
   ```

---

### 5.6 CI Integration (GitHub Actions)

**File**: `.github/workflows/frontend-tests.yml` (CREATE NEW)

```yaml
name: Frontend Tests

on:
  push:
    branches: [master, develop]
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-tests.yml'
  pull_request:
    branches: [master, develop]
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run unit tests
        run: |
          cd frontend
          npm run test:unit

      - name: Run integration tests
        run: |
          cd frontend
          npm run test:integration

      - name: Generate coverage report
        run: |
          cd frontend
          npm run test:coverage

      - name: Check coverage thresholds
        run: |
          cd frontend
          npm run test:ci

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/lcov.info
          flags: frontend
          name: frontend-coverage

      - name: Comment PR with coverage
        if: github.event_name == 'pull_request'
        uses: codecov/codecov-action@v3
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
```

---

## 6. Regression Prevention Strategy

### 6.1 Contract Testing

**Approach**: Snapshot testing for API request/response structure

**File**: `tests/integration/contract-tests.test.ts`

```typescript
describe('API Contract Tests', () => {
  it('createProject request should match contract', async () => {
    let capturedBody: any = null;

    server.use(
      http.post('/api/projects/create', async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json({ id: 1, ...capturedBody });
      })
    );

    await projectsApi.createProject({
      name: 'Test',
      description: 'Desc'
    });

    // Snapshot test ensures request structure doesn't change
    expect(capturedBody).toMatchSnapshot();
  });

  it('createProject response should match contract', async () => {
    const result = await projectsApi.createProject({
      name: 'Test',
      description: 'Desc'
    });

    // Snapshot test ensures response structure doesn't change
    expect(result).toMatchSnapshot({
      id: expect.any(Number),
      created_at: expect.any(String),
      updated_at: expect.any(String)
    });
  });

  // Similar tests for all API endpoints
});
```

**Benefits**:
- Detect breaking changes in API contracts
- Verify request/response structure
- Prevent accidental property renames

---

### 6.2 E2E Test Validation

**Requirement**: All 10 existing Playwright tests MUST pass

**File**: `tests/e2e/regression.spec.ts` (ADD TO PLAYWRIGHT)

```typescript
import { test, expect } from '@playwright/test';

test.describe('Regression Tests (Ensure Refactoring Didnt Break Anything)', () => {
  test('should create project and send message (E2E)', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // Create project
    await page.click('button:has-text("New Project")');
    await page.fill('input[name="name"]', 'E2E Test Project');
    await page.fill('textarea[name="description"]', 'Testing refactoring');
    await page.click('button:has-text("Create")');

    // Verify project appears in sidebar
    await expect(page.locator('text=E2E Test Project')).toBeVisible();

    // Create conversation
    await page.click('button:has-text("New Chat")');

    // Send message
    await page.fill('textarea[placeholder*="message"]', 'Hello, test');
    await page.press('textarea[placeholder*="message"]', 'Enter');

    // Verify message appears
    await expect(page.locator('text=Hello, test')).toBeVisible();
  });
});
```

**Validation Steps**:
1. Run existing Playwright tests: `npm run test:e2e`
2. Verify all 10 tests pass
3. Add new regression tests for refactored code
4. Baseline: 10/10 passing (100%)

---

### 6.3 Visual Regression Testing (Optional)

**Tool**: Playwright Visual Comparisons

**File**: `tests/e2e/visual-regression.spec.ts`

```typescript
test('sidebar should look the same after refactoring', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Take screenshot of sidebar
  await expect(page.locator('.sidebar')).toHaveScreenshot('sidebar-after-refactor.png');
});
```

**Benefits**:
- Detect unintended UI changes
- Verify CSS/layout unchanged
- Catch visual regressions

**Scope**: OPTIONAL (not required for 50% coverage goal)

---

## 7. Quality Gates

### 7.1 Coverage Requirements (MUST PASS)

| Gate | Threshold | Current | Target | Status |
|------|-----------|---------|--------|--------|
| Overall frontend coverage | ≥ 50% | 15% | 52% | PENDING |
| `projects-api.ts` | ≥ 85% | 0% | 90% | PENDING |
| `conversations-api.ts` | ≥ 85% | 0% | 88% | PENDING |
| `messages-api.ts` | ≥ 85% | 0% | 87% | PENDING |
| `api-base.ts` | ≥ 90% | 0% | 92% | PENDING |
| `sse-client.ts` | ≥ 65% | 0% | 68% | PENDING |
| `sse-reconnection.ts` | ≥ 90% | 0% | 93% | PENDING |
| `csrf-client.ts` | ≥ 95% | 0% | 97% | PENDING |

**Pass Criteria**: ALL gates above thresholds

---

### 7.2 Functional Gates (MUST PASS)

- ✅ All unit tests passing (107/107)
- ✅ All integration tests passing (11/11)
- ✅ All component tests passing (12/12)
- ✅ All existing E2E tests passing (10/10 Playwright)
- ✅ Zero regressions detected

**Pass Criteria**: 100% test pass rate

---

### 7.3 Performance Benchmarks

**Metrics to Track**:

| Metric | Baseline | Target | Max Allowed |
|--------|----------|--------|-------------|
| Test execution time | N/A | < 30s | 60s |
| Bundle size (gzipped) | ~150KB | < 160KB | 180KB |
| API call latency (mock) | N/A | < 10ms | 50ms |
| Memory usage (test suite) | N/A | < 500MB | 1GB |

**Measurement**:
```bash
# Test execution time
npm run test:ci -- --reporter=verbose

# Bundle size
npm run build
du -sh dist/

# Memory usage
node --expose-gc tests/measure-memory.js
```

**File**: `tests/measure-memory.js` (CREATE)

```javascript
// Measure memory usage during test execution
const { exec } = require('child_process');

exec('npm run test:coverage', (error, stdout, stderr) => {
  const memUsage = process.memoryUsage();
  console.log('Memory Usage:');
  console.log(`  RSS: ${(memUsage.rss / 1024 / 1024).toFixed(2)} MB`);
  console.log(`  Heap Used: ${(memUsage.heapUsed / 1024 / 1024).toFixed(2)} MB`);
  console.log(`  Heap Total: ${(memUsage.heapTotal / 1024 / 1024).toFixed(2)} MB`);
});
```

---

### 7.4 Code Quality Gates

**Linting**:
```bash
npm run lint
```

**Type Checking**:
```bash
npm run check
```

**Formatting**:
```bash
npm run format
```

**All MUST pass** before merging refactored code.

---

## 8. Testing Timeline

### 8.1 Time Estimates

| Phase | Tasks | Time (Hours) | Responsible |
|-------|-------|--------------|-------------|
| **Day 1** | MSW setup, test infrastructure, vitest config | 4h | QA-Agent |
| **Day 2** | Write unit tests (projects, conversations, messages) | 8h | QA-Agent |
| **Day 3** | Write unit tests (sse, csrf, api-base) | 6h | QA-Agent |
| **Day 4 AM** | Write integration tests | 3h | QA-Agent |
| **Day 4 PM** | Run tests, fix failures, verify coverage | 3h | QA-Agent |
| **TOTAL** | All testing tasks | **24 hours** | - |

**Breakdown**:
- Infrastructure setup: 4 hours
- Unit test writing: 14 hours (~8 min per test × 107 tests)
- Integration test writing: 3 hours
- Test debugging and coverage validation: 3 hours

**Parallelization**: If Frontend-Agent helps write tests, timeline reduces to 2 days.

---

### 8.2 Test Execution Time

**Unit Tests**: ~15 seconds (107 tests)
**Integration Tests**: ~20 seconds (11 tests with SSE)
**Component Tests**: ~5 seconds (12 tests)
**E2E Tests (Playwright)**: ~45 seconds (10 tests)

**Total CI Pipeline Time**: ~85 seconds

---

## 9. Risk Assessment

### 9.1 What Could We Miss?

**Blind Spots**:

1. **EventSource Edge Cases**:
   - Network interruptions during stream
   - Browser closing tab mid-stream
   - Server restarting during connection
   - **Mitigation**: Integration tests + manual testing

2. **CSRF Token Race Conditions**:
   - Multiple API calls simultaneously while token expired
   - Token refresh during long-running request
   - **Mitigation**: Integration test with concurrent requests

3. **Toast Notification Timing**:
   - Toast shown before user sees response
   - Multiple toasts stacking
   - **Mitigation**: Component tests with @testing-library

4. **Browser Compatibility**:
   - EventSource not supported in IE11 (acceptable)
   - Fetch API polyfill needed for old browsers
   - **Mitigation**: Document browser support requirements

5. **Memory Leaks**:
   - EventSource not properly closed
   - Event listeners not removed
   - **Mitigation**: Manual testing + Chrome DevTools profiling

6. **SSE Streaming Edge Cases**:
   - Empty tokens (whitespace-only)
   - Very long tokens (> 1KB)
   - Malformed JSON events
   - **Mitigation**: Add edge case tests

---

### 9.2 Testing Gaps

**NOT Covered by Unit/Integration Tests**:

1. **Visual Appearance**:
   - Toast colors correct
   - Message bubbles aligned
   - Sidebar responsive
   - **Mitigation**: E2E tests + manual testing

2. **Accessibility (a11y)**:
   - Screen reader support
   - Keyboard navigation
   - ARIA labels
   - **Mitigation**: Manual testing with screen reader

3. **Network Conditions**:
   - Slow 3G connection
   - High latency (500ms+)
   - Packet loss
   - **Mitigation**: Manual testing with Chrome DevTools throttling

4. **Concurrency**:
   - Multiple tabs open
   - Multiple users
   - Race conditions
   - **Mitigation**: Manual testing + load testing (out of scope)

5. **Security**:
   - XSS attacks in markdown
   - CSRF token hijacking
   - SQL injection (backend)
   - **Mitigation**: Security testing phase (separate)

---

### 9.3 Mitigation Strategies

**Strategy 1: Layered Testing**:
- Unit tests: Cover functions in isolation
- Integration tests: Cover module interactions
- Component tests: Cover UI feedback
- E2E tests: Cover user workflows
- Manual testing: Cover edge cases, UX, accessibility

**Strategy 2: Continuous Monitoring**:
- CI pipeline runs tests on every commit
- Coverage report on every PR
- Performance benchmarks tracked over time

**Strategy 3: Risk-Based Prioritization**:
- CRITICAL modules (csrf, api-base): 90-95% coverage
- HIGH modules (API functions): 85% coverage
- MEDIUM modules (SSE): 65% coverage
- LOW modules (utils): 50% coverage

**Strategy 4: Incremental Validation**:
- Test each refactored module immediately after creation
- Run tests before committing
- Verify E2E tests after each milestone

---

## 10. Validation Plan for Refactoring

### 10.1 Step-by-Step Validation During Refactoring

**CRITICAL: Test Continuously, Not at the End**

#### Phase 1: Refactor `api-client.ts` → 3 files

**Step 1**: Create `api-base.ts` (shared utilities)
- Write unit tests: `api-base.test.ts` (15 tests)
- Run: `npm run test src/lib/services/shared/api-base.test.ts`
- Verify: All 15 tests pass
- Check coverage: `npm run test:coverage -- src/lib/services/shared/api-base.ts`
- Gate: ≥ 90% coverage

**Step 2**: Create `projects-api.ts` (extract from api-client.ts)
- Write unit tests: `projects-api.test.ts` (18 tests)
- Run: `npm run test src/lib/services/projects-api.test.ts`
- Verify: All 18 tests pass
- Check coverage: ≥ 85%

**Step 3**: Create `conversations-api.ts`
- Write unit tests: `conversations-api.test.ts` (22 tests)
- Run tests
- Verify coverage: ≥ 85%

**Step 4**: Create `messages-api.ts`
- Write unit tests: `messages-api.test.ts` (12 tests)
- Run tests
- Verify coverage: ≥ 85%

**Step 5**: Delete old `api-client.ts`
- Update all imports in components
- Run: `npm run test` (all unit tests)
- Run: `npm run test:e2e` (all Playwright tests)
- Verify: No regressions

**Gate Before Proceeding**: ALL tests passing, coverage ≥ 85%

---

#### Phase 2: Refactor `sse-client.ts` → 2 files

**Step 1**: Create `csrf-client.ts` (extract CSRF logic)
- Write unit tests: `csrf-client.test.ts` (8 tests)
- Run tests
- Verify coverage: ≥ 95%

**Step 2**: Create `sse-reconnection.ts` (extract retry logic)
- Write unit tests: `sse-reconnection.test.ts` (10 tests)
- Run tests
- Verify coverage: ≥ 90%

**Step 3**: Refactor `sse-client.ts` (use new modules)
- Write unit tests: `sse-client.test.ts` (12 tests)
- Run tests
- Verify coverage: ≥ 65%

**Step 4**: Update all SSE usage in components
- Update imports
- Run: `npm run test`
- Run: `npm run test:e2e`
- Verify: No regressions

**Gate Before Proceeding**: ALL tests passing, coverage ≥ 65%

---

#### Phase 3: Integration Testing

**Step 1**: Write integration tests
- `tests/integration/chat-flow.test.ts`
- `tests/integration/sse-reconnection.test.ts`
- `tests/integration/csrf-token-flow.test.ts`
- `tests/integration/error-recovery.test.ts`

**Step 2**: Run all integration tests
- Run: `npm run test:integration`
- Verify: All 11 tests pass

**Step 3**: Verify coverage gate
- Run: `npm run test:coverage`
- Check report: Overall ≥ 50%

---

#### Phase 4: Final Validation

**Step 1**: Run complete test suite
```bash
npm run test:ci
```

**Step 2**: Verify coverage thresholds
```
✓ Overall: 52% (≥ 50%)
✓ projects-api.ts: 90% (≥ 85%)
✓ conversations-api.ts: 88% (≥ 85%)
✓ messages-api.ts: 87% (≥ 85%)
✓ api-base.ts: 92% (≥ 90%)
✓ sse-client.ts: 68% (≥ 65%)
✓ sse-reconnection.ts: 93% (≥ 90%)
✓ csrf-client.ts: 97% (≥ 95%)
```

**Step 3**: Run E2E tests
```bash
npm run test:e2e
```

**Verify**: 10/10 Playwright tests pass (no regressions)

**Step 4**: Manual smoke testing
- Create project
- Create conversation
- Send message
- Verify SSE streaming works
- Delete conversation
- Delete project

**Step 5**: Git checkpoint
```bash
git add .
git commit -m "Stage 1 Phase 5: Frontend refactoring complete (50% coverage achieved)"
```

---

### 10.2 When to Run Which Tests

**During Development** (continuous):
- Run unit tests for current module: `npm run test -- src/lib/services/projects-api.test.ts`
- Watch mode: `npm run test:watch`

**After Each Module** (gating):
- Run all unit tests: `npm run test:unit`
- Check coverage: `npm run test:coverage`

**After Refactoring Complete** (final validation):
- Run all tests: `npm run test`
- Run integration tests: `npm run test:integration`
- Run E2E tests: `npm run test:e2e`
- Check coverage: `npm run test:coverage`

**Before Git Commit** (pre-commit hook):
```bash
npm run lint && npm run check && npm run test
```

**CI Pipeline** (automated):
```bash
npm run test:ci
```

---

### 10.3 Continuous Validation Approach

**Philosophy**: Test-Driven Refactoring (TDR)

**Process**:
1. **Before refactoring**: Write tests for existing behavior
2. **During refactoring**: Keep tests passing
3. **After refactoring**: Add tests for new functionality

**Benefits**:
- Catch regressions immediately
- Refactor with confidence
- Document expected behavior
- Enable safe future changes

**Example Workflow**:
```bash
# 1. Write test for existing api-client.ts function
npm run test:watch

# 2. Extract function to new file (e.g., projects-api.ts)
# Tests still pass (behavior unchanged)

# 3. Update imports
# Tests still pass

# 4. Delete old code
# Tests still pass

# 5. Add new tests for edge cases
# Coverage increases
```

---

## 11. Questions for Super-AI & Frontend-Agent

### 11.1 Architecture Questions

**Q1**: Should we use dependency injection for API client?
- Current: Direct imports (`import { createProject } from './projects-api'`)
- Alternative: Inject via context (`const api = useAPI()`)
- Trade-off: Testability vs simplicity

**Q2**: Should we create a global SSE manager?
- Current: Create new SSEClient() per conversation
- Alternative: Singleton SSEManager managing all connections
- Trade-off: Memory efficiency vs complexity

**Q3**: Should we implement request deduplication?
- Scenario: User clicks "Create Project" twice rapidly
- Current: Sends 2 requests
- Alternative: Debounce or deduplicate identical requests
- Trade-off: Complexity vs UX robustness

---

### 11.2 Testing Concerns

**Q4**: How to test EventSource comprehensively?
- Problem: EventSource is hard to mock in jsdom
- Current approach: Mock global.EventSource
- Alternative: Use real EventSource with test server
- Question: Is mocking sufficient or do we need real SSE?

**Q5**: Should we add visual regression tests?
- Tool: Playwright visual comparisons
- Scope: Screenshots of sidebar, chat interface
- Trade-off: Confidence vs CI time increase
- Question: Is this overkill for refactoring?

**Q6**: Should we test browser compatibility explicitly?
- Browsers: Chrome, Firefox, Safari, Edge
- Current: Only test in jsdom (simulated browser)
- Alternative: Run tests in real browsers via Playwright
- Question: Is cross-browser testing needed?

---

### 11.3 Coverage Questions

**Q7**: Is 50% overall coverage sufficient?
- Current target: 50%
- Industry standard: 70-80% for production apps
- Trade-off: Speed vs thoroughness
- Question: Should we aim higher (60-70%)?

**Q8**: Should we test error boundaries?
- Scenario: EventSource throws unexpected error
- Current: Only test expected errors (403, 500, network)
- Alternative: Test unexpected errors (malformed JSON, etc.)
- Question: How deep should error testing go?

**Q9**: Should we add mutation testing?
- Tool: Stryker Mutator
- Purpose: Test if tests actually catch bugs
- Trade-off: Time vs confidence in tests
- Question: Is this needed for refactoring validation?

---

### 11.4 Timeline Questions

**Q10**: Can timeline be compressed?
- Current estimate: 4 days (24 hours)
- If Frontend-Agent helps: 2 days (12 hours each)
- Trade-off: Speed vs QA thoroughness
- Question: Should we parallelize test writing?

---

## 12. Success Criteria Summary

### 12.1 Coverage Gates (MANDATORY)

✅ Overall frontend coverage: ≥ 50%
✅ Critical modules (api-base, csrf): ≥ 90%
✅ API modules (projects, conversations, messages): ≥ 85%
✅ SSE modules: ≥ 65%

### 12.2 Functional Gates (MANDATORY)

✅ All unit tests passing (107/107)
✅ All integration tests passing (11/11)
✅ All component tests passing (12/12)
✅ All E2E tests passing (10/10)
✅ Zero regressions detected

### 12.3 Quality Gates (MANDATORY)

✅ npm run lint (no errors)
✅ npm run check (TypeScript type check passes)
✅ npm run format (code formatted)
✅ Test execution time < 30 seconds
✅ No flaky tests (run 10 times, all pass)

### 12.4 Performance Gates (NICE-TO-HAVE)

✅ Bundle size increase < 10KB
✅ API mock latency < 10ms
✅ Memory usage < 500MB

---

## 13. Deliverables

### 13.1 Test Files (107 tests total)

**Unit Tests** (75 tests):
- `src/lib/services/projects-api.test.ts` (18 tests)
- `src/lib/services/conversations-api.test.ts` (22 tests)
- `src/lib/services/messages-api.test.ts` (12 tests)
- `src/lib/services/shared/api-base.test.ts` (15 tests)
- `src/lib/services/sse-client.test.ts` (12 tests)
- `src/lib/services/sse-reconnection.test.ts` (10 tests)
- `src/lib/services/csrf-client.test.ts` (8 tests)
- `src/lib/stores/toast.test.ts` (10 tests)

**Integration Tests** (11 tests):
- `tests/integration/chat-flow.test.ts` (1 test)
- `tests/integration/sse-reconnection.test.ts` (3 tests)
- `tests/integration/csrf-token-flow.test.ts` (4 tests)
- `tests/integration/error-recovery.test.ts` (3 tests)

**Component Tests** (12 tests):
- `tests/component/toast-integration.test.ts` (12 tests)

**E2E Regression Tests** (10 tests):
- Existing Playwright tests (must all pass)

---

### 13.2 Test Infrastructure

- `vitest.config.ts` - Vitest configuration
- `tests/setup.ts` - Global test setup
- `tests/helpers/mock-server.ts` - MSW server
- `tests/helpers/factories.ts` - Mock data factories
- `tests/helpers/mock-toast.ts` - Mock toast store
- `.github/workflows/frontend-tests.yml` - CI pipeline

---

### 13.3 Documentation

- This testing strategy document
- Coverage report (HTML + JSON)
- Test execution logs
- Performance benchmarks

---

## 14. Conclusion

This comprehensive testing strategy ensures that the frontend refactoring achieves 50% coverage while preventing regressions. The layered approach (unit → integration → component → E2E) provides confidence at every level.

**Key Success Factors**:
1. **Test-Driven Refactoring**: Write tests before extracting code
2. **Continuous Validation**: Run tests after every change
3. **Coverage Gates**: Enforce thresholds in CI
4. **Layered Testing**: Unit, integration, component, E2E
5. **MSW for Realism**: Test actual fetch logic, not mocks

**Risk Mitigation**:
- Multiple test layers catch different bug types
- E2E tests catch integration issues
- Coverage gates prevent untested code
- CI pipeline prevents regressions

**Timeline**: 4 days (24 hours) for complete implementation

**Confidence Level**: HIGH (comprehensive strategy with clear gates)

---

**Next Steps**:
1. Super-AI reviews and approves strategy
2. Frontend-Agent reviews architecture concerns
3. QA-Agent begins implementation (Day 1: Infrastructure setup)
4. Continuous validation during refactoring
5. Final approval after all gates pass

**This testing strategy ensures Stage 1 perfection. No broken code reaches production.**
