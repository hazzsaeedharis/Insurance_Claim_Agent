# Insurance Claim Processing - Docker Demo Startup
# This script starts all services in Docker containers

Write-Host "[>] Starting Insurance Claim Processing System" -ForegroundColor Green
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "[ERROR] Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (!(Test-Path .env)) {
    Write-Host "[WARNING] .env file not found. Copying from env.template..." -ForegroundColor Yellow
    Copy-Item env.template .env
    Write-Host "[INFO] Please edit .env file with your API keys before continuing." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter after you've updated the .env file"
}

# Load environment variables
Write-Host "[>] Loading environment variables..." -ForegroundColor Cyan
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

# Navigate to infra directory
cd infra

Write-Host "[>] Starting Docker services..." -ForegroundColor Cyan
Write-Host ""

# Start services
docker-compose up -d

Write-Host ""
Write-Host "[>] Waiting for services to be healthy..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Check service health
Write-Host ""
Write-Host "[>] Service Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "[SUCCESS] Docker services started!" -ForegroundColor Green
Write-Host ""
Write-Host "Available Services:" -ForegroundColor Yellow
Write-Host "  - PostgreSQL:          http://localhost:5432" -ForegroundColor Gray
Write-Host "  - MinIO Console:       http://localhost:9001" -ForegroundColor Gray
Write-Host "  - Keycloak:            http://localhost:8080" -ForegroundColor Gray
Write-Host "  - Redis:               http://localhost:6379" -ForegroundColor Gray
Write-Host "  - RabbitMQ Console:    http://localhost:15672" -ForegroundColor Gray
Write-Host "  - AI Processing API:   http://localhost:8005" -ForegroundColor Gray
Write-Host ""
Write-Host "Check AI Service Health:" -ForegroundColor Yellow
Write-Host "  curl http://localhost:8005/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "View Logs:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f ai-processing-service" -ForegroundColor Cyan
Write-Host ""
Write-Host "Stop All Services:" -ForegroundColor Yellow
Write-Host "  docker-compose down" -ForegroundColor Cyan
Write-Host ""

