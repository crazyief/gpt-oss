# GPT-OSS Agent Setup Script
# This script verifies the multi-agent system is properly configured

Write-Host "GPT-OSS Multi-Agent System Setup Verification" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Check Claude Code agents
Write-Host "`nChecking Claude Code Agents..." -ForegroundColor Yellow
$claudeAgentPath = "$env:USERPROFILE\.claude\agents"
$requiredAgents = @(
    "gpt-oss-pm-architect.md",
    "gpt-oss-backend.md",
    "gpt-oss-frontend.md",
    "gpt-oss-document-rag.md",
    "gpt-oss-qa.md"
)

$missingAgents = @()
foreach ($agent in $requiredAgents) {
    $agentFile = Join-Path $claudeAgentPath $agent
    if (Test-Path $agentFile) {
        Write-Host "  ✓ $agent" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $agent" -ForegroundColor Red
        $missingAgents += $agent
    }
}

# Check super-ai-ultrathink separately (already exists)
if (Test-Path "$claudeAgentPath\super-ai-ultrathink.md") {
    Write-Host "  ✓ super-ai-ultrathink.md (existing)" -ForegroundColor Green
}

# Check message bus role definitions
Write-Host "`nChecking Message Bus Role Definitions..." -ForegroundColor Yellow
$messageBusPath = "D:\gpt-oss\.claude-bus\agents"
$roleDefinitions = @(
    "PM-Architect-Agent.md",
    "Backend-Agent.md",
    "Frontend-Agent.md",
    "Document-RAG-Agent.md",
    "QA-Agent.md",
    "Super-AI-UltraThink-Agent.md"
)

foreach ($role in $roleDefinitions) {
    $roleFile = Join-Path $messageBusPath $role
    if (Test-Path $roleFile) {
        Write-Host "  ✓ $role" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $role" -ForegroundColor Red
    }
}

# Check message bus directories
Write-Host "`nChecking Message Bus Structure..." -ForegroundColor Yellow
$messageBusDirs = @(
    "D:\gpt-oss\.claude-bus\planning",
    "D:\gpt-oss\.claude-bus\tasks",
    "D:\gpt-oss\.claude-bus\contracts",
    "D:\gpt-oss\.claude-bus\code",
    "D:\gpt-oss\.claude-bus\reviews",
    "D:\gpt-oss\.claude-bus\help",
    "D:\gpt-oss\.claude-bus\dependencies"
)

foreach ($dir in $messageBusDirs) {
    if (Test-Path $dir) {
        Write-Host "  ✓ $(Split-Path $dir -Leaf)/" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $(Split-Path $dir -Leaf)/ (creating...)" -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "    Created!" -ForegroundColor Green
    }
}

# Check events log
$eventsLog = "D:\gpt-oss\.claude-bus\events.jsonl"
if (Test-Path $eventsLog) {
    Write-Host "  ✓ events.jsonl" -ForegroundColor Green
} else {
    Write-Host "  ✗ events.jsonl (creating...)" -ForegroundColor Yellow
    New-Item -ItemType File -Path $eventsLog -Force | Out-Null
    # Add initial event
    $initEvent = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        event = "system_initialized"
        agent = "setup-script"
        message = "Multi-agent system initialized"
    } | ConvertTo-Json -Compress
    Add-Content -Path $eventsLog -Value $initEvent
    Write-Host "    Created with initial event!" -ForegroundColor Green
}

# Summary
Write-Host "`n=============================================" -ForegroundColor Cyan
if ($missingAgents.Count -eq 0) {
    Write-Host "✓ All Claude Code agents are installed!" -ForegroundColor Green
    Write-Host "`nNext Steps:" -ForegroundColor Yellow
    Write-Host "1. Restart Claude Code to refresh agent list"
    Write-Host "2. Select a gpt-oss-* agent from the dropdown"
    Write-Host "3. The agent will load its role definition automatically"
    Write-Host "`nTo use agents manually:" -ForegroundColor Yellow
    Write-Host "- Click the agent dropdown in Claude Code"
    Write-Host "- Choose the appropriate gpt-oss-* agent"
    Write-Host "- Start working on your assigned tasks!"
} else {
    Write-Host "✗ Some agents are missing!" -ForegroundColor Red
    Write-Host "Missing agents: $($missingAgents -join ', ')" -ForegroundColor Red
    Write-Host "`nPlease ensure all agent files have been created."
}

Write-Host "`nMessage Bus Status:" -ForegroundColor Yellow
Write-Host "All directories are ready for multi-agent communication!"
Write-Host "`nFor more information, see:" -ForegroundColor Cyan
Write-Host "  D:\gpt-oss\.claude-bus\AGENT_ARCHITECTURE.md"