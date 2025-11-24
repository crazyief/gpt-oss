# Playwright MCP Installation Guide

## Overview

This guide provides step-by-step instructions for installing and configuring Microsoft's Playwright MCP alongside the existing Chrome DevTools MCP setup.

**Created**: 2024-11-23
**Purpose**: Enable cross-browser E2E testing and test generation capabilities

---

## Prerequisites

1. **Node.js**: Version 18 or newer required
2. **Claude Code**: Already configured with Chrome DevTools MCP
3. **Project Path**: D:\gpt-oss

---

## Installation Steps

### Step 1: Install Playwright MCP Package

Open terminal in project root:

```bash
cd D:\gpt-oss

# Option 1: Global installation (recommended for Claude Code)
npx @playwright/mcp@latest

# Option 2: Project-specific installation
npm install --save-dev @playwright/mcp

# Install Playwright browsers (if not already installed)
npx playwright install
```

### Step 2: Configure Claude Code

Locate your Claude Code configuration file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add Playwright MCP to the configuration:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      // ... existing Chrome DevTools config ...
    },
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp",
        "--browser", "chromium",
        "--timeout", "30000"
      ],
      "env": {
        "NODE_ENV": "development",
        "PLAYWRIGHT_BROWSERS_PATH": "0"
      }
    }
  }
}
```

### Step 3: Verify Installation

1. **Restart Claude Code** completely (close and reopen)
2. **Check available tools** - Playwright tools should appear
3. **Test basic functionality**:
   ```
   Use Playwright MCP to navigate to https://example.com and take a screenshot
   ```

### Step 4: Create Test Directories

```bash
# Create Playwright test result directories
mkdir -p .claude-bus/test-results/playwright/screenshots
mkdir -p .claude-bus/test-results/playwright/videos
mkdir -p .claude-bus/test-results/playwright/traces
mkdir -p .claude-bus/test-results/playwright/reports
```

---

## Configuration Options

### Basic Configuration

```json
{
  "command": "npx",
  "args": ["@playwright/mcp"],
  "env": {}
}
```

### Advanced Configuration

```json
{
  "command": "npx",
  "args": [
    "@playwright/mcp",
    "--browser", "chromium",         // or firefox, webkit
    "--headed",                       // Show browser window
    "--timeout", "30000",            // 30 second timeout
    "--viewport", "1920,1080",      // Screen size
    "--device", "iPhone 12",         // Mobile emulation
    "--proxy", "http://proxy:8080",  // Proxy settings
    "--trace", "on",                 // Enable tracing
    "--video", "on"                  // Record videos
  ],
  "env": {
    "NODE_ENV": "development",
    "DEBUG": "playwright:*"          // Enable debug logs
  }
}
```

---

## Docker Integration

If running in Docker, add Playwright service to `docker-compose.yml`:

```yaml
services:
  playwright:
    image: mcr.microsoft.com/playwright:v1.40.0-focal
    ports:
      - "9223:9223"
    volumes:
      - ./frontend:/app/frontend
      - ./.claude-bus/test-results:/app/test-results
    environment:
      - NODE_ENV=development
    command: npx @playwright/mcp --port 9223
```

---

## Agent Configuration Updates

### Frontend-Agent.md

Add to MCP tools declaration:

```yaml
mcp_tools:
  chrome_devtools:
    - take_snapshot
    - click
    - fill
    # ... existing tools ...
  playwright:
    - navigate
    - screenshot
    - click
    - fill
    - hover
    - select
    - codegen
```

### QA-Agent.md

Add full Playwright access:

```yaml
mcp_tools:
  chrome_devtools:
    - "*"  # Full access
  playwright:
    - "*"  # Full access to all Playwright tools
```

---

## Testing the Integration

### Basic Test

```javascript
// Test Playwright MCP is working
async function testPlaywright() {
  // Navigate to test page
  await playwright__navigate("http://localhost:5173");

  // Take screenshot
  await playwright__screenshot({
    fullPage: true,
    path: ".claude-bus/test-results/playwright/test.png"
  });

  // Click element
  await playwright__click("#submit-button");

  console.log("Playwright MCP test successful!");
}
```

### Cross-Browser Test

```javascript
// Test across multiple browsers
const browsers = ["chromium", "firefox", "webkit"];

for (const browser of browsers) {
  await playwright__launch_browser({ browser });
  await playwright__navigate("http://localhost:5173");
  await playwright__screenshot({
    path: `.claude-bus/test-results/playwright/${browser}-screenshot.png`
  });
  await playwright__close_browser();
}
```

---

## Troubleshooting

### Problem: Playwright tools not appearing in Claude Code

**Solution**:
1. Verify Node.js version: `node --version` (must be 18+)
2. Check config file path is correct
3. Restart Claude Code completely
4. Check logs for errors

### Problem: Browser launch fails

**Solution**:
1. Install browsers: `npx playwright install`
2. Check permissions for browser executables
3. Verify no firewall blocking
4. Try headless mode first

### Problem: Port conflict with Chrome DevTools

**Solution**:
1. Use different ports (9222 for Chrome DevTools, 9223 for Playwright)
2. Check no other services using ports
3. Kill any zombie browser processes

### Problem: Tests timeout quickly

**Solution**:
1. Increase timeout in config: `--timeout 60000`
2. Check network connectivity
3. Verify services are running
4. Use `--slow-mo 500` to slow down actions

---

## Best Practices

1. **Use Chrome DevTools for**:
   - Performance profiling
   - Network debugging
   - Console monitoring
   - Memory analysis

2. **Use Playwright for**:
   - Cross-browser testing
   - E2E test automation
   - Test code generation
   - Visual regression testing
   - API testing

3. **Coordination**:
   - Run both MCPs on different ports
   - Use lock files to prevent conflicts
   - Keep test artifacts separate
   - Document which MCP each test uses

4. **Performance**:
   - Limit concurrent browser instances
   - Close browsers after tests
   - Clean up old test artifacts
   - Use headless mode in CI/CD

---

## Migration from Chrome DevTools Only

No migration needed! Both MCPs work together:

1. **Keep existing Chrome DevTools tests** - They still work
2. **Add new Playwright tests** - For cross-browser needs
3. **Gradually adopt** - Use Playwright for new E2E tests
4. **Maintain both** - Each has unique strengths

---

## References

- [Playwright MCP GitHub](https://github.com/microsoft/playwright-mcp)
- [Playwright Documentation](https://playwright.dev)
- Chrome DevTools MCP Config: `.claude-bus/config/mcp-config.json`
- Browser Testing Protocol: `.claude-bus/protocols/browser-testing-protocol.md`

---

## Support

If you encounter issues:
1. Check this guide first
2. Review error logs
3. Consult PM-Architect-Agent
4. Escalate to Super-AI-UltraThink-Agent if needed