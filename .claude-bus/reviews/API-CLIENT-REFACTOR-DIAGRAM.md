# API Client Refactoring - Architecture Diagram

## Before Refactoring

```
frontend/src/lib/services/
└── api-client.ts (471 lines)
    ├── fetchProjects()
    ├── fetchProject(id)
    ├── createProject(data)
    ├── deleteProject(id)
    ├── fetchConversations(projectId?)
    ├── fetchConversation(id)
    ├── createConversation(data)
    ├── updateConversation(id, data)
    ├── deleteConversation(id)
    ├── fetchMessages(conversationId)
    └── updateMessageReaction(messageId, reaction)

    Issues:
    ❌ Monolithic 471-line file
    ❌ Repetitive error handling (11 copies)
    ❌ Hard to test (all or nothing)
    ❌ Difficult to extend
```

## After Refactoring (Day 1)

```
frontend/src/lib/services/
├── api/
│   ├── base.ts (100 lines)
│   │   ├── apiRequest<T>()              ← Core fetch wrapper
│   │   ├── ApiRequestOptions            ← Type-safe options
│   │   └── getErrorMessage()            ← Centralized error mapping
│   │
│   ├── projects.ts (90 lines)
│   │   ├── fetchProjects()              ← GET /api/projects/list
│   │   ├── fetchProject(id)             ← GET /api/projects/:id
│   │   ├── createProject()              ← POST /api/projects/create
│   │   ├── updateProject()              ← PATCH /api/projects/:id
│   │   ├── deleteProject()              ← DELETE /api/projects/:id
│   │   └── getProjectStats()            ← GET /api/projects/:id/stats
│   │
│   └── index.ts (19 lines)
│       └── Barrel exports for clean imports
│
└── core/ (empty - reserved for future)

Benefits:
✅ Modular structure (209 total lines)
✅ DRY error handling (single implementation)
✅ Easy to test (isolated modules)
✅ Clear extension pattern
```

## After Refactoring (Day 2 - Planned)

```
frontend/src/lib/services/
├── api/
│   ├── base.ts (100 lines)
│   │   └── Shared fetch wrapper
│   │
│   ├── projects.ts (90 lines)
│   │   └── Project CRUD + stats
│   │
│   ├── conversations.ts (~100 lines)
│   │   ├── fetchConversations()
│   │   ├── fetchConversation(id)
│   │   ├── createConversation()
│   │   ├── updateConversation()
│   │   └── deleteConversation()
│   │
│   ├── messages.ts (~80 lines)
│   │   ├── fetchMessages()
│   │   └── updateMessageReaction()
│   │
│   ├── chat.ts (~60 lines)
│   │   └── SSE streaming utilities (if needed)
│   │
│   └── index.ts (25 lines)
│       └── Export all modules
│
└── core/ (future)
    └── Shared utilities

Total: ~455 lines (vs 471 original)
Files: 6 modular files (vs 1 monolithic)
```

## Error Handling Flow

### Before (Repetitive)
```typescript
// api-client.ts - repeated 11 times
export async function fetchProjects(): Promise<ProjectListResponse> {
  try {
    const response = await fetch(API_ENDPOINTS.projects.list);

    if (!response.ok) {
      const error = await response.json();
      const message = getErrorMessage(error);  // ← Repeated
      toast.error(`Failed to load: ${message}`);  // ← Repeated
      throw new Error(error.detail || 'Failed');
    }

    return await response.json();
  } catch (err) {
    if (err instanceof TypeError) {  // ← Repeated
      toast.error('Network error');  // ← Repeated
    }
    throw err;
  }
}
```

