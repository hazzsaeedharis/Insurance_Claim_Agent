# Start Web Demo with AI Backend
# This script starts the AI API and opens the web interface

Write-Host "`n=== Starting ClaimAI Pro Web Demo ===" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (!(Test-Path ".venv")) {
    Write-Host "[ERROR] Virtual environment not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (!(Test-Path ".env")) {
    Write-Host "[WARNING] .env file not found. API keys may not be configured." -ForegroundColor Yellow
}

# Start the AI Processing API in background
Write-Host "[>] Starting AI Processing API on port 8005..." -ForegroundColor Cyan
$apiJob = Start-Job -ScriptBlock {
    param($dir)
    cd $dir
    & "$dir\.venv\Scripts\python.exe" -m uvicorn services.ai_processing.api:app --host 0.0.0.0 --port 8005 --reload
} -ArgumentList $PWD

Write-Host "[OK] API starting in background (Job ID: $($apiJob.Id))" -ForegroundColor Green

# Wait for API to be ready
Write-Host "[>] Waiting for API to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Test API health
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8005/health" -Method Get -TimeoutSec 5
    Write-Host "[OK] API is healthy!" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] API may still be starting up..." -ForegroundColor Yellow
}

# Start a simple HTTP server for the web interface
Write-Host "[>] Starting web server on port 8080..." -ForegroundColor Cyan
cd web
$webJob = Start-Job -ScriptBlock {
    param($dir)
    cd "$dir\web"
    python -m http.server 8080
} -ArgumentList $PWD.Parent

Write-Host "[OK] Web server started (Job ID: $($webJob.Id))" -ForegroundColor Green

# Open browser
Write-Host "[>] Opening browser..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
Start-Process "http://localhost:8080"

Write-Host ""
Write-Host "=== Demo is Ready! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Web Interface:  http://localhost:8080" -ForegroundColor Cyan
Write-Host "API Docs:       http://localhost:8005/docs" -ForegroundColor Cyan
Write-Host "Health Check:   http://localhost:8005/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both services" -ForegroundColor Yellow
Write-Host ""

# Keep script running and monitor jobs
try {
    while ($true) {
        # Check if jobs are still running
        $apiStatus = Get-Job -Id $apiJob.Id
        $webStatus = Get-Job -Id $webJob.Id
        
        if ($apiStatus.State -ne "Running" -or $webStatus.State -ne "Running") {
            Write-Host "[WARNING] A service has stopped" -ForegroundColor Yellow
            break
        }
        
        Start-Sleep -Seconds 5
    }
} finally {
    Write-Host "`n[>] Stopping services..." -ForegroundColor Yellow
    Stop-Job -Id $apiJob.Id, $webJob.Id -ErrorAction SilentlyContinue
    Remove-Job -Id $apiJob.Id, $webJob.Id -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Services stopped" -ForegroundColor Green
}

