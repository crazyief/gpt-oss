# Browser Testing Coordination Protocol

## Overview

This protocol defines how Frontend-Agent and QA-Agent coordinate browser testing activities using Chrome DevTools MCP and Playwright MCP to prevent conflicts, ensure test isolation, and maintain consistent quality standards.

**Version**: 2.0.0
**Last Updated**: 2024-11-23
**Applies to**: Frontend-Agent, QA-Agent
**MCP Tools**: Chrome DevTools MCP, Playwright MCP

---

## MCP Tool Selection Guide

### Chrome DevTools MCP vs Playwright MCP

Choose the right MCP based on your testing needs:

| Testing Scenario | Recommended MCP | Rationale |
|------------------|-----------------|-----------|
| **Performance Profiling** | Chrome DevTools | Full trace capture, Core Web Vitals |
| **Network Debugging** | Chrome DevTools | Request inspection, timing analysis |
| **Console Error Monitoring** | Chrome DevTools | Real-time console output |
| **Cross-Browser Testing** | Playwright | Firefox, Safari support |
| **E2E Test Writing** | Playwright | Test generation, better API |
| **Visual Regression** | Playwright | Built-in screenshot diffing |
| **API + UI Testing** | Playwright | Native API testing support |
| **Accessibility Debugging** | Chrome DevTools | Detailed a11y tree inspection |
| **Component Testing** | Either | Both work well |
| **SSE/WebSocket Debugging** | Chrome DevTools | Network tab inspection |

### Tool Usage Examples

#### Chrome DevTools MCP
```python
# Performance profiling example
mcp__chrome-devtools__performance_start_trace(reload=True, autoStop=True)
# ... user interactions ...
results = mcp__chrome-devtools__performance_stop_trace()
# Analyze Core Web Vitals

# Network debugging
requests = mcp__chrome-devtools__list_network_requests()
sse_request = mcp__chrome-devtools__get_network_request(reqid=123)
```

#### Playwright MCP
```python
# Cross-browser testing
playwright__launch_browser(browser="firefox")
playwright__navigate("http://localhost:5173")
playwright__screenshot(fullPage=True)

# Test generation
playwright__start_codegen()
# Perform manual interactions
test_code = playwright__stop_codegen()
```

### Coordination Rules

1. **Both MCPs can run simultaneously** - Different ports (9222 vs 9223)
2. **Browser isolation** - Each MCP manages its own browser instance
3. **No shared state** - Tests are independent
4. **Priority**: QA-Agent gets priority for both MCPs during Phase 4

---

## 1. Resource Allocation

### Browser Instance Limits
- **Maximum concurrent browser pages**: 3 (across all agents)
- **Maximum memory per browser**: 2GB
- **Page timeout**: 30 seconds
- **Total test timeout**: 5 minutes per test suite

### Priority System
1. **QA-Agent**: HIGH priority during Phase 4 (Integration Testing)
2. **Frontend-Agent**: NORMAL priority during Phase 2 (Development)
3. **Conflict resolution**: QA-Agent preempts Frontend-Agent if needed

### Lock Mechanism
Agents MUST acquire a lock before starting browser operations:

```bash
# Check if browser is available
if [ -f .claude-bus/locks/browser.lock ]; then
  # Browser is locked - wait or skip
  echo "Browser locked by another agent"
  exit 1
fi

# Acquire lock
echo "{\"agent\": \"Frontend-Agent\", \"timestamp\": \"$(date -Iseconds)\", \"pid\": $$}" > .claude-bus/locks/browser.lock

# Perform browser operations
# ...

# Release lock
rm .claude-bus/locks/browser.lock
```

**Lock timeout**: If lock file is older than 5 minutes, it can be forcibly removed (assume crashed process).

---

## 2. Test Isolation Rules

### Pre-Test Cleanup
Before EVERY test, agents MUST:

1. **Clear browser state**:
   ```javascript
   await page.evaluate(() => {
     localStorage.clear();
     sessionStorage.clear();
     // Clear all cookies
     document.cookie.split(";").forEach(c => {
       document.cookie = c.trim().split("=")[0] + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT';
     });
   });
   ```

2. **Navigate to clean URL**: Always start from a known state
   ```javascript
   await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
   ```

3. **Verify service health**: Check that backend services are responding
   ```bash
   curl -f http://localhost:8000/health || exit 1
   ```

