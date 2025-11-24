# Dual MCP Testing Examples

**Version**: 1.0.0
**Date**: 2024-11-23
**Purpose**: Practical examples of using Chrome DevTools MCP and Playwright MCP together

---

## Overview

This document provides real-world examples of how Frontend-Agent and QA-Agent should use Chrome DevTools MCP and Playwright MCP together for comprehensive testing of the GPT-OSS application.

---

## Example 1: Component Development & Testing (Frontend-Agent)

**Scenario**: Developing a new `FileUpload.svelte` component

### Step 1: Develop with Chrome DevTools MCP

```javascript
// Start dev server first: npm run dev

// 1. Navigate to component test page
mcp__chrome-devtools__navigate_page({
  url: "http://localhost:5173/test-components/file-upload",
  type: "url"
});

// 2. Inspect initial render
const snapshot = mcp__chrome-devtools__take_snapshot();
console.log("Component structure:", snapshot);

// 3. Test drag-and-drop interaction
mcp__chrome-devtools__drag({
  from_uid: "file-from-desktop",
  to_uid: "drop-zone"
});

// 4. Check for console errors
const consoleMessages = mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
});

// 5. Take screenshot of result
mcp__chrome-devtools__take_screenshot({
  filePath: ".claude-bus/test-results/screenshots/frontend-agent/file-upload-test.png"
});
```

### Step 2: Automate Test with Playwright MCP

```javascript
// Generate test code from interactions
playwright__launch_browser({ browser: "chromium" });
playwright__navigate("http://localhost:5173/test-components/file-upload");

// Start recording interactions
playwright__codegen();

// (Manually perform the file upload interactions in the opened browser)
// - Click the upload button
// - Select a file
// - Verify success message

// Stop recording and get generated test
const testCode = playwright__stop_codegen();

// Save generated test code
// Frontend-Agent would save this to frontend/tests/components/file-upload.spec.ts
```

**Result**: Chrome DevTools used for debugging during development, Playwright generates automated regression test.

---

## Example 2: Bug Investigation & Reproduction (QA-Agent)

**Scenario**: User reports "Messages disappear after streaming completes"

### Step 1: Investigate with Chrome DevTools MCP

```javascript
// 1. Navigate to chat page
mcp__chrome-devtools__new_page({
  url: "http://localhost:5173"
});

// 2. Create conversation and send message
mcp__chrome-devtools__click({ uid: "new-chat-button" });
mcp__chrome-devtools__fill({ uid: "message-input", value: "Test message" });
mcp__chrome-devtools__press_key({ key: "Enter" });

// 3. Monitor network for SSE stream
mcp__chrome-devtools__list_network_requests({
  resourceTypes: ["fetch", "eventsource"]
});

// 4. Watch console for errors during streaming
const console = mcp__chrome-devtools__list_console_messages({
  includePreservedMessages: true
});

// 5. Inspect DOM after streaming completes
mcp__chrome-devtools__evaluate_script({
  function: `() => {
    const messages = document.querySelectorAll('.message-bubble');
    return Array.from(messages).map(m => ({
      role: m.dataset.role,
      content: m.textContent,
      isEmpty: m.textContent.trim() === ''
    }));
  }`
});

// 6. Take screenshot of bug
mcp__chrome-devtools__take_screenshot({
  filePath: ".claude-bus/test-results/screenshots/qa-agent/bug-disappearing-messages.png"
});
```

### Step 2: Create Regression Test with Playwright MCP

