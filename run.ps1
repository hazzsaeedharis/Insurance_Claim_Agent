# Insurance Claim Agent - Simple Runner
# Quick commands to run the system

param(
    [string]$Command = "help",
    [switch]$Help
)

if ($Help -or $Command -eq "help") {
    Write-Host "Insurance Claim Agent - Quick Commands" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Available commands:" -ForegroundColor Yellow
    Write-Host "  test       - Test all components (logging, metrics, claims)" -ForegroundColor Cyan
    Write-Host "  docker     - Start full Docker infrastructure" -ForegroundColor Cyan
    Write-Host "  status     - Show current system status" -ForegroundColor Cyan
    Write-Host "  help       - Show this help message" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1 test        # Test all components" -ForegroundColor White
    Write-Host "  .\run.ps1 docker      # Start Docker services" -ForegroundColor White
    Write-Host "  .\run.ps1 status      # Show status" -ForegroundColor White
    exit
}

function Test-Components {
    Write-Host "Testing Insurance Claim Agent Components" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
    # Test logger
    Write-Host "`nTesting Logger..." -ForegroundColor Yellow
    & .\.venv\Scripts\python.exe services\common\logger.py
    
    # Test metrics
    Write-Host "`nTesting Metrics..." -ForegroundColor Yellow
    & .\.venv\Scripts\python.exe services\common\metrics.py
    
    # Generate claims
    Write-Host "`nGenerating Claims..." -ForegroundColor Yellow
    & .\.venv\Scripts\python.exe data\gen_synthetic_claims.py
    
    Write-Host "`nComponent testing complete!" -ForegroundColor Green
}

function Start-Docker {
    Write-Host "Starting Docker Infrastructure" -ForegroundColor Green
    Write-Host "==============================" -ForegroundColor Green
    
    try {
        docker --version | Out-Null
        Write-Host "Docker found - starting services..." -ForegroundColor Yellow
        
        Set-Location "infra"
        docker-compose up --build
        Set-Location ".."
        
    } catch {
        Write-Host "Docker not available. Please install Docker Desktop." -ForegroundColor Red
        Write-Host "You can still test components with: .\run.ps1 test" -ForegroundColor Yellow
    }
}

function Show-Status {
    Write-Host "Insurance Claim Agent Status" -ForegroundColor Green
    Write-Host "============================" -ForegroundColor Green
    
    # Check Python environment
    if (Test-Path ".venv") {
        Write-Host "Python Environment: OK" -ForegroundColor Green
    } else {
        Write-Host "Python Environment: Missing (run setup.ps1)" -ForegroundColor Red
    }
    
    # Check Docker
    try {
        docker --version | Out-Null
        Write-Host "Docker: Available" -ForegroundColor Green
    } catch {
        Write-Host "Docker: Not available" -ForegroundColor Yellow
    }
    
    # Check data files
    $claimCount = (Get-ChildItem "data\synthetic\*.json" -ErrorAction SilentlyContinue).Count
    Write-Host "Synthetic Claims: $claimCount files" -ForegroundColor Cyan
    
    $policyCount = (Get-ChildItem "data\policies\*\*.pdf" -ErrorAction SilentlyContinue).Count
    Write-Host "Policy Documents: $policyCount files" -ForegroundColor Cyan
    
    Write-Host "`nRecommendation: Start with '.\run.ps1 test'" -ForegroundColor Blue
}

# Execute command
switch ($Command.ToLower()) {
    "test" { Test-Components }
    "docker" { Start-Docker }
    "status" { Show-Status }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\run.ps1 help' for available commands" -ForegroundColor Yellow
    }
}