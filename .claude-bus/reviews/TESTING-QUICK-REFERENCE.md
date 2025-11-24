# Testing Quick Reference Guide
**Date**: 2025-11-24
**QA Agent**: Claude QA-Agent (Sonnet 4.5)

---

## Quick Commands

### Run Tests
```bash
# Run all tests
npm run test

# Run tests in watch mode (auto-rerun on file change)
npm run test:watch

# Run specific test file
npm run test src/lib/services/projects-api.test.ts

# Run tests matching pattern
npm run test -- projects

# Run with UI (interactive test explorer)
npm run test:ui
```

### Coverage
```bash
# Generate coverage report
npm run test:coverage

# View HTML coverage report
open coverage/index.html

# Check coverage for specific file
npm run test:coverage -- src/lib/services/projects-api.ts
```

### Test Types
```bash
# Run only unit tests
npm run test:unit

# Run only integration tests
npm run test:integration

# Run only component tests
npm run test:component

# Run E2E tests (Playwright)
npm run test:e2e
```

### CI/Debug
```bash
# Run tests in CI mode (verbose, no watch)
npm run test:ci

# Debug tests (attach debugger)
npm run test:debug

# Run tests 10 times (flaky test detection)
for i in {1..10}; do npm run test; done
```

---

## Test File Template

### Unit Test Template

```typescript
/**
 * Unit tests for [module name]
 *
 * Purpose: [What this module does]
 * Coverage Target: [X%]
 */

import { describe, it, expect, beforeAll, afterAll, afterEach, vi } from 'vitest';
import { server } from '../../../tests/helpers/mock-server';
import { http, HttpResponse } from 'msw';
import * as moduleToTest from './module-to-test';

// Mock dependencies
vi.mock('$lib/stores/toast', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn()
  },
  getErrorMessage: vi.fn((err) => err.detail || 'Error')
}));

describe('[ModuleName]', () => {
  // MSW setup
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  describe('[functionName]', () => {
    it('should [expected behavior]', async () => {
      // Arrange: Set up test data
      const input = { /* test input */ };

      // Act: Call function
      const result = await moduleToTest.functionName(input);

      // Assert: Verify results
      expect(result).toBeDefined();
      expect(result.property).toBe('expected value');
    });

    it('should handle error [error scenario]', async () => {
      // Arrange: Mock error response
      server.use(
        http.post('/api/endpoint', () => {
          return HttpResponse.json(
            { detail: 'Error message' },
            { status: 400 }
          );
        })
      );

      // Act + Assert: Expect rejection
      await expect(
        moduleToTest.functionName(input)
      ).rejects.toThrow();
    });
  });
});
```

---

### Integration Test Template

```typescript
/**
 * Integration test: [Test scenario name]
 *
 * Purpose: Test interaction between multiple modules
 */

import { describe, it, expect } from 'vitest';
import * as module1 from '$lib/services/module1';
import * as module2 from '$lib/services/module2';

describe('Integration: [Scenario Name]', () => {
  it('should handle complete workflow', async () => {
    // Step 1: First operation
    const result1 = await module1.operation1();
    expect(result1).toBeDefined();

    // Step 2: Second operation using result from step 1
    const result2 = await module2.operation2(result1.id);
    expect(result2).toBeDefined();

    // Step 3: Verify final state
    const finalState = await module1.getState();
    expect(finalState).toMatchObject({
      /* expected state */
    });
  });
});
```

---

### Component Test Template

```typescript
/**
 * Component tests for [ComponentName]
 *
 * Purpose: Test UI behavior and user interactions
 */

import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import ComponentName from './ComponentName.svelte';

describe('ComponentName', () => {
  it('should render correctly', () => {
    const { container } = render(ComponentName, {
      props: { /* component props */ }
    });

    // Verify rendered content
    expect(container.textContent).toContain('expected text');
  });

  it('should handle user interaction', async () => {
    const { container, component } = render(ComponentName);

    // Find and click button
    const button = container.querySelector('button');
    await fireEvent.click(button);

    // Verify result
    expect(component.someState).toBe('expected value');
  });
});
```

---

## MSW Handler Examples

### Success Response
```typescript
http.get('/api/projects/list', () => {
  return HttpResponse.json({
    projects: [
      { id: 1, name: 'Project 1' },
      { id: 2, name: 'Project 2' }
    ],
    total: 2
  });
});
```

### Error Response
```typescript
http.post('/api/projects/create', () => {
  return HttpResponse.json(
    { detail: 'Validation failed' },
    { status: 400 }
  );
});
```

### Network Error
```typescript
http.get('/api/projects/list', () => {
  return HttpResponse.error();
});
```

### Dynamic Response
```typescript
http.get('/api/projects/:id', ({ params }) => {
  const id = Number(params.id);
  return HttpResponse.json({
    id,
    name: `Project ${id}`
  });
});
```

### Capture Request
```typescript
http.post('/api/projects/create', async ({ request }) => {
  const body = await request.json();
  const headers = request.headers;

  // Verify request
  console.log('Request body:', body);
  console.log('CSRF token:', headers.get('X-CSRF-Token'));

  return HttpResponse.json({ id: 1, ...body });
});
```

---

## Common Test Patterns

### Test API Success
```typescript
it('should create project successfully', async () => {
  const result = await projectsApi.createProject({
    name: 'Test',
    description: 'Desc'
  });

  expect(result.id).toBeDefined();
  expect(result.name).toBe('Test');
  expect(toast.success).toHaveBeenCalled();
});
```

### Test API Error
```typescript
it('should handle 404 error', async () => {
  server.use(
    http.get('/api/projects/:id', () => {
      return HttpResponse.json(
        { detail: 'Not found' },
        { status: 404 }
      );
    })
  );

  await expect(
    projectsApi.fetchProject(999)
  ).rejects.toThrow();

  expect(toast.error).toHaveBeenCalledWith(
    expect.stringContaining('not found')
  );
});
```

