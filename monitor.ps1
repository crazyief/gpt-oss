# PowerShell script to monitor message bus activity

Write-Host "===== Message Bus Monitor =====" -ForegroundColor Cyan
Write-Host "Monitoring D:\gpt-oss\.claude-bus\" -ForegroundColor Yellow
Write-Host ""

while ($true) {
    Clear-Host
    Write-Host "===== Message Bus Status =====" -ForegroundColor Cyan
    Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""

    # Show pending tasks
    Write-Host "[TASKS]" -ForegroundColor Green
    $tasks = Get-ChildItem ".claude-bus\tasks\*.json" -ErrorAction SilentlyContinue
    foreach ($task in $tasks) {
        $content = Get-Content $task.FullName | ConvertFrom-Json
        $color = switch ($content.status) {
            "pending" { "Yellow" }
            "in-progress" { "Cyan" }
            "completed" { "Green" }
            "blocked" { "Red" }
            default { "White" }
        }
        Write-Host "  $($content.id): [$($content.status)] $($content.title) -> $($content.assignee)" -ForegroundColor $color
    }

    Write-Host ""
    Write-Host "[HELP REQUESTS]" -ForegroundColor Red
    $helps = Get-ChildItem ".claude-bus\help\*.json" -ErrorAction SilentlyContinue
    foreach ($help in $helps) {
        $content = Get-Content $help.FullName | ConvertFrom-Json
        Write-Host "  $($help.Name): $($content.from) needs help with $($content.type)" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "[RECENT EVENTS]" -ForegroundColor Blue
    if (Test-Path ".claude-bus\events.jsonl") {
        Get-Content ".claude-bus\events.jsonl" -Tail 5 | ForEach-Object {
            if ($_ -ne "") {
                $event = $_ | ConvertFrom-Json
                Write-Host "  [$($event.timestamp)] $($event.agent): $($event.action)" -ForegroundColor Gray
            }
        }
    }

    Write-Host ""
    Write-Host "Press Ctrl+C to exit" -ForegroundColor Gray
    Start-Sleep -Seconds 2
}