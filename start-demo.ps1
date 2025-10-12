# InsureClaim AI - One-Click Demo Startup
# This script ensures everything is ready for your VC demo

Write-Host "Starting InsureClaim AI Demo Environment" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check if Docker is running
Write-Host "`n[>] Checking prerequisites..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "[OK] Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not installed or not running!" -ForegroundColor Red
    Write-Host "   Please install Docker Desktop from https://docker.com" -ForegroundColor Yellow
    exit 1
}

# Check if Docker daemon is running
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker daemon is not running!" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] Docker daemon is running" -ForegroundColor Green

# Create necessary directories
Write-Host "`n[>] Setting up directories..." -ForegroundColor Yellow
$directories = @("logs", "data/synthetic")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "[OK] Created $dir" -ForegroundColor Green
    }
}

# Check if Python is available for synthetic data generation
Write-Host "`n[>] Checking Python..." -ForegroundColor Yellow
try {
    python --version | Out-Null
    Write-Host "[OK] Python is installed" -ForegroundColor Green
    
    # Generate synthetic claims if needed
    $claimCount = (Get-ChildItem "data\synthetic\*.json" -ErrorAction SilentlyContinue).Count
    if ($claimCount -lt 10) {
        Write-Host "[>] Generating synthetic claims..." -ForegroundColor Yellow
        python data\gen_synthetic_claims.py
        Write-Host "[OK] Generated sample claims" -ForegroundColor Green
    } else {
        Write-Host "[OK] Sample claims already exist" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] Python not found - skipping synthetic data generation" -ForegroundColor Yellow
}

# Stop any existing containers
Write-Host "`n[>] Cleaning up old containers..." -ForegroundColor Yellow
docker-compose -f infra\docker-compose.yml down 2>$null
Write-Host "[OK] Cleanup complete" -ForegroundColor Green

# Start services
Write-Host "`n[>] Starting all services..." -ForegroundColor Yellow
Write-Host "   This may take 2-3 minutes on first run" -ForegroundColor Gray

Set-Location infra
docker-compose up -d --build

# Wait for services to be healthy
Write-Host "`n[>] Waiting for services to be ready..." -ForegroundColor Yellow
$services = @{
    "PostgreSQL" = "http://localhost:5432"
    "MinIO" = "http://localhost:9001"
    "Redis" = "http://localhost:6379"
    "Keycloak" = "http://localhost:8080"
}

$maxRetries = 30
$allHealthy = $false
$retryCount = 0

while (-not $allHealthy -and $retryCount -lt $maxRetries) {
    $allHealthy = $true
    Start-Sleep -Seconds 2
    $retryCount++
    
    # Check if containers are running
    $runningContainers = docker ps --format "table {{.Names}}\t{{.Status}}" 2>$null
    if ($runningContainers -match "unhealthy") {
        $allHealthy = $false
    }
}

Set-Location ..

if ($allHealthy) {
    Write-Host "`n[OK] All services are running!" -ForegroundColor Green
} else {
    Write-Host "`n[WARNING] Some services may still be starting..." -ForegroundColor Yellow
}

# Display access information
Write-Host "`n[DEMO ACCESS POINTS]" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Web Portal:        " -NoNewline; Write-Host "file:///$PWD/web/index.html" -ForegroundColor White
Write-Host "Claims API:        " -NoNewline; Write-Host "http://localhost:8001/docs" -ForegroundColor White
Write-Host "Document Service:  " -NoNewline; Write-Host "http://localhost:8002/docs" -ForegroundColor White
Write-Host "OCR Service:       " -NoNewline; Write-Host "http://localhost:8003/docs" -ForegroundColor White
Write-Host "Processing Service:" -NoNewline; Write-Host "http://localhost:8004/docs" -ForegroundColor White
Write-Host "=====================================" -ForegroundColor Cyan

# Open web portal in browser
Write-Host "`n[>] Opening web portal in browser..." -ForegroundColor Yellow
$webPath = "$PWD\web\index.html"
Start-Process $webPath

# Show demo tips
Write-Host "`n[DEMO TIPS]" -ForegroundColor Yellow
Write-Host "1. Click 'Start Demo' in the web portal for automated flow" -ForegroundColor White
Write-Host "2. Use sample documents from data\samples\documents\" -ForegroundColor White
Write-Host "3. Check DEMO_SCRIPT.md for talking points" -ForegroundColor White
Write-Host "4. To stop all services: .\stop-demo.ps1" -ForegroundColor White

Write-Host "`n[SUCCESS] Demo environment is ready!" -ForegroundColor Green
Write-Host "Good luck with your presentation!" -ForegroundColor Green

