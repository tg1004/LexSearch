# LexSearch stack verification (run from project root)
# Usage: .\scripts\verify_stack.ps1

$ErrorActionPreference = "Continue"
Write-Host ""
Write-Host "=== LexSearch Stack Verification ===" -ForegroundColor Cyan
Write-Host ""

function Test-Endpoint {
    param([string]$Name, [string]$Url)
    try {
        $null = Invoke-WebRequest -Uri $Url -TimeoutSec 8 -UseBasicParsing
        Write-Host "OK  $Name" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "FAIL $Name - $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

$pg = docker compose ps postgres --format "{{.Status}}" 2>$null
if ($pg -match "healthy") {
    Write-Host "OK  Postgres container healthy" -ForegroundColor Green
} else {
    Write-Host "WARN Postgres: $pg" -ForegroundColor Yellow
}

$redis = docker compose ps redis --format "{{.Status}}" 2>$null
if ($redis -match "Up") {
    Write-Host "OK  Redis running" -ForegroundColor Green
} else {
    Write-Host "FAIL Redis not running" -ForegroundColor Red
}

Test-Endpoint "Elasticsearch" "http://localhost:9200/_cluster/health" | Out-Null
Test-Endpoint "Qdrant healthz" "http://localhost:6333/healthz" | Out-Null

try {
    $collections = Invoke-RestMethod -Uri "http://localhost:6333/collections" -TimeoutSec 8
    $name = $collections.result.collections.name
    if ($name -contains "legal_judgements") {
        Write-Host "OK  Qdrant collection legal_judgements exists" -ForegroundColor Green
    } else {
        Write-Host "WARN Qdrant collection legal_judgements not found - run data pipeline" -ForegroundColor Yellow
    }
} catch {
    Write-Host "FAIL Qdrant collections API - $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $es = Invoke-RestMethod -Uri "http://localhost:9200/legal_judgements/_count" -TimeoutSec 8
    Write-Host "OK  Elasticsearch index count: $($es.count)" -ForegroundColor Green
} catch {
    Write-Host "WARN Elasticsearch index legal_judgements - $($_.Exception.Message)" -ForegroundColor Yellow
}

try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 5
    Write-Host "OK  Backend API: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "INFO Backend not running on port 8000 - start with uvicorn" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Done." -ForegroundColor Cyan
Write-Host ""