### Test CSRF Token Included
```typescript
it('should include CSRF token in request', async () => {
  let capturedHeaders: Headers | null = null;

  server.use(
    http.post('/api/endpoint', ({ request }) => {
      capturedHeaders = request.headers;
      return HttpResponse.json({ success: true });
    })
  );

  await apiFunction();

  expect(capturedHeaders?.get('X-CSRF-Token')).toBeTruthy();
});
```

### Test Retry on 403
```typescript
it('should retry on 403', async () => {
  let callCount = 0;

  server.use(
    http.post('/api/endpoint', () => {
      callCount++;
      if (callCount === 1) {
        return HttpResponse.json(
          { detail: 'Token expired' },
          { status: 403 }
        );
      } else {
        return HttpResponse.json({ success: true });
      }
    })
  );

  const result = await apiFunction();

  expect(callCount).toBe(2); // Retried once
  expect(result.success).toBe(true);
});
```

### Test Network Error
```typescript
it('should handle network error', async () => {
  server.use(
    http.post('/api/endpoint', () => {
      return HttpResponse.error();
    })
  );

  await expect(apiFunction()).rejects.toThrow();

  expect(toast.error).toHaveBeenCalledWith(
    expect.stringContaining('Network error')
  );
});
```

### Test Payload Structure
```typescript
it('should send correct payload', async () => {
  let capturedBody: any = null;

  server.use(
    http.post('/api/endpoint', async ({ request }) => {
      capturedBody = await request.json();
      return HttpResponse.json({ success: true });
    })
  );

  await apiFunction({ name: 'Test', value: 123 });

  expect(capturedBody).toEqual({
    name: 'Test',
    value: 123
  });
});
```

---

## Coverage Thresholds

### Global Thresholds (vitest.config.ts)
```typescript
coverage: {
  thresholds: {
    global: {
      branches: 50,
      functions: 50,
      lines: 50,
      statements: 50
    }
  }
}
```

### Per-File Thresholds
```typescript
coverage: {
  thresholds: {
    'src/lib/services/api-base.ts': {
      branches: 90,
      functions: 90,
      lines: 90
    },
    'src/lib/services/csrf-client.ts': {
      branches: 95,
      functions: 95,
      lines: 95
    }
  }
}
```

---

## Debugging Tips

### Enable Console Logs
```typescript
// In test file
import { vi } from 'vitest';

// Don't suppress console in this test
vi.spyOn(console, 'log').mockImplementation(() => {});
```

### Inspect Component HTML
```typescript
const { container } = render(Component);
console.log(container.innerHTML); // See rendered HTML
```

### Pause Test Execution
```typescript
it('should do something', async () => {
  debugger; // Pause here (run with --inspect-brk)
  const result = await apiFunction();
});
```

### Check MSW Handlers
```typescript
// In test
server.events.on('request:start', ({ request }) => {
  console.log('Request:', request.method, request.url);
});
```

### View Coverage Gaps
```bash
npm run test:coverage
open coverage/index.html
# Red = uncovered, yellow = partially covered, green = covered
```

---

## CI Pipeline Integration

### GitHub Actions Workflow
```yaml
- name: Run Frontend Tests
  run: |
    cd frontend
    npm ci
    npm run test:ci

- name: Check Coverage
  run: |
    cd frontend
    npm run test:coverage

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./frontend/coverage/lcov.info
```

---

## Performance Optimization

### Reduce Test Time
```typescript
// Use beforeAll instead of beforeEach when possible
beforeAll(() => {
  // Setup once
});

// Use parallel execution
vitest.config.ts:
  test: {
    threads: true,
    maxThreads: 4
  }
```

### Reduce Bundle Size
```bash
# Analyze bundle
npm run build -- --mode=analyze

# Check gzip size
npm run build
gzip -k dist/assets/*.js
ls -lh dist/assets/*.js.gz
```

---

## Common Issues

### Issue: "EventSource is not defined"
**Solution**: Mock EventSource in test setup
```typescript
// tests/setup.ts
global.EventSource = vi.fn().mockImplementation(() => ({
  addEventListener: vi.fn(),
  close: vi.fn()
}));
```

### Issue: "Cannot find module '$lib/...'"
**Solution**: Add path alias in vitest.config.ts
```typescript
resolve: {
  alias: {
    $lib: path.resolve('./src/lib')
  }
}
```

### Issue: Tests fail in CI but pass locally
**Solution**: Check timezone/locale differences
```typescript
// Mock Date in tests
global.Date = class extends Date {
  constructor() {
    super('2025-11-24T00:00:00Z'); // Fixed time
  }
};
```

### Issue: Coverage report shows 0%
**Solution**: Ensure include/exclude patterns correct
```typescript
// vitest.config.ts
coverage: {
  include: ['src/lib/services/**/*.ts'],
  exclude: ['**/*.test.ts']
}
```

---

## Useful Resources

- **Vitest Docs**: https://vitest.dev/
- **MSW Docs**: https://mswjs.io/
- **Testing Library**: https://testing-library.com/docs/svelte-testing-library/intro
- **Playwright**: https://playwright.dev/

---

## Quality Checklist

Before committing:
- [ ] All tests pass: `npm run test`
- [ ] Coverage ≥ thresholds: `npm run test:coverage`
- [ ] No lint errors: `npm run lint`
- [ ] Types valid: `npm run check`
- [ ] Code formatted: `npm run format`
- [ ] E2E tests pass: `npm run test:e2e`

---

**This quick reference provides all commands and patterns needed for efficient testing.**