```javascript
// Create automated test to prevent bug from returning
playwright__launch_browser({ browser: "chromium" });
playwright__navigate("http://localhost:5173");

// Write test that reproduces bug
playwright__click({ selector: "#new-chat-button" });
playwright__fill({ selector: "#message-input", value: "Test message" });
playwright__press({ selector: "#message-input", key: "Enter" });

// Wait for streaming to complete
playwright__wait_for_selector({
  selector: '.message-bubble[data-role="assistant"]',
  state: "visible"
});

// Assert message content exists and is not empty
playwright__assert_visible({ selector: '.message-bubble[data-role="assistant"]' });
playwright__assert_text({
  selector: '.message-bubble[data-role="assistant"]',
  text: /.+/,  // Regex: matches any non-empty text
  useRegex: true
});

// Take screenshot for visual regression
playwright__screenshot({
  path: ".claude-bus/test-results/playwright/screenshots/qa-agent/message-after-streaming.png"
});
```

**Result**: Chrome DevTools identified the bug, Playwright created automated test to prevent regression.

---

## Example 3: Cross-Browser Compatibility (QA-Agent)

**Scenario**: Verify chat interface works on Firefox and Safari

### Step 1: Baseline with Chrome DevTools MCP

```javascript
// 1. Test on Chromium (development browser)
mcp__chrome-devtools__new_page({ url: "http://localhost:5173" });

// 2. Capture performance metrics
mcp__chrome-devtools__performance_start_trace({ reload: true, autoStop: true });
// (Metrics recorded: LCP, CLS, TTFB)

// 3. Take baseline screenshot
mcp__chrome-devtools__take_screenshot({
  filePath: ".claude-bus/test-results/screenshots/qa-agent/chromium-baseline.png"
});
```

### Step 2: Cross-Browser Testing with Playwright MCP

```javascript
// Test on Firefox
playwright__launch_browser({ browser: "firefox" });
playwright__navigate("http://localhost:5173");

playwright__click({ selector: "#new-chat-button" });
playwright__fill({ selector: "#message-input", value: "Cross-browser test" });
playwright__press({ selector: "#message-input", key: "Enter" });

// Wait for response
playwright__wait_for_selector({ selector: '.message-bubble[data-role="assistant"]' });

// Take screenshot
playwright__screenshot({
  path: ".claude-bus/test-results/playwright/screenshots/qa-agent/firefox-chat.png"
});

playwright__close_browser();

// Test on WebKit (Safari)
playwright__launch_browser({ browser: "webkit" });
playwright__navigate("http://localhost:5173");

// Repeat same test
playwright__click({ selector: "#new-chat-button" });
playwright__fill({ selector: "#message-input", value: "Cross-browser test" });
playwright__press({ selector: "#message-input", key: "Enter" });

playwright__wait_for_selector({ selector: '.message-bubble[data-role="assistant"]' });

playwright__screenshot({
  path: ".claude-bus/test-results/playwright/screenshots/qa-agent/webkit-chat.png"
});

// Compare screenshots for visual consistency
playwright__screenshot_compare({
  baseline: ".claude-bus/test-results/screenshots/qa-agent/chromium-baseline.png",
  current: ".claude-bus/test-results/playwright/screenshots/qa-agent/firefox-chat.png",
  threshold: 5  // Allow 5% difference
});
```

**Result**: Chrome DevTools provides deep Chromium insights, Playwright validates cross-browser compatibility.

---

## Example 4: Performance Debugging + E2E Validation (QA-Agent)

**Scenario**: Chat page is slow, need to find bottleneck and ensure fix doesn't break functionality

### Step 1: Profile Performance with Chrome DevTools MCP

```javascript
// 1. Start performance profiling
mcp__chrome-devtools__new_page({ url: "http://localhost:5173" });

mcp__chrome-devtools__performance_start_trace({
  reload: true,
  autoStop: false
});

// 2. Perform user workflow
mcp__chrome-devtools__click({ uid: "new-chat-button" });
mcp__chrome-devtools__fill({ uid: "message-input", value: "Performance test" });
mcp__chrome-devtools__press_key({ key: "Enter" });

// 3. Wait for streaming to complete
mcp__chrome-devtools__wait_for({ text: "assistant message completed" });

// 4. Stop profiling
const perfResults = mcp__chrome-devtools__performance_stop_trace();

// 5. Analyze insights
mcp__chrome-devtools__performance_analyze_insight({
  insightSetId: "NAVIGATION_0",
  insightName: "LCPBreakdown"
});

// Result: Identifies LCP is slow due to large bundle size
```