### Post-Test Cleanup
After EVERY test, agents MUST:

1. **Close all pages** except the default tab
2. **Save artifacts** (screenshots, traces, logs)
3. **Release lock file**
4. **Log test completion**

---

## 3. Artifact Management

### Screenshot Naming Convention
Format: `{agent}-{timestamp}-{test-name}.png`

Examples:
- `frontend-agent-20241123-143022-chat-component.png`
- `qa-agent-20241123-143100-e2e-login-flow.png`

### Directory Structure
```
.claude-bus/test-results/
├── screenshots/
│   ├── frontend-agent/
│   │   ├── 2024-11-23-component-button.png
│   │   ├── 2024-11-23-component-modal.png
│   │   └── 2024-11-23-sidebar-rendering.png
│   └── qa-agent/
│       ├── 2024-11-23-e2e-login-flow.png
│       ├── 2024-11-23-e2e-chat-workflow.png
│       └── 2024-11-23-accessibility-scan.png
├── traces/
│   ├── frontend-agent/
│   └── qa-agent/
│       ├── 2024-11-23-performance-trace-homepage.json
│       └── 2024-11-23-performance-trace-chat.json
└── console-logs/
    ├── frontend-agent/
    └── qa-agent/
```

### Artifact Retention
- **Screenshots**: Keep for 30 days
- **Traces**: Keep for 7 days
- **Console logs**: Keep for 14 days
- **Failed test artifacts**: Keep indefinitely until issue resolved

---

## 4. Phase-Specific Coordination

### Phase 2: Development (Frontend-Agent Active)
- **Frontend-Agent**: Component testing, visual verification
- **QA-Agent**: INACTIVE (no browser testing)
- **Concurrency**: Not a concern, only one agent active

**Frontend-Agent workflow**:
1. Start dev server: `npm run dev`
2. Acquire browser lock
3. Test individual components
4. Take screenshots for visual verification
5. Check console for errors
6. Release lock

### Phase 4: Integration Testing (QA-Agent Active)
- **QA-Agent**: Full E2E testing, performance profiling
- **Frontend-Agent**: INACTIVE (development complete)
- **Concurrency**: Not a concern, only one agent active

**QA-Agent workflow**:
1. Verify all services running
2. Acquire browser lock (high priority)
3. Execute comprehensive test suites
4. Record performance baselines
5. Generate test reports
6. Release lock

### Emergency Override
If PM-Architect detects critical issue requiring immediate Frontend-Agent testing during Phase 4:
1. PM-Architect notifies QA-Agent to pause
2. QA-Agent completes current test (max 5 min)
3. QA-Agent releases lock
4. Frontend-Agent acquires lock, performs fix verification
5. Frontend-Agent releases lock
6. QA-Agent resumes testing

---

## 5. Error Handling

### Browser Crash Recovery
If browser crashes during test:
1. **Log error** to `.claude-bus/monitoring/browser-failures.jsonl`
2. **Force release lock** (delete lock file)
3. **Save crash artifacts** (screenshot if possible, console logs)
4. **Retry test** (max 2 retries with 1s delay)
5. **Escalate to PM-Architect** if retries fail

