# Script to check available Groq models
# Make sure GROQ_API_KEY is set in your environment

param(
    [string]$ApiKey = $env:GROQ_API_KEY
)

# Try to load .env file if API key not found
if (-not $ApiKey -and (Test-Path .env)) {
    Write-Host "[>] Loading API key from .env file..." -ForegroundColor Cyan
    Get-Content .env | ForEach-Object {
        if ($_ -match '^GROQ_API_KEY=(.+)$') {
            $ApiKey = $matches[1].Trim()
        }
    }
}

if (-not $ApiKey) {
    Write-Host "[ERROR] GROQ_API_KEY not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Option 1: Load from .env file" -ForegroundColor Yellow
    Write-Host '  . .\load-env.ps1' -ForegroundColor Cyan
    Write-Host '  .\check-groq-models.ps1' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Option 2: Set manually" -ForegroundColor Yellow
    Write-Host '  $env:GROQ_API_KEY = "your_api_key_here"' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Option 3: Pass as parameter" -ForegroundColor Yellow
    Write-Host '  .\check-groq-models.ps1 -ApiKey "your_api_key_here"' -ForegroundColor Cyan
    exit 1
}

Write-Host "[>] Checking available Groq models..." -ForegroundColor Green
Write-Host ""

try {
    $headers = @{
        "Authorization" = "Bearer $ApiKey"
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-RestMethod -Uri "https://api.groq.com/openai/v1/models" -Method Get -Headers $headers
    
    Write-Host "[OK] Successfully retrieved models!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Available Models:" -ForegroundColor Cyan
    Write-Host ("-" * 80)
    
    foreach ($model in $response.data) {
        Write-Host "Model ID: " -NoNewline -ForegroundColor Yellow
        Write-Host $model.id -ForegroundColor White
        
        if ($model.owned_by) {
            Write-Host "  Owner: $($model.owned_by)" -ForegroundColor Gray
        }
        
        if ($model.created) {
            $date = [DateTimeOffset]::FromUnixTimeSeconds($model.created).DateTime
            Write-Host "  Created: $($date.ToString('yyyy-MM-dd'))" -ForegroundColor Gray
        }
        
        Write-Host ""
    }
    
    Write-Host ("-" * 80)
    Write-Host "Total models: $($response.data.Count)" -ForegroundColor Green
    
} catch {
    Write-Host "[ERROR] Failed to retrieve models!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host ""
        Write-Host "API key appears to be invalid. Please check your key." -ForegroundColor Yellow
    }
}