### After (DRY)
```typescript
// projects.ts - all functions use shared wrapper
export async function fetchProjects(): Promise<ProjectListResponse> {
  return apiRequest<ProjectListResponse>(API_ENDPOINTS.projects.list);
  // ← Error handling automatic via apiRequest()
}

// base.ts - single implementation
export async function apiRequest<T>(endpoint: string, options?: ApiRequestOptions) {
  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      const message = customErrorMessage || getErrorMessage(response.status, error);

      if (!skipErrorToast) {
        toast.error(message);  // ← Single implementation
      }

      throw new Error(error.detail || message);
    }

    return await response.json();
  } catch (err) {
    if (err instanceof TypeError) {  // ← Single implementation
      const message = 'Network error. Please check your connection.';
      if (!skipErrorToast) {
        toast.error(message);
      }
      throw new Error(message);
    }
    throw err;
  }
}
```

## Import Usage

### Before
```typescript
// Component imports (old)
import {
  fetchProjects,
  createProject,
  deleteProject
} from '$lib/services/api-client';

const projects = await fetchProjects();
await createProject({ name: 'Test' });
```

### After
```typescript
// Component imports (new - Day 2 update)
import { projectsApi } from '$lib/services/api';

const projects = await projectsApi.fetchProjects();
await projectsApi.createProject('Test', 'Description');

// Or namespace import
import * as api from '$lib/services/api';
const projects = await api.projectsApi.fetchProjects();
```

## Testing Strategy

### Before (Difficult)
```typescript
// Had to mock entire api-client.ts
vi.mock('$lib/services/api-client', () => ({
  fetchProjects: vi.fn(),
  fetchProject: vi.fn(),
  createProject: vi.fn(),
  // ... 8 more functions
}));
```

### After (Easy)
```typescript
// Test base module in isolation
describe('apiRequest', () => {
  it('should handle 404 errors', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({ ok: false, status: 404 })
    );

    await expect(apiRequest('/test')).rejects.toThrow('Resource not found');
  });
});

// Test projects module with mocked base
vi.mock('./base', () => ({
  apiRequest: vi.fn()
}));

describe('fetchProjects', () => {
  it('should call apiRequest with correct endpoint', async () => {
    await fetchProjects();
    expect(apiRequest).toHaveBeenCalledWith('/api/projects/list');
  });
});
```

## File Size Comparison

| Module | Before | After | Change |
|--------|--------|-------|--------|
| Base utilities | 0 lines | 100 lines | +100 (new) |
| Projects API | ~150 lines | 90 lines | -60 (40% reduction) |
| Conversations API | ~200 lines | ~100 lines | -100 (50% reduction) |
| Messages API | ~100 lines | ~80 lines | -20 (20% reduction) |
| Chat/SSE utilities | ~21 lines | ~60 lines | +39 (separated) |
| Barrel exports | 0 lines | 25 lines | +25 (new) |
| **Total** | **471 lines** | **455 lines** | **-16 lines (3% reduction)** |
| **Files** | **1 file** | **6 files** | **+5 files** |

**Key Insight**: Same functionality, better organization. Slight line reduction comes from eliminating repetitive error handling code.

## Code Quality Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Max file size | 471 lines | 100 lines | < 400 lines |
| DRY violations | 11 copies | 0 copies | 0 |
| Testability | Low | High | High |
| Maintainability | Low | High | High |
| Type safety | ✅ Yes | ✅ Yes | Yes |
| Documentation | Partial | Full JSDoc | Full |

## Next Steps (Day 2)

1. ✅ Create `api/conversations.ts` (~100 lines)
2. ✅ Create `api/messages.ts` (~80 lines)
3. ✅ Create `api/chat.ts` (~60 lines, if needed)
4. ✅ Update barrel exports in `api/index.ts`
5. ✅ Update all component imports (replace api-client imports)
6. ✅ Delete old `api-client.ts`
7. ✅ Verify all components compile
8. ✅ Verify runtime functionality

## Architecture Principles Applied

1. **Single Responsibility**: Each module handles one domain
2. **DRY (Don't Repeat Yourself)**: Shared error handling in base
3. **Open/Closed**: Easy to add new API modules without modifying existing
4. **Interface Segregation**: Components import only what they need
5. **Dependency Inversion**: Components depend on api module interface, not implementation

---

**Created**: 2025-11-24
**Author**: Frontend-Agent
