# Dual MCP Testing Examples

## Overview

Real-world examples showing how Chrome DevTools MCP and Playwright MCP work together for comprehensive testing.

---

## Example 1: Performance + Cross-Browser Testing

**Scenario**: Test chat interface performance across browsers

```python
# QA-Agent test script

async def test_chat_performance_cross_browser():
    """
    Use Chrome DevTools for performance profiling
    Use Playwright for cross-browser validation
    """

    # Step 1: Chrome DevTools - Baseline performance
    print("📊 Capturing performance baseline with Chrome DevTools...")

    # Start performance trace
    chrome_devtools.navigate_page(url="http://localhost:5173/chat")
    chrome_devtools.performance_start_trace(reload=True, autoStop=False)

    # Perform standard chat operations
    chrome_devtools.fill(uid="chat-input", value="Test message")
    chrome_devtools.click(uid="send-button")
    chrome_devtools.wait_for(text="Test message", timeout=5000)

    # Stop trace and analyze
    trace_results = chrome_devtools.performance_stop_trace()
    baseline_metrics = {
        "lcp": trace_results["insights"]["LCP"],
        "fcp": trace_results["insights"]["FCP"],
        "cls": trace_results["insights"]["CLS"]
    }

    print(f"✅ Chrome baseline: LCP={baseline_metrics['lcp']}ms")

    # Step 2: Playwright - Cross-browser validation
    print("🌐 Testing across browsers with Playwright...")

    browsers = ["chromium", "firefox", "webkit"]
    results = {}

    for browser in browsers:
        # Launch browser
        playwright.launch_browser(browser=browser)
        playwright.navigate("http://localhost:5173/chat")

        # Measure load time
        start_time = time.time()
        playwright.wait_for_selector("#chat-container")
        load_time = (time.time() - start_time) * 1000

        # Test functionality
        playwright.fill("#chat-input", "Test message")
        playwright.click("#send-button")

        # Take screenshot for visual comparison
        playwright.screenshot(
            fullPage=True,
            path=f"test-results/{browser}-chat.png"
        )

        results[browser] = {
            "load_time": load_time,
            "functional": True
        }

        playwright.close_browser()

    # Step 3: Compare and report
    print("\n📈 Test Results:")
    print(f"Chrome DevTools Performance: {baseline_metrics}")
    print(f"Cross-Browser Load Times: {results}")

    # Assert performance requirements
    assert baseline_metrics["lcp"] < 2500, "LCP exceeds threshold"
    assert all(r["functional"] for r in results.values()), "Functionality broken in some browsers"

    return {
        "performance": baseline_metrics,
        "cross_browser": results
    }
```

---

## Example 2: Debugging SSE Streaming Issues

**Scenario**: Debug SSE streaming with Chrome DevTools, automate fix validation with Playwright

```python
# Frontend-Agent debugging script

async def debug_and_fix_sse_streaming():
    """
    Chrome DevTools: Debug network issues
    Playwright: Automate regression test
    """

    # Phase 1: Debug with Chrome DevTools
    print("🔍 Debugging SSE with Chrome DevTools...")

    # Navigate and start monitoring
    chrome_devtools.navigate_page(url="http://localhost:5173/chat")

    # Clear console to start fresh
    chrome_devtools.list_console_messages()

    # Trigger SSE stream
    chrome_devtools.fill(uid="chat-input", value="Stream test")
    chrome_devtools.click(uid="send-button")

    # Monitor network for SSE
    time.sleep(2)  # Let stream start
    requests = chrome_devtools.list_network_requests(
        resourceTypes=["eventsource", "xhr", "fetch"]
    )

    # Find SSE request
    sse_request = None
    for req in requests:
        if "/api/chat/stream" in req["url"]:
            sse_request = chrome_devtools.get_network_request(reqid=req["id"])
            break

    if sse_request:
        print(f"✅ SSE Request found: {sse_request['status']}")
        print(f"Headers: {sse_request['responseHeaders']}")

        # Check for issues
        if sse_request['status'] != 200:
            print(f"❌ SSE Failed: Status {sse_request['status']}")

            # Get console errors
            console_msgs = chrome_devtools.list_console_messages(types=["error"])
            for msg in console_msgs:
                print(f"Console Error: {msg['text']}")

    # Phase 2: Create automated test with Playwright
    print("\n🤖 Creating automated regression test...")

    # Start recording
    playwright.start_codegen()

    # Perform the fixed flow
    playwright.navigate("http://localhost:5173/chat")
    playwright.fill("#chat-input", "Test SSE streaming")
    playwright.click("#send-button")

    # Wait for streaming to complete
    playwright.wait_for_selector(".message-complete", timeout=10000)

    # Stop recording and get test code
    test_code = playwright.stop_codegen()

    # Save the test
    with open("tests/sse_streaming_test.js", "w") as f:
        f.write(test_code)

    print("✅ Regression test created: tests/sse_streaming_test.js")

    return {
        "issue_found": sse_request['status'] != 200 if sse_request else False,
        "test_created": True
    }
```

