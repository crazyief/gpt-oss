# Stage 1 Final Refactoring - Execution Plan v2 (70% Coverage)

**Approved by User**: 2025-11-24
**Plan Version**: Option B-2 (MCP-Enhanced Hybrid) - 70% Coverage
**Timeline**: 7 days (42-48 hours)
**Assigned Agents**: Frontend-Agent, QA-Agent, Super-AI-UltraThink (advisor)

---

## 🎯 Scope (User Approved - Updated for 70% Coverage)

### ✅ INCLUDED
1. **API Client Refactoring** - 471 lines → 3 files @ ~100 lines
2. **CSRF Token Implementation** - Token-based protection
3. **Frontend Unit Tests** - Vitest (144 tests, increased from 107)
4. **Frontend Integration Tests** - Vitest + MSW (23 tests, increased from 11)
5. **Playwright MCP Component Tests** - Real browser (15 tests, increased from 12)
6. **Playwright MCP E2E Tests** - Full workflows (12 existing + 6 new = 18 tests)
7. **Chrome DevTools Visual Regression** - Screenshot comparison (5 tests)
8. **Chrome DevTools Performance Testing** - Core Web Vitals (3 tests)

**Total Tests**: 208 tests (vs 148 previously)
**Coverage Target**: 70% (vs 52% previously)

**Test Pyramid Distribution**:
- Unit: 144 tests (69%) ✅ Target: 55-65% (slightly above, acceptable)
- Integration: 23 tests (11%) ✅ Target: 15-25% (slightly below, will add more)
- Component: 15 tests (7%) ✅ Target: 5-15%
- E2E: 18 tests (9%) ✅ Target: 5-15%
- Visual: 5 tests (2%)
- Performance: 3 tests (1%)

**Revised Distribution (balanced pyramid)**:
- Unit: 125 tests (60%) ✅
- Integration: 42 tests (20%) ✅
- Component: 21 tests (10%) ✅
- E2E: 20 tests (10%) ✅
- Visual: 5 tests
- Performance: 3 tests
- **Total: 216 tests for 70% coverage**

### ❌ EXCLUDED (Deferred to Stage 2)
- SSE Client Refactoring (458 lines is acceptable, only 1 consumer)

---

## 📊 Coverage Calculation

**Current codebase stats** (estimated):
- Total lines of code: ~1,500 lines (frontend/src/lib/)
- Currently untested lines: ~1,100 lines (26% coverage from existing 10 E2E tests)
- Target tested lines: 1,050 lines (70%)
- Additional coverage needed: 1,050 - 390 = 660 lines

**Test allocation to achieve 70%**:
- 125 unit tests @ 5 lines coverage each = 625 lines
- 42 integration tests @ 8 lines coverage each = 336 lines
- 21 component tests @ 15 lines coverage each = 315 lines
- 20 E2E tests @ 30 lines coverage each = 600 lines
- **Total coverage: 1,876 lines (some overlap expected, final: ~70%)**

---

## 📅 Execution Timeline (7 Days)

### Day 1: Monday (6 hours)
**Phase 1: API Client Refactoring - Part 1**
- 09:00-10:00: Create directory structure (api/, core/, shared/)
- 10:00-12:00: Implement `api/base.ts` (shared fetch wrapper with error handling)
- 12:00-13:00: Lunch break
- 13:00-15:00: Implement `api/projects.ts` (5 functions)

**Deliverables**:
- api/base.ts (80 lines) ✅
- api/projects.ts (100 lines) ✅

---

### Day 2: Tuesday (8 hours)
**Phase 1: API Client Refactoring - Part 2**
- 09:00-11:00: Implement `api/conversations.ts` (6 functions)
- 11:00-12:00: Implement `api/messages.ts` (3 functions)
- 12:00-13:00: Lunch break
- 13:00-14:00: Implement `api/index.ts` (barrel exports)
- 14:00-16:00: Update 5 component imports (ChatInterface, ProjectSelector, etc.)
- 16:00-17:00: Manual testing of all API functions

**Deliverables**:
- api/conversations.ts (120 lines) ✅
- api/messages.ts (60 lines) ✅
- api/index.ts (barrel exports) ✅
- All components updated ✅

---

### Day 3: Wednesday (8 hours)
**Phase 2: CSRF Implementation**
- 09:00-11:00: Create `core/csrf.ts` (token fetch, cache, lazy loading)
- 11:00-12:00: Backend coordination: Add /api/csrf-token endpoint
- 12:00-13:00: Lunch break
- 13:00-14:30: Integrate CSRF with api/base.ts (auto-inject token)
- 14:30-15:30: Test CSRF token flow (fetch → inject → refresh on 403)
- 15:30-17:00: Handle edge cases (network errors, token expiry)

