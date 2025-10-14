# Insurance Claim Agent - Component Runner
# Run individual components for development and testing

param(
    [string]$Component = "all",
    [switch]$Help
)

if ($Help) {
    Write-Host "🏥 Insurance Claim Agent - Component Runner" -ForegroundColor Green
    Write-Host "Usage: .\run-components.ps1 [-Component <name>] [-Help]" -ForegroundColor White
    Write-Host ""
    Write-Host "Available components:" -ForegroundColor Yellow
    Write-Host "  logger     - Test logging module" -ForegroundColor Cyan
    Write-Host "  metrics    - Test metrics module" -ForegroundColor Cyan
    Write-Host "  claims     - Generate synthetic claims data" -ForegroundColor Cyan
    Write-Host "  all        - Run all component tests (default)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\run-components.ps1 -Component logger" -ForegroundColor White
    Write-Host "  .\run-components.ps1" -ForegroundColor White
    exit
}

# Ensure virtual environment is activated
if (!(Test-Path env:VIRTUAL_ENV)) {
    Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}

Write-Host "🏥 Running Insurance Claim Agent Components" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

function Test-Logger {
    Write-Host "`n📝 Testing Logger Module..." -ForegroundColor Yellow
    & .\.venv\Scripts\python.exe services\common\logger.py
}

function Test-Metrics {
    Write-Host "`n📊 Testing Metrics Module..." -ForegroundColor Yellow
    & .\.venv\Scripts\python.exe services\common\metrics.py
}

function Test-Claims {
    Write-Host "`n🔍 Generating Synthetic Claims..." -ForegroundColor Yellow
    & .\.venv\Scripts\python.exe data\gen_synthetic_claims.py
}

function Show-Status {
    Write-Host "`n📋 Current Status:" -ForegroundColor Green
    Write-Host "  • Synthetic claims: " -NoNewline
    $claimCount = (Get-ChildItem "data\synthetic\*.json" -ErrorAction SilentlyContinue).Count
    Write-Host "$claimCount files" -ForegroundColor Cyan
    
    Write-Host "  • Policy documents: " -NoNewline
    $policyCount = (Get-ChildItem "data\policies\*\*.pdf" -ErrorAction SilentlyContinue).Count
    Write-Host "$policyCount files" -ForegroundColor Cyan
    
    Write-Host "  • Sample documents: " -NoNewline
    $sampleCount = (Get-ChildItem "data\samples\*\*.pdf" -ErrorAction SilentlyContinue).Count
    Write-Host "$sampleCount files" -ForegroundColor Cyan
    
    if (Test-Path "logs") {
        Write-Host "  • Log files: " -NoNewline
        $logCount = (Get-ChildItem "logs\*.log" -ErrorAction SilentlyContinue).Count
        Write-Host "$logCount files" -ForegroundColor Cyan
    }
}

# Run specific component or all
switch ($Component.ToLower()) {
    "logger" { Test-Logger }
    "metrics" { Test-Metrics }
    "claims" { Test-Claims }
    "all" {
        Test-Logger
        Test-Metrics
        Test-Claims
        Show-Status
    }
    default {
        Write-Host "❌ Unknown component: $Component" -ForegroundColor Red
        Write-Host "Run with -Help to see available components" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "`n✅ Component testing complete!" -ForegroundColor Green