# Insurance Claim Agent - Help & Quick Start Guide

Write-Host "Insurance Claim Agent - Quick Start Guide" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

Write-Host "`nWhat You Can Run Right Now:" -ForegroundColor Yellow

Write-Host "`n1. Setup Environment" -ForegroundColor White
Write-Host "   .\setup.ps1" -ForegroundColor Cyan
Write-Host "   → Initializes Python environment and dependencies" -ForegroundColor Gray

Write-Host "`n2. 🧪 Test Individual Components" -ForegroundColor White
Write-Host "   .\run-components.ps1                  # Test all components" -ForegroundColor Cyan
Write-Host "   .\run-components.ps1 -Component logger   # Test logging only" -ForegroundColor Cyan
Write-Host "   .\run-components.ps1 -Help               # Show component options" -ForegroundColor Cyan
Write-Host "   → Tests logging, metrics, and data generation" -ForegroundColor Gray

Write-Host "`n3. 🐳 Full Infrastructure (Docker Required)" -ForegroundColor White
Write-Host "   .\run-docker.ps1                      # Start all services" -ForegroundColor Cyan
Write-Host "   .\run-docker.ps1 -Action down         # Stop services" -ForegroundColor Cyan
Write-Host "   .\run-docker.ps1 -Help                # Show Docker options" -ForegroundColor Cyan
Write-Host "   → Starts PostgreSQL, MinIO, Keycloak, Redis, RabbitMQ" -ForegroundColor Gray

Write-Host "`n📊 What's Already Built:" -ForegroundColor Yellow
Write-Host "   ✅ Infrastructure: Docker, K8s, CI/CD pipeline" -ForegroundColor Green
Write-Host "   ✅ Logging: Structured JSON logging with correlation IDs" -ForegroundColor Green
Write-Host "   ✅ Metrics: Prometheus-compatible metrics collection" -ForegroundColor Green
Write-Host "   ✅ Authentication: RBAC roles and Keycloak integration" -ForegroundColor Green
Write-Host "   ✅ Data: Synthetic claims generator and real policy PDFs" -ForegroundColor Green

Write-Host "`n🔍 Quick Health Check:" -ForegroundColor Yellow

# Check Python environment
if (Test-Path ".venv") {
    Write-Host "   ✅ Python virtual environment" -ForegroundColor Green
} else {
    Write-Host "   ❌ Python virtual environment (run setup.ps1)" -ForegroundColor Red
}

# Check Docker
try {
    docker --version | Out-Null
    Write-Host "   ✅ Docker available" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Docker not available (install Docker Desktop)" -ForegroundColor Yellow
}

# Check data files
$claimCount = (Get-ChildItem "data\synthetic\*.json" -ErrorAction SilentlyContinue).Count
Write-Host "   📄 Synthetic claims: $claimCount files" -ForegroundColor Cyan

$policyCount = (Get-ChildItem "data\policies\*\*.pdf" -ErrorAction SilentlyContinue).Count
Write-Host "   📋 Policy documents: $policyCount files" -ForegroundColor Cyan

Write-Host "`n🚀 Quick Start Recommendation:" -ForegroundColor Yellow
Write-Host "   1. .\setup.ps1                       # First time setup" -ForegroundColor White
Write-Host "   2. .\run-components.ps1              # Test what's built" -ForegroundColor White
Write-Host "   3. .\run-docker.ps1                  # Start full stack (if Docker available)" -ForegroundColor White

Write-Host "`n📚 Need More Help?" -ForegroundColor Yellow
Write-Host "   • Check README.md for detailed documentation" -ForegroundColor Gray
Write-Host "   • View Tasks.md to see development progress" -ForegroundColor Gray
Write-Host "   • All scripts support -Help flag" -ForegroundColor Gray

Write-Host "`nPro Tip:" -ForegroundColor Blue
Write-Host "   Run .\run-components.ps1 first to see the core functionality," -ForegroundColor White
Write-Host "   then try .\run-docker.ps1 to experience the full infrastructure!" -ForegroundColor White