### Timeout Handling
If test exceeds 30s page timeout:
1. **Take emergency screenshot** of current state
2. **Capture console errors**
3. **Release lock**
4. **Mark test as TIMEOUT** in results
5. **Continue to next test** (don't block entire suite)

### Lock Conflict Resolution
If lock file exists but process is dead (stale lock):
```bash
# Check lock age
LOCK_AGE=$(( $(date +%s) - $(stat -c %Y .claude-bus/locks/browser.lock) ))
if [ $LOCK_AGE -gt 300 ]; then
  echo "Stale lock detected (older than 5 minutes), force releasing"
  rm .claude-bus/locks/browser.lock
fi
```

---

## 6. Logging Requirements

All browser operations MUST be logged to `.claude-bus/monitoring/browser-usage.jsonl`:

```json
{
  "timestamp": "2024-11-23T14:30:22Z",
  "agent": "Frontend-Agent",
  "action": "acquire_lock",
  "test_name": "chat-component-rendering",
  "duration_ms": 0
}
```

```json
{
  "timestamp": "2024-11-23T14:30:55Z",
  "agent": "Frontend-Agent",
  "action": "release_lock",
  "test_name": "chat-component-rendering",
  "duration_ms": 33000,
  "status": "success",
  "artifacts": [
    "frontend-agent-20241123-143022-chat-component.png"
  ]
}
```

### Log Entry Types
- `acquire_lock` - Lock acquired
- `release_lock` - Lock released
- `test_start` - Test execution started
- `test_complete` - Test finished successfully
- `test_failed` - Test failed
- `test_timeout` - Test exceeded timeout
- `browser_crash` - Browser crashed

---

## 7. Performance Monitoring

### Baseline Tracking
QA-Agent MUST establish performance baselines during first Phase 4 run:

Store in `.claude-bus/metrics/performance-baselines.json`:
```json
{
  "homepage": {
    "lcp_ms": 1200,
    "fcp_ms": 800,
    "cls": 0.05,
    "ttfb_ms": 250,
    "timestamp": "2024-11-23T14:00:00Z"
  },
  "chat_page": {
    "lcp_ms": 1500,
    "fcp_ms": 900,
    "cls": 0.03,
    "ttfb_ms": 300,
    "timestamp": "2024-11-23T14:00:00Z"
  }
}
```

### Regression Detection
On subsequent test runs, compare against baselines:
- **LCP degradation > 10%**: WARNING
- **LCP degradation > 25%**: FAIL test
- **CLS increase > 0.05**: FAIL test
- **Console errors > 0**: FAIL test

---

## 8. Best Practices

### Frontend-Agent Testing
✅ **DO**:
- Test individual components in isolation
- Take screenshots for visual verification
- Check console for errors/warnings
- Use component-specific test URLs
- Keep tests under 10 seconds each

❌ **DON'T**:
- Run full E2E workflows (defer to QA-Agent)
- Perform performance profiling (defer to QA-Agent)
- Test multi-page flows (defer to QA-Agent)
- Leave browser pages open
- Skip lock acquisition

### QA-Agent Testing
✅ **DO**:
- Test complete user workflows
- Record performance traces
- Validate accessibility
- Test error scenarios
- Compare against baselines
- Generate comprehensive reports

❌ **DON'T**:
- Skip pre-test cleanup
- Ignore performance regressions
- Test during Phase 2 (wait for Phase 4)
- Use Frontend-Agent's screenshots directory

---

## 9. Troubleshooting Guide

### Problem: "Browser is locked" error
**Cause**: Another agent is using browser
**Solution**:
1. Check lock file age: `ls -lh .claude-bus/locks/browser.lock`
2. If older than 5 minutes, force remove: `rm .claude-bus/locks/browser.lock`
3. If recent, wait for other agent to finish

### Problem: Tests are flaky/inconsistent
**Cause**: Browser state pollution
**Solution**:
1. Verify pre-test cleanup is executed
2. Check for shared localStorage/cookies
3. Use unique test data IDs
4. Clear cache before tests

### Problem: Browser crashes frequently
**Cause**: Memory exhaustion
**Solution**:
1. Check browser memory usage
2. Close unused pages
3. Reduce concurrent test parallelism
4. Restart browser between test suites

### Problem: Screenshots are missing
**Cause**: Directory doesn't exist or permissions issue
**Solution**:
1. Verify directory exists: `ls -la .claude-bus/test-results/screenshots/`
2. Create if missing: `mkdir -p .claude-bus/test-results/screenshots/{agent-name}/`
3. Check write permissions

---

## 10. Compliance Checklist

Before merging code that uses browser testing:

- [ ] Agent definition file updated with MCP tool requirements
- [ ] Tests acquire and release lock properly
- [ ] Pre-test cleanup implemented
- [ ] Post-test cleanup implemented
- [ ] Screenshots saved to correct directory
- [ ] Logging to browser-usage.jsonl implemented
- [ ] Error handling covers crashes and timeouts
- [ ] Performance baselines established (QA-Agent only)
- [ ] Test documentation updated

---

## References

- MCP Configuration: `.claude-bus/config/mcp-config.json`
- Frontend-Agent Definition: `.claude-bus/agents/Frontend-Agent.md`
- QA-Agent Definition: `.claude-bus/agents/QA-Agent.md`
- Performance Baselines: `.claude-bus/metrics/performance-baselines.json`
