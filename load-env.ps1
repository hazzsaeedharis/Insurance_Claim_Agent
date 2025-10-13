# Load environment variables from .env file
# Usage: . .\load-env.ps1

if (-not (Test-Path .env)) {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    Write-Host "Run .\setup-api-keys.ps1 to create one" -ForegroundColor Yellow
    return
}

Write-Host "[>] Loading environment variables from .env..." -ForegroundColor Cyan

$envVars = 0
Get-Content .env | ForEach-Object {
    # Skip empty lines and comments
    if ($_ -match '^\s*$' -or $_ -match '^\s*#') {
        return
    }
    
    # Parse KEY=VALUE
    if ($_ -match '^([^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        
        # Set environment variable
        [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
        $envVars++
        
        # Show non-sensitive variables
        if ($key -notlike "*KEY*" -and $key -notlike "*PASSWORD*") {
            Write-Host "  [OK] $key = $value" -ForegroundColor Gray
        } else {
            Write-Host "  [OK] $key = ****" -ForegroundColor Gray
        }
    }
}

Write-Host "[OK] Loaded $envVars environment variables" -ForegroundColor Green
Write-Host ""