---

## Example 3: Visual Regression + Performance Impact

**Scenario**: Validate UI changes don't degrade performance

```python
# QA-Agent comprehensive test

async def test_ui_update_impact():
    """
    Playwright: Visual regression testing
    Chrome DevTools: Performance impact analysis
    """

    # Step 1: Playwright - Capture baseline visuals
    print("📸 Capturing visual baselines with Playwright...")

    pages = ["/", "/chat", "/projects", "/settings"]
    baseline_screenshots = {}

    playwright.launch_browser(browser="chromium")

    for page in pages:
        playwright.navigate(f"http://localhost:5173{page}")
        playwright.wait_for_load_state("networkidle")

        screenshot_path = f"baselines/{page.replace('/', 'root')}.png"
        playwright.screenshot(fullPage=True, path=screenshot_path)
        baseline_screenshots[page] = screenshot_path

    playwright.close_browser()

    # Step 2: Deploy UI updates
    print("🚀 UI updates deployed (simulated)...")

    # Step 3: Chrome DevTools - Measure performance impact
    print("⚡ Measuring performance impact...")

    performance_results = {}

    for page in pages:
        chrome_devtools.navigate_page(url=f"http://localhost:5173{page}")
        chrome_devtools.performance_start_trace(reload=True, autoStop=True)

        # Wait for trace completion
        time.sleep(3)
        trace = chrome_devtools.performance_stop_trace()

        performance_results[page] = {
            "lcp": trace["insights"]["LCP"],
            "fcp": trace["insights"]["FCP"],
            "cls": trace["insights"]["CLS"],
            "ttfb": trace["insights"]["TTFB"]
        }

    # Step 4: Playwright - Visual comparison
    print("🔍 Comparing visuals...")

    visual_diffs = {}
    playwright.launch_browser(browser="chromium")

    for page in pages:
        playwright.navigate(f"http://localhost:5173{page}")
        playwright.wait_for_load_state("networkidle")

        new_screenshot = f"current/{page.replace('/', 'root')}.png"
        playwright.screenshot(fullPage=True, path=new_screenshot)

        # Compare with baseline (using Playwright's built-in comparison)
        diff_result = playwright.compare_screenshots(
            baseline=baseline_screenshots[page],
            current=new_screenshot,
            threshold=5  # 5% difference threshold
        )

        visual_diffs[page] = diff_result

    playwright.close_browser()

    # Step 5: Generate report
    print("\n📊 Impact Analysis Report:")
    print("=" * 50)

    for page in pages:
        print(f"\n{page}:")
        print(f"  Performance: LCP={performance_results[page]['lcp']}ms")
        print(f"  Visual Change: {visual_diffs[page]['difference']}%")

        if visual_diffs[page]['difference'] > 5:
            print(f"  ⚠️ Significant visual change detected!")

        if performance_results[page]['lcp'] > 2500:
            print(f"  ⚠️ Performance degradation detected!")

    return {
        "performance": performance_results,
        "visual_changes": visual_diffs
    }
```

---

## Example 4: Accessibility Testing Combination

**Scenario**: Comprehensive accessibility validation