### Step 2: Validate Fix with Playwright MCP

```javascript
// After frontend optimizations (code splitting, lazy loading)

// 1. Run comprehensive E2E test to ensure nothing broke
playwright__launch_browser({ browser: "chromium" });
playwright__navigate("http://localhost:5173");

// 2. Test full user workflow
playwright__click({ selector: "#new-chat-button" });
playwright__fill({ selector: "#message-input", value: "Test after optimization" });
playwright__press({ selector: "#message-input", key: "Enter" });

// 3. Verify all functionality still works
playwright__assert_visible({ selector: '.message-bubble[data-role="user"]' });
playwright__assert_visible({ selector: '.message-bubble[data-role="assistant"]' });

// 4. Send follow-up message
playwright__fill({ selector: "#message-input", value: "Follow-up test" });
playwright__press({ selector: "#message-input", key: "Enter" });

playwright__assert_visible({
  selector: '.message-bubble[data-role="assistant"]:nth-child(4)'
});

// 5. Switch conversations
playwright__click({ selector: '.conversation-item:nth-child(2)' });
playwright__assert_url({ url: /project\/\d+\/conversation\/\d+/ });

// All tests pass = optimization didn't break functionality
```

### Step 3: Re-Profile with Chrome DevTools MCP

```javascript
// Verify performance improvement
mcp__chrome-devtools__performance_start_trace({ reload: true, autoStop: true });

// Compare new metrics against baseline
// Before: LCP 3500ms, After: LCP 800ms ✅
```

**Result**: Chrome DevTools identified bottleneck and verified fix, Playwright ensured no regressions.

---

## Example 5: API + UI Integration Testing (QA-Agent)

**Scenario**: Verify backend API state matches frontend UI state

### Step 1: Setup Test Data via Playwright API

```javascript
// 1. Launch browser
playwright__launch_browser({ browser: "chromium" });

// 2. Use Playwright API testing to create test data
const project = await playwright__api_post({
  url: "http://localhost:8000/api/projects/create",
  data: {
    name: "API Test Project",
    description: "Created via Playwright API"
  }
});

const conversation = await playwright__api_post({
  url: "http://localhost:8000/api/conversations/create",
  data: {
    project_id: project.id,
    title: "API Test Conversation"
  }
});

// 3. Navigate to UI
playwright__navigate(`http://localhost:5173/project/${project.id}`);

// 4. Verify UI shows correct data
playwright__assert_text({
  selector: ".project-name",
  text: "API Test Project"
});

playwright__assert_text({
  selector: ".conversation-item:first-child .title",
  text: "API Test Conversation"
});
```

### Step 2: Interact via UI, Verify via API

```javascript
// 1. Send message via UI
playwright__click({ selector: "#new-chat-button" });
playwright__fill({ selector: "#message-input", value: "API integration test" });
playwright__press({ selector: "#message-input", key: "Enter" });

// 2. Wait for response
playwright__wait_for_selector({
  selector: '.message-bubble[data-role="assistant"]'
});

// 3. Verify backend state via API
const messages = await playwright__api_get({
  url: `http://localhost:8000/api/messages/${conversation.id}`
});

// 4. Assert backend matches UI
if (messages.length !== 2) {
  throw new Error(`Expected 2 messages, got ${messages.length}`);
}

if (messages[0].role !== "user" || messages[0].content !== "API integration test") {
  throw new Error("User message not saved correctly");
}

if (messages[1].role !== "assistant" || messages[1].content === "") {
  throw new Error("Assistant response not saved correctly");
}
```

### Step 3: Inspect Network with Chrome DevTools MCP

```javascript
// If test fails, use Chrome DevTools to debug

mcp__chrome-devtools__list_network_requests({
  resourceTypes: ["fetch", "xhr"]
});

