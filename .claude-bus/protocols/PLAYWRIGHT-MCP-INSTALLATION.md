# Playwright MCP Installation Guide for Claude Code

**Version**: 1.0.0
**Date**: 2024-11-23
**Target**: Windows development environment

---

## Overview

This guide walks you through installing Microsoft's Playwright MCP server for Claude Code, enabling cross-browser E2E testing and test automation alongside the existing Chrome DevTools MCP.

---

## Prerequisites

- ✅ Node.js installed (v18 or later)
- ✅ Claude Code (Claude Desktop) installed
- ✅ Chrome DevTools MCP already configured (optional but recommended)

---

## Installation Steps

### Step 1: Install Playwright MCP Server (5 minutes)

**Option A: Global Installation (Recommended)**

```bash
# Install Playwright test framework
npm install -g @playwright/test

# Install Playwright MCP server (Microsoft official)
npm install -g @playwright/mcp

# Install browser binaries
npx playwright install chromium firefox webkit
```

**Option B: Project-Local Installation**

```bash
cd D:\gpt-oss

# Install Playwright MCP as dev dependency
npm install --save-dev @playwright/test @playwright/mcp

# Install browser binaries
npx playwright install
```

---

### Step 2: Configure Claude Code (2 minutes)

**Locate Claude Code Config File**:

Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Edit `claude_desktop_config.json`**:

Add Playwright MCP server configuration:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "@executeautomation/mcp-chrome-devtools"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

**Note**: Using `npx @playwright/mcp@latest` ensures you always get the latest version without global installation.

---

### Step 3: Restart Claude Code (1 minute)

1. Close Claude Code completely (exit from system tray)
2. Reopen Claude Code
3. Wait for MCP servers to initialize (~10 seconds)

---

### Step 4: Verify Installation (2 minutes)

**Test 1: Check Available Tools**

In Claude Code, ask:
```
What Playwright tools do you have access to?
```

You should see tools like:
- `playwright__launch_browser`
- `playwright__navigate`
- `playwright__screenshot`
- `playwright__click`
- `playwright__fill`
- `playwright__codegen`
- And many more...

**Test 2: Simple Navigation Test**

Ask Claude Code:
```
Use Playwright MCP to navigate to https://example.com and take a screenshot
```

Claude should successfully:
1. Launch browser (default: Chromium)
2. Navigate to example.com
3. Take screenshot
4. Return screenshot or confirmation

---

## Troubleshooting

### Issue 1: "MCP server failed to start"

**Symptom**: Claude Code shows MCP connection error

**Solution**:
```bash
# Verify Node.js version
node --version  # Should be v18+

# Reinstall Playwright
npm install -g @playwright/test @playwright/mcp
npx playwright install

# Test if Playwright MCP is accessible
npx @playwright/mcp@latest --help
```

### Issue 2: "Browser not found"

**Symptom**: Playwright can't launch browsers

**Solution**:
```bash
# Install all browser binaries
npx playwright install chromium
npx playwright install firefox
npx playwright install webkit

# Or install all at once
npx playwright install
```

### Issue 3: "Permission denied" on Windows

**Symptom**: Browser installation fails

**Solution**:
1. Run PowerShell as Administrator
2. Execute installation commands
3. Restart Claude Code

### Issue 4: Both MCPs conflict

**Symptom**: Chrome DevTools stops working after adding Playwright

**Solution**:
- This should NOT happen - they use different ports (9222 vs 9223)
- Verify both entries exist in `claude_desktop_config.json`
- Restart Claude Code
- Check Claude Code logs: `%APPDATA%\Claude\logs\`

---

## Configuration Files Updated

After installation, these project files have been updated:

1. **`.claude-bus/config/mcp-config.json`**
   - Added Playwright configuration
   - Defined tool selection rules
   - Configured agent permissions

2. **`.claude-bus/protocols/browser-testing-protocol.md`**
   - Added MCP selection guide
   - Updated coordination rules
   - Added usage examples

3. **`.claude-bus/agents/Frontend-Agent.md`** (to be updated)
   - Add Playwright tool declarations
   - Define usage scenarios

4. **`.claude-bus/agents/QA-Agent.md`** (to be updated)
   - Add full Playwright tool access
   - Cross-browser testing guidelines

---

## Next Steps After Installation

1. **Update Agent Definitions** - Add Playwright tools to Frontend-Agent and QA-Agent
2. **Create Test Examples** - Reference examples in `.claude-bus/protocols/dual-mcp-testing-examples.md`
3. **Start Using** - Begin with simple component tests, expand to cross-browser E2E
4. **Maintain Both MCPs** - Keep Chrome DevTools for debugging, use Playwright for automation

---

## Quick Reference

### When to Use Playwright MCP

✅ **Use Playwright MCP for**:
- Cross-browser testing (Firefox, Safari)
- E2E test writing and generation
- Visual regression testing
- API + UI combined testing
- Test automation in CI/CD

❌ **Don't use Playwright MCP for**:
- Performance profiling (use Chrome DevTools)
- Network request debugging (use Chrome DevTools)
- Real-time console monitoring (use Chrome DevTools)
- SSE/WebSocket debugging (use Chrome DevTools)

### When to Use Chrome DevTools MCP

✅ **Use Chrome DevTools MCP for**:
- Performance profiling (LCP, CLS, TTFB)
- Network inspection (request timing, headers)
- Console error monitoring
- Accessibility tree inspection
- SSE/WebSocket debugging

### When to Use Both Together

🔥 **Use Both for**:
- Comprehensive test coverage (Chrome DevTools finds bugs, Playwright prevents regressions)
- Cross-environment validation (debug in Chrome, verify in Firefox)
- Complete QA workflow (profile performance, automate tests)

---

## Support Resources

- **Playwright MCP GitHub**: https://github.com/microsoft/playwright-mcp
- **Playwright Docs**: https://playwright.dev/docs/intro
- **executeautomation MCP**: https://github.com/executeautomation/mcp-playwright
- **Project Documentation**: `.claude-bus/protocols/browser-testing-protocol.md`
- **Usage Examples**: `.claude-bus/protocols/dual-mcp-testing-examples.md`

---

## Version History

- **v1.0.0** (2024-11-23) - Initial installation guide for dual MCP setup