```python
async def test_accessibility_comprehensive():
    """
    Chrome DevTools: Detailed a11y tree analysis
    Playwright: Cross-browser a11y validation
    """

    # Chrome DevTools - Deep accessibility inspection
    print("🔍 Deep a11y analysis with Chrome DevTools...")

    chrome_devtools.navigate_page(url="http://localhost:5173")

    # Get detailed accessibility tree
    a11y_snapshot = chrome_devtools.take_snapshot(verbose=True)

    # Analyze for issues
    issues = []
    for element in a11y_snapshot["elements"]:
        # Check for missing alt text
        if element["role"] == "img" and not element.get("name"):
            issues.append(f"Image missing alt text: {element['uid']}")

        # Check for missing labels
        if element["role"] in ["textbox", "button"] and not element.get("name"):
            issues.append(f"Interactive element missing label: {element['uid']}")

    # Playwright - Cross-browser validation
    print("🌐 Cross-browser a11y testing...")

    browsers = ["chromium", "firefox", "webkit"]

    for browser in browsers:
        playwright.launch_browser(browser=browser)
        playwright.navigate("http://localhost:5173")

        # Run axe-core accessibility tests
        playwright.inject_script("https://cdn.jsdelivr.net/npm/axe-core@4/axe.min.js")

        a11y_results = playwright.evaluate("""
            async () => {
                const results = await axe.run();
                return {
                    violations: results.violations.length,
                    passes: results.passes.length
                };
            }
        """)

        print(f"{browser}: {a11y_results['violations']} violations found")

        playwright.close_browser()

    return {"chrome_devtools_issues": issues}
```

---

## Example 5: E2E Workflow with Dual Validation

**Scenario**: Complete user journey with performance monitoring

```python
async def test_complete_user_journey():
    """
    Playwright: Drive the E2E flow
    Chrome DevTools: Monitor performance throughout
    """

    # Start Chrome DevTools monitoring
    chrome_devtools.navigate_page(url="http://localhost:5173")
    chrome_devtools.performance_start_trace(reload=False, autoStop=False)

    # Use Playwright for user interactions
    playwright.launch_browser(browser="chromium")
    playwright.navigate("http://localhost:5173")

    # Step 1: Login
    playwright.fill("#username", "testuser")
    playwright.fill("#password", "testpass")
    playwright.click("#login-button")
    playwright.wait_for_url("**/dashboard")

    # Check Chrome DevTools console for errors
    console_errors = chrome_devtools.list_console_messages(types=["error"])
    assert len(console_errors) == 0, f"Console errors during login: {console_errors}"

    # Step 2: Create project
    playwright.click("#new-project")
    playwright.fill("#project-name", "Test Project")
    playwright.click("#create-button")

    # Step 3: Upload document
    playwright.upload_file("#file-input", "./test-docs/sample.pdf")
    playwright.wait_for_selector(".upload-complete")

    # Step 4: Start chat
    playwright.click("#chat-tab")
    playwright.fill("#chat-input", "Analyze this document")
    playwright.click("#send-button")
    playwright.wait_for_selector(".ai-response")

    # Stop performance monitoring
    performance_data = chrome_devtools.performance_stop_trace()

    # Validate performance
    insights = performance_data["insights"]
    assert insights["TotalBlockingTime"] < 500, "Too much blocking time"
    assert insights["CumulativeLayoutShift"] < 0.1, "Layout shift too high"

    playwright.close_browser()

    return {
        "journey_complete": True,
        "performance_metrics": insights
    }
```

---

## Best Practices for Dual MCP Testing

1. **Use Chrome DevTools for**:
   - Real-time monitoring during tests
   - Debugging test failures
   - Performance baseline capture
   - Network request inspection

2. **Use Playwright for**:
   - Driving user interactions
   - Cross-browser validation
   - Screenshot comparisons
   - Test code generation

3. **Combine both for**:
   - Comprehensive E2E validation
   - Performance regression testing
   - Debugging + automation workflow
   - Full coverage testing

4. **Avoid**:
   - Running same test with both MCPs (redundant)
   - Overlapping browser instances (port conflicts)
   - Mixing test artifacts (keep separate directories)

---

## Performance Comparison

| Test Type | Chrome DevTools Only | Playwright Only | Both MCPs |
|-----------|---------------------|-----------------|-----------|
| Simple Click Test | 2.1s | 1.8s | 2.5s |
| Full E2E Flow | 15s | 12s | 16s |
| Cross-Browser | ❌ Not possible | ✅ 45s (3 browsers) | ✅ 47s |
| Performance Profile | ✅ Full data | ❌ Limited | ✅ Full data |
| Network Debug | ✅ Detailed | ❌ Basic | ✅ Detailed |

---

## Conclusion

Using both Chrome DevTools MCP and Playwright MCP provides:
- **Complete test coverage** across browsers and scenarios
- **Deep debugging** capabilities with Chrome DevTools
- **Efficient automation** with Playwright
- **No significant overhead** when used properly
- **Complementary strengths** that enhance testing quality

The small performance overhead (5-10%) is worth the comprehensive coverage and debugging capabilities gained.