// Check specific API request
const chatRequest = mcp__chrome-devtools__get_network_request({ reqid: 42 });

// Inspect request/response details
console.log("Request payload:", chatRequest.requestPayload);
console.log("Response status:", chatRequest.statusCode);
console.log("Response data:", chatRequest.responseBody);
```

**Result**: Playwright handles API + UI testing, Chrome DevTools debugs issues.

---

## Best Practices

### 1. Choose the Right Tool for the Job

✅ **Chrome DevTools MCP**:
- Finding bugs during development
- Deep performance analysis
- Real-time console monitoring
- Network debugging (especially SSE/WebSocket)

✅ **Playwright MCP**:
- Writing regression tests
- Cross-browser validation
- Automated test generation
- API + UI integration testing

### 2. Use Both for Complete Coverage

```
Development Cycle:
1. Develop feature (Chrome DevTools for debugging)
2. Create tests (Playwright for automation)
3. Find bugs (Chrome DevTools for investigation)
4. Prevent regressions (Playwright for test suite)
5. Profile performance (Chrome DevTools for metrics)
6. Validate cross-browser (Playwright for Firefox/Safari)
```

### 3. Artifact Organization

```
.claude-bus/test-results/
├── screenshots/
│   ├── frontend-agent/        # Chrome DevTools screenshots
│   └── qa-agent/              # Chrome DevTools screenshots
├── traces/
│   ├── frontend-agent/        # Chrome DevTools traces
│   └── qa-agent/              # Chrome DevTools traces
└── playwright/
    ├── screenshots/
    │   ├── frontend-agent/    # Playwright screenshots (Chromium only)
    │   └── qa-agent/          # Playwright screenshots (all browsers)
    ├── videos/
    │   └── qa-agent/          # Test failure videos
    ├── traces/
    │   └── qa-agent/          # Playwright traces
    └── generated-tests/       # Auto-generated test code
```

### 4. Lock Management

Both MCPs can run simultaneously (different ports), but still acquire browser lock for coordination:

```bash
# Before using EITHER MCP
echo '{"agent":"QA-Agent","mcp":"playwright","timestamp":"..."}' > .claude-bus/locks/browser.lock

# Perform testing
# ...

# Release lock after testing
rm .claude-bus/locks/browser.lock
```

---

## Troubleshooting

### Issue: "Which MCP should I use?"

**Answer**: Refer to the MCP Selection Guide in `browser-testing-protocol.md`

Quick decision tree:
- Need to debug? → Chrome DevTools
- Need to automate? → Playwright
- Need performance metrics? → Chrome DevTools
- Need cross-browser? → Playwright
- Not sure? → Try Chrome DevTools first (faster for quick tests)

### Issue: "Can I use both at the same time?"

**Answer**: Yes! They run on different ports and manage separate browser instances.

**Example**:
```javascript
// Chrome DevTools debugging on port 9222
mcp__chrome-devtools__new_page({ url: "http://localhost:5173" });

// Playwright testing on port 9223 (simultaneous)
playwright__launch_browser({ browser: "firefox" });
playwright__navigate("http://localhost:5173");

// Both work independently
```

### Issue: "Test generated by Playwright fails in Chrome DevTools"

**Answer**: This is expected! Different tools, different approaches.

Playwright tests use accessibility tree (deterministic).
Chrome DevTools uses DevTools Protocol (browser-specific).

**Solution**: Keep tests separate, use each for their strengths.

---

## References

- **Configuration**: `.claude-bus/config/mcp-config.json`
- **Protocol**: `.claude-bus/protocols/browser-testing-protocol.md`
- **Installation**: `.claude-bus/protocols/PLAYWRIGHT-MCP-INSTALLATION.md`
- **Frontend Agent**: `.claude-bus/agents/Frontend-Agent.md`
- **QA Agent**: `.claude-bus/agents/QA-Agent.md`

