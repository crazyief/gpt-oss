# Test Chrome DevTools MCP Server
Write-Host "Testing Chrome DevTools MCP Server..." -ForegroundColor Cyan

# Test 1: Check Node.js version
Write-Host "`nChecking Node.js version..." -ForegroundColor Yellow
$nodeVersion = node --version
Write-Host "Node.js version: $nodeVersion" -ForegroundColor Green

# Test 2: Check npm version
Write-Host "`nChecking npm version..." -ForegroundColor Yellow
$npmVersion = npm --version
Write-Host "npm version: $npmVersion" -ForegroundColor Green

# Test 3: Check Chrome installation
Write-Host "`nChecking Chrome installation..." -ForegroundColor Yellow
if (Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe") {
    Write-Host "Chrome found at: C:\Program Files\Google\Chrome\Application\chrome.exe" -ForegroundColor Green
} else {
    Write-Host "Chrome not found in standard location!" -ForegroundColor Red
}

# Test 4: Check MCP package
Write-Host "`nChecking Chrome DevTools MCP package..." -ForegroundColor Yellow
$mcpVersion = npx -y chrome-devtools-mcp@latest --version
Write-Host "Chrome DevTools MCP version: $mcpVersion" -ForegroundColor Green

# Test 5: Check Claude configuration
Write-Host "`nChecking Claude configuration..." -ForegroundColor Yellow
$configPath = "$env:APPDATA\Claude\claude_desktop_config.json"
if (Test-Path $configPath) {
    $config = Get-Content $configPath | ConvertFrom-Json
    if ($config.mcpServers.'chrome-devtools') {
        Write-Host "Chrome DevTools MCP is configured in Claude!" -ForegroundColor Green
        Write-Host "Configuration:" -ForegroundColor Cyan
        $config.mcpServers.'chrome-devtools' | ConvertTo-Json
    } else {
        Write-Host "Chrome DevTools MCP not found in configuration!" -ForegroundColor Red
    }
} else {
    Write-Host "Claude configuration file not found!" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Restart Claude Code application completely (close all windows)" -ForegroundColor White
Write-Host "2. Open Claude Code again" -ForegroundColor White
Write-Host "3. Run the /mcp command - you should see 'chrome-devtools' listed" -ForegroundColor White
Write-Host "4. Test with: 'Check the performance of https://developers.chrome.com'" -ForegroundColor White