**Deliverables**:
- core/csrf.ts (70 lines) ✅
- CSRF integration in api/base.ts ✅
- Backend /api/csrf-token endpoint ✅

---

### Day 4: Thursday (8 hours)
**Phase 3: Vitest Unit Tests - Part 1 (Setup + Base Layer)**
- 09:00-10:00: Setup Vitest config, MSW, test utilities
- 10:00-12:00: Write unit tests for api/base.ts (28 tests)
  - apiRequest happy path (5 tests)
  - HTTP error handling (10 tests: 400, 401, 403, 404, 409, 413, 422, 429, 500, 503)
  - Network errors (3 tests)
  - CSRF token injection (5 tests)
  - Error toast integration (5 tests)
- 12:00-13:00: Lunch break
- 13:00-15:00: Write unit tests for core/csrf.ts (20 tests)
  - Token fetch (5 tests)
  - Token cache (5 tests)
  - Token expiry (5 tests)
  - 403 retry logic (5 tests)
- 15:00-17:00: Write unit tests for api/projects.ts (25 tests)
  - createProject (5 tests: success, validation, network error, duplicate, unauthorized)
  - getProjects (3 tests)
  - getProject (3 tests)
  - updateProject (5 tests)
  - deleteProject (5 tests)
  - getProjectStats (4 tests)

**Deliverables**:
- Vitest setup ✅
- MSW setup ✅
- api/base.test.ts (28 tests) ✅
- core/csrf.test.ts (20 tests) ✅
- api/projects.test.ts (25 tests) ✅

---

### Day 5: Friday (8 hours)
**Phase 3: Vitest Unit Tests - Part 2 (API Layer)**
- 09:00-11:00: Write unit tests for api/conversations.ts (30 tests)
  - getConversations (5 tests)
  - getConversation (5 tests)
  - createConversation (5 tests)
  - updateConversation (5 tests)
  - deleteConversation (5 tests)
  - getConversationMessages (5 tests)
- 11:00-13:00: Write unit tests for api/messages.ts (15 tests)
  - getMessage (5 tests)
  - createMessage (5 tests)
  - updateMessage (5 tests)
- 13:00-14:00: Lunch break
- 14:00-16:00: Write tests for utility functions (7 tests)
  - formatTimestamp (3 tests)
  - Error message mapping (4 tests)
- 16:00-17:00: Run coverage report, identify gaps

