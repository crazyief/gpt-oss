# Service Health Check Script for Phase 2 Prerequisites
# Run this before starting Development Phase to ensure all services are ready

Write-Host "=== GPT-OSS Service Health Check ===" -ForegroundColor Cyan
Write-Host ""

$allHealthy = $true

# Function to test service health
function Test-ServiceHealth {
    param(
        [string]$ServiceName,
        [string]$HealthCheckCommand,
        [string]$FallbackCommand,
        [bool]$Required
    )

    Write-Host "Checking $ServiceName..." -NoNewline

    try {
        $result = Invoke-Expression $HealthCheckCommand 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓ OK" -ForegroundColor Green
            return $true
        } else {
            throw "Health check failed"
        }
    }
    catch {
        if ($Required) {
            Write-Host " ✗ FAILED" -ForegroundColor Red
            Write-Host "  Fallback: $FallbackCommand" -ForegroundColor Yellow
            return $false
        } else {
            Write-Host " ⚠ Not running (optional)" -ForegroundColor Yellow
            return $true
        }
    }
}

# Check llama.cpp LLM Service
$healthy = Test-ServiceHealth `
    -ServiceName "llama.cpp (LLM Service)" `
    -HealthCheckCommand "curl -f http://localhost:8080/v1/models" `
    -FallbackCommand "docker-compose logs llama | check for errors" `
    -Required $true
$allHealthy = $allHealthy -and $healthy

# Check Neo4j
$healthy = Test-ServiceHealth `
    -ServiceName "Neo4j (Knowledge Graph)" `
    -HealthCheckCommand "curl -f http://localhost:7474" `
    -FallbackCommand "docker-compose up -d neo4j" `
    -Required $true
$allHealthy = $allHealthy -and $healthy

# Check ChromaDB
$healthy = Test-ServiceHealth `
    -ServiceName "ChromaDB (Vector Store)" `
    -HealthCheckCommand "curl -f http://localhost:8001/api/v1/heartbeat" `
    -FallbackCommand "docker-compose up -d chroma" `
    -Required $true
$allHealthy = $allHealthy -and $healthy

# Check Backend (optional - may not exist yet)
$healthy = Test-ServiceHealth `
    -ServiceName "Backend FastAPI" `
    -HealthCheckCommand "curl -f http://localhost:8000/health" `
    -FallbackCommand "Not required for Stage 1" `
    -Required $false
$allHealthy = $allHealthy -and $healthy

Write-Host ""
if ($allHealthy) {
    Write-Host "=== All Required Services Healthy ✓ ===" -ForegroundColor Green
    Write-Host "Ready to start Phase 2 Development" -ForegroundColor Green
    exit 0
} else {
    Write-Host "=== Some Services Failed ✗ ===" -ForegroundColor Red
    Write-Host "Please fix failed services before starting Phase 2" -ForegroundColor Red
    Write-Host "Run: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}
