# Test Playwright MCP

This file contains test instructions to verify Playwright MCP is working in Claude Code CLI.

## Test Commands

After restarting Claude Code CLI, you can test Playwright MCP with these commands:

### Basic Browser Test
Ask Claude: "Use playwright mcp to open a browser to https://example.com and take a screenshot"

### Navigation Test
Ask Claude: "Use playwright mcp to navigate to https://github.com and search for 'playwright'"

### Form Interaction Test
Ask Claude: "Use playwright mcp to go to https://www.google.com and search for 'Claude AI'"

## Available Playwright MCP Tools

When Playwright MCP is properly installed, you should have access to these tools:
- Browser automation capabilities
- Page navigation
- Element interaction (click, type, etc.)
- Screenshot capture
- Form filling
- Web scraping

## Verification Steps

1. Restart Claude Code CLI (close and reopen)
2. Check available MCP servers: `/mcp`
3. You should see "playwright" listed
4. Try one of the test commands above

## Troubleshooting

If Playwright MCP doesn't appear:
1. Run `claude mcp list` to check status
2. If disconnected, run: `claude mcp remove playwright`
3. Then reinstall: `claude mcp add playwright -s user -- npx -y @executeautomation/playwright-mcp-server`
4. Restart Claude Code CLI