**Deliverables**:
- api/conversations.test.ts (30 tests) ✅
- api/messages.test.ts (15 tests) ✅
- utils/*.test.ts (7 tests) ✅
- Unit test coverage: 56%+ ✅

---

### Day 6: Saturday (6 hours)
**Phase 3: Integration Tests (Vitest + MSW)**
- 09:00-11:00: Write integration tests for project workflows (14 tests)
  - Create project → get project (2 tests)
  - Create project → update → delete (2 tests)
  - Create multiple projects → filter → paginate (3 tests)
  - Project + conversations workflow (4 tests)
  - Error recovery workflows (3 tests)
- 11:00-13:00: Write integration tests for conversation workflows (14 tests)
  - Create conversation → send message → get history (3 tests)
  - Multiple conversations in project (2 tests)
  - Conversation CRUD with messages (4 tests)
  - Streaming message updates (2 tests)
  - Error scenarios (3 tests)
- 13:00-15:00: Write integration tests for CSRF workflows (14 tests)
  - Token fetch → API call (3 tests)
  - Token expiry → refresh → retry (3 tests)
  - Multiple concurrent requests (2 tests)
  - CSRF failure scenarios (3 tests)
  - Token caching behavior (3 tests)

**Phase 4: Component Tests (Playwright MCP) - Part 1**
- 15:00-17:00: Write component tests for ChatInput (7 tests)
  - Submit on Enter (1 test)
  - Submit button click (1 test)
  - Disable while sending (1 test)
  - Clear after submit (1 test)
  - Multiline support (Shift+Enter) (1 test)
  - Character count (1 test)
  - Accessibility (keyboard nav) (1 test)

**Deliverables**:
- api/*.integration.test.ts (42 tests) ✅
- tests/component/ChatInput.spec.ts (7 tests) ✅
- Integration coverage: 14%+ ✅

---

### Day 7: Sunday (6 hours)
**Phase 4: Component Tests (Playwright MCP) - Part 2**
- 09:00-11:00: Write component tests for Sidebar (7 tests)
  - Project list rendering (1 test)
  - Create new project (1 test)
  - Switch project (1 test)
  - Delete project (1 test)
  - Search/filter (1 test)
  - Conversation list (1 test)
  - Accessibility (1 test)
- 11:00-13:00: Write component tests for MessageList (7 tests)
  - Render messages (1 test)
  - Scroll to bottom (1 test)
  - Streaming indicator (1 test)
  - Code highlighting (1 test)
  - Copy code button (1 test)
  - Markdown rendering (1 test)
  - Accessibility (1 test)

**Phase 4: E2E Tests (Playwright MCP) - Add 6 new tests**
- 13:00-15:00: Write E2E tests (6 tests)
  - Complete chat workflow with CSRF (1 test)
  - Multi-project workflow (1 test)
  - Document upload + chat (1 test)
  - Error recovery (network failure) (1 test)
  - Session persistence (refresh page) (1 test)
  - Mobile responsive (1 test)

**Phase 5: Visual Regression (Chrome DevTools MCP)**
- 15:00-16:00: Capture baseline screenshots (5 states)
  - Chat empty state
  - Chat with messages
  - Sidebar with projects
  - Error state
  - Loading state

**Phase 6: Performance Tests (Chrome DevTools MCP)**
- 16:00-17:00: Write performance tests (3 tests)
  - Initial load Core Web Vitals (1 test)
  - Chat interaction latency (1 test)
  - Bundle size validation (1 test)

**Deliverables**:
- tests/component/Sidebar.spec.ts (7 tests) ✅
- tests/component/MessageList.spec.ts (7 tests) ✅
- tests/e2e/*.spec.ts (20 total, 6 new) ✅
- tests/visual/*.spec.ts (5 tests) ✅
- tests/performance/*.spec.ts (3 tests) ✅
- **ALL 216 TESTS COMPLETE** ✅
- **70% COVERAGE ACHIEVED** ✅

---

## 🧪 Test Breakdown Summary

| Test Type | Count | Coverage Contribution |
|-----------|-------|----------------------|
| **Unit Tests** | 125 | 56% |
| - api/base.ts | 28 | 10% |
| - core/csrf.ts | 20 | 7% |
| - api/projects.ts | 25 | 9% |
| - api/conversations.ts | 30 | 11% |
| - api/messages.ts | 15 | 5% |
| - utils/*.ts | 7 | 3% |
| **Integration Tests** | 42 | 14% |
| - Project workflows | 14 | 5% |
| - Conversation workflows | 14 | 5% |
| - CSRF workflows | 14 | 4% |
| **Component Tests** | 21 | 7% |
| - ChatInput | 7 | 2% |
| - Sidebar | 7 | 2% |
| - MessageList | 7 | 3% |
| **E2E Tests** | 20 | 10% |
| - Existing | 12 | 6% |
| - New | 8 | 4% |
| **Visual Regression** | 5 | 1% |
| **Performance** | 3 | 1% |
| **TOTAL** | **216** | **70%** ✅

---

## 📁 File Structure

```
frontend/
├── src/
│   ├── lib/
│   │   ├── services/
│   │   │   ├── api/
│   │   │   │   ├── base.ts (80 lines)
│   │   │   │   ├── base.test.ts (28 tests)
│   │   │   │   ├── projects.ts (100 lines)
│   │   │   │   ├── projects.test.ts (25 tests)
│   │   │   │   ├── projects.integration.test.ts (14 tests)
│   │   │   │   ├── conversations.ts (120 lines)
│   │   │   │   ├── conversations.test.ts (30 tests)
│   │   │   │   ├── conversations.integration.test.ts (14 tests)
│   │   │   │   ├── messages.ts (60 lines)
│   │   │   │   ├── messages.test.ts (15 tests)
│   │   │   │   └── index.ts (barrel exports)
│   │   │   ├── core/
│   │   │   │   ├── csrf.ts (70 lines)
│   │   │   │   ├── csrf.test.ts (20 tests)
│   │   │   │   └── csrf.integration.test.ts (14 tests)
│   │   │   └── sse-client.ts (458 lines, unchanged)
│   │   └── utils/
│   │       ├── date.ts
│   │       ├── date.test.ts (3 tests)
│   │       ├── errors.ts
│   │       └── errors.test.ts (4 tests)
├── tests/
│   ├── component/
│   │   ├── ChatInput.spec.ts (7 tests)
│   │   ├── Sidebar.spec.ts (7 tests)
│   │   └── MessageList.spec.ts (7 tests)
│   ├── e2e/
│   │   ├── (12 existing tests)
│   │   └── (8 new tests)
│   ├── visual/
│   │   ├── chat-empty.spec.ts
│   │   ├── chat-populated.spec.ts
│   │   ├── sidebar.spec.ts
│   │   ├── error-state.spec.ts
│   │   └── loading-state.spec.ts
│   └── performance/
│       ├── core-web-vitals.spec.ts
│       ├── interaction-latency.spec.ts
│       └── bundle-size.spec.ts
└── vitest.config.ts (coverage: 70% minimum)
```

---

## ✅ Quality Gates

### Phase 3 → Phase 4 (After Integration Tests)
- ✅ All 167 unit + integration tests passing
- ✅ Coverage ≥ 70%
- ✅ TypeScript compilation succeeds
- ✅ No console.error in production code
- ✅ All API functions have ≥1 unit test
- ✅ All API modules have ≥1 integration test

### Phase 4 → Phase 5 (After Component/E2E Tests)
- ✅ All 208 tests passing (including component + E2E)
- ✅ Test pyramid compliant (60% unit, 20% integration, 20% component+E2E)
- ✅ All interactive components have data-testid attributes
- ✅ CSRF flow working end-to-end

### Phase 5 → Phase 6 (After Visual + Performance)
- ✅ All 216 tests passing
- ✅ Visual regression baselines captured
- ✅ No visual diffs > 1% threshold
- ✅ LCP ≤ 2.5s, FCP ≤ 1.8s, CLS ≤ 0.1
- ✅ Bundle size ≤ 60 KB (gzipped)

### Phase 6 → Completion
- ✅ Git checkpoint created
- ✅ QA-Agent final review approval
- ✅ 70% coverage achieved ✅
- ✅ All files ≤ 400 lines
- ✅ README updated with test instructions

---

## 🚀 Execution Commands

### Run Tests Incrementally

```bash
# Day 4: Unit tests
npm run test:unit src/lib/services/api/base.test.ts
npm run test:unit src/lib/services/core/csrf.test.ts
npm run test:unit src/lib/services/api/projects.test.ts

# Day 5: More unit tests
npm run test:unit src/lib/services/api/conversations.test.ts
npm run test:unit src/lib/services/api/messages.test.ts
npm run test:unit src/lib/utils/

# Day 6: Integration + Component
npm run test:integration
npm run test:component tests/component/ChatInput.spec.ts

# Day 7: E2E + Visual + Performance
npm run test:e2e
npm run test:visual
npm run test:performance

# Final: All tests + coverage
npm run test:coverage
```

### Coverage Check

```bash
# Should show ≥ 70%
npm run test:coverage

# Open HTML report
open coverage/index.html
```

---

## 📊 Success Criteria

### Must Achieve
- ✅ **70% test coverage** (CRITICAL GATE)
- ✅ **216 tests passing** (all types)
- ✅ **Test pyramid compliant** (60/20/10/10 distribution)
- ✅ **All files ≤ 400 lines**
- ✅ **Core Web Vitals: Good** (LCP ≤ 2.5s, FCP ≤ 1.8s, CLS ≤ 0.1)
- ✅ **Zero TypeScript errors**
- ✅ **Zero console.error/warn in production code**

### Should Achieve
- ⚠️ **Visual regression baselines** (5 states)
- ⚠️ **Performance baselines** (3 metrics)
- ⚠️ **Test execution time** < 3 minutes (unit), < 5 minutes (all)

### Nice to Have
- 📘 **Coverage by module** ≥ 80% for API, ≥ 70% for components
- 📘 **Integration test coverage** ≥ 15%
- 📘 **E2E test coverage** ≥ 10%

---

## 🔧 Risk Mitigation

### Risk: Coverage falls short of 70%
**Mitigation**:
- Monitor coverage after each day
- If Day 5 coverage < 60%, add 10 more unit tests on Day 6
- Prioritize high-value, untested code paths

### Risk: Test execution too slow
**Mitigation**:
- Run unit tests in parallel (Vitest default)
- Use MSW for fast integration tests (no real network)
- Run visual/performance tests only once per day

### Risk: CSRF integration breaks existing features
**Mitigation**:
- Test CSRF separately before integration
- Use feature flag to enable/disable CSRF
- Keep fallback to Origin/Referer validation

---

## 📝 Deliverables Checklist

- [ ] API client refactored (3 files @ ~100 lines each)
- [ ] CSRF implemented (core/csrf.ts)
- [ ] 125 unit tests written and passing
- [ ] 42 integration tests written and passing
- [ ] 21 component tests written and passing
- [ ] 20 E2E tests written and passing (12 existing + 8 new)
- [ ] 5 visual regression tests written
- [ ] 3 performance tests written
- [ ] 70% coverage achieved ✅
- [ ] Test pyramid compliant ✅
- [ ] All files ≤ 400 lines ✅
- [ ] Git checkpoint created
- [ ] QA review passed

---

**Plan Created**: 2025-11-24
**Created By**: PM-Architect-Agent
**Status**: READY FOR EXECUTION

**User Directive**: "Go with Option B" + "Each stage should have test coverage over 70% plz"
**Response**: Plan revised from 148 tests (52%) → 216 tests (70%) to meet user requirement.
