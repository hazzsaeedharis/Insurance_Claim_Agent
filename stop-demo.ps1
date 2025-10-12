# InsureClaim AI - Stop Demo Environment

Write-Host "🛑 Stopping InsureClaim AI Demo Environment" -ForegroundColor Yellow
Write-Host "===========================================" -ForegroundColor Yellow

# Stop all containers
Write-Host "`nStopping Docker containers..." -ForegroundColor Yellow
Set-Location infra
docker-compose down
Set-Location ..

Write-Host "`n✅ All services stopped successfully!" -ForegroundColor Green
Write-Host "   To restart, run: .\start-demo.ps1" -ForegroundColor Gray

