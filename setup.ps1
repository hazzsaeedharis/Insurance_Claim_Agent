# Insurance Claim Agent - Setup Script
# This script sets up your development environment

Write-Host "🏥 Insurance Claim Agent - Setup" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if virtual environment exists
if (Test-Path ".venv") {
    Write-Host "✅ Python virtual environment found" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install Python dependencies if requirements.txt exists
if (Test-Path "requirements.txt") {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Create logs directory
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Name "logs" -Force | Out-Null
    Write-Host "📁 Created logs directory" -ForegroundColor Green
}

# Copy environment variables
if (!(Test-Path "infra\.env")) {
    if (Test-Path "infra\.env.example") {
        Copy-Item "infra\.env.example" "infra\.env"
        Write-Host "📝 Created .env file from example" -ForegroundColor Green
        Write-Host "   Edit infra\.env to customize settings" -ForegroundColor Yellow
    }
}

Write-Host "`n🎉 Setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor White
Write-Host "1. Run individual components: .\run-components.ps1" -ForegroundColor Cyan
Write-Host "2. Start full infrastructure: .\run-docker.ps1" -ForegroundColor Cyan
Write-Host "3. View available commands: .\run-help.ps1" -ForegroundColor Cyan