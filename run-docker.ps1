# Insurance Claim Agent - Docker Runner
# Start the full infrastructure using Docker Compose

param(
    [string]$Action = "up",
    [switch]$Help,
    [switch]$Build,
    [switch]$Detached
)

if ($Help) {
    Write-Host "🏥 Insurance Claim Agent - Docker Runner" -ForegroundColor Green
    Write-Host "Usage: .\run-docker.ps1 [-Action <action>] [-Build] [-Detached] [-Help]" -ForegroundColor White
    Write-Host ""
    Write-Host "Available actions:" -ForegroundColor Yellow
    Write-Host "  up         - Start all services (default)" -ForegroundColor Cyan
    Write-Host "  down       - Stop all services" -ForegroundColor Cyan
    Write-Host "  status     - Show service status" -ForegroundColor Cyan
    Write-Host "  logs       - Show service logs" -ForegroundColor Cyan
    Write-Host "  restart    - Restart all services" -ForegroundColor Cyan
    Write-Host "  clean      - Stop and remove volumes" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Build     - Force rebuild of containers" -ForegroundColor Cyan
    Write-Host "  -Detached  - Run in background (for 'up' action)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\run-docker.ps1                    # Start all services" -ForegroundColor White
    Write-Host "  .\run-docker.ps1 -Action down       # Stop all services" -ForegroundColor White
    Write-Host "  .\run-docker.ps1 -Build -Detached   # Build and run in background" -ForegroundColor White
    exit
}

# Check if Docker is available
try {
    docker --version | Out-Null
    Write-Host "✅ Docker found" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found or not running" -ForegroundColor Red
    Write-Host "   Please install Docker Desktop and ensure it's running" -ForegroundColor Yellow
    exit 1
}

# Check if docker-compose.yml exists
if (!(Test-Path "infra\docker-compose.yml")) {
    Write-Host "❌ docker-compose.yml not found in infra directory" -ForegroundColor Red
    exit 1
}

# Change to infra directory
Set-Location "infra"

Write-Host "🏥 Insurance Claim Agent - Docker Infrastructure" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

function Start-Services {
    Write-Host "🚀 Starting services..." -ForegroundColor Yellow
    
    $buildFlag = if ($Build) { "--build" } else { "" }
    $detachFlag = if ($Detached) { "-d" } else { "" }
    
    $command = "docker-compose up $buildFlag $detachFlag"
    Write-Host "Running: $command" -ForegroundColor Gray
    
    Invoke-Expression $command
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Services started successfully!" -ForegroundColor Green
        Show-ServiceInfo
    } else {
        Write-Host "`n❌ Failed to start services" -ForegroundColor Red
    }
}

function Stop-Services {
    Write-Host "🛑 Stopping services..." -ForegroundColor Yellow
    docker-compose down
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Services stopped successfully!" -ForegroundColor Green
    }
}

function Show-Status {
    Write-Host "📊 Service Status:" -ForegroundColor Yellow
    docker-compose ps
}

function Show-Logs {
    Write-Host "📄 Service Logs:" -ForegroundColor Yellow
    docker-compose logs --tail=50
}

function Restart-Services {
    Write-Host "🔄 Restarting services..." -ForegroundColor Yellow
    docker-compose restart
}

function Clean-All {
    Write-Host "🧹 Stopping services and cleaning volumes..." -ForegroundColor Yellow
    docker-compose down -v --remove-orphans
    Write-Host "✅ Cleanup complete!" -ForegroundColor Green
}

function Show-ServiceInfo {
    Write-Host "`n📋 Service Information:" -ForegroundColor Green
    Write-Host "  🔐 Keycloak Admin:    http://localhost:8080 (admin/admin123)" -ForegroundColor Cyan
    Write-Host "  🗃️  PostgreSQL:       localhost:5432 (insurance_admin/dev_password_123)" -ForegroundColor Cyan
    Write-Host "  📦 MinIO Console:     http://localhost:9001 (minioadmin/minioadmin123)" -ForegroundColor Cyan
    Write-Host "  🔄 Redis:             localhost:6379" -ForegroundColor Cyan
    Write-Host "  🐰 RabbitMQ Mgmt:     http://localhost:15672 (rabbitmq/rabbitmq123)" -ForegroundColor Cyan
    Write-Host "  ❤️  Health Check:     http://localhost:8000/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "💡 To view logs: .\run-docker.ps1 -Action logs" -ForegroundColor Yellow
    Write-Host "💡 To stop: .\run-docker.ps1 -Action down" -ForegroundColor Yellow
}

# Execute the requested action
switch ($Action.ToLower()) {
    "up" { Start-Services }
    "down" { Stop-Services }
    "status" { Show-Status }
    "logs" { Show-Logs }
    "restart" { Restart-Services }
    "clean" { Clean-All }
    default {
        Write-Host "❌ Unknown action: $Action" -ForegroundColor Red
        Write-Host "Run with -Help to see available actions" -ForegroundColor Yellow
        Set-Location ".."
        exit 1
    }
}

# Return to original directory
Set-Location ".."