# Setup API Keys for Insurance Claim Agent
# This script helps you set up your API keys safely

Write-Host ""
Write-Host "=== Insurance Claim Agent - API Keys Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (Test-Path .env) {
    Write-Host "[OK] .env file already exists" -ForegroundColor Green
    $overwrite = Read-Host "Do you want to update your API keys? (y/n)"
    if ($overwrite -ne 'y') {
        Write-Host "Setup cancelled." -ForegroundColor Yellow
        exit
    }
} else {
    Write-Host "[>] Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item env.template .env
    Write-Host "[OK] Created .env file" -ForegroundColor Green
}

Write-Host ""
Write-Host "Please enter your API keys (or press Enter to skip):" -ForegroundColor Cyan
Write-Host ""

# Get Groq API Key
Write-Host "1. Groq API Key (REQUIRED)" -ForegroundColor Yellow
Write-Host "   Get it from: https://console.groq.com/keys" -ForegroundColor Gray
$groqKey = Read-Host "   Enter your Groq API key"

if ($groqKey) {
    # Update .env file
    (Get-Content .env) -replace 'GROQ_API_KEY=.*', "GROQ_API_KEY=$groqKey" | Set-Content .env
    Write-Host "   [OK] Groq API key saved" -ForegroundColor Green
} else {
    Write-Host "   [WARNING] Groq API key is required for the system to work!" -ForegroundColor Red
}

Write-Host ""

# Get Gemini API Key
Write-Host "2. Gemini API Key (Recommended - FREE tier available!)" -ForegroundColor Yellow
Write-Host "   Get it from: https://makersuite.google.com/app/apikey" -ForegroundColor Gray
$geminiKey = Read-Host "   Enter your Gemini API key (or press Enter to skip)"

if ($geminiKey) {
    (Get-Content .env) -replace 'GEMINI_API_KEY=.*', "GEMINI_API_KEY=$geminiKey" | Set-Content .env
    Write-Host "   [OK] Gemini API key saved" -ForegroundColor Green
} else {
    Write-Host "   [INFO] Skipping Gemini" -ForegroundColor Yellow
}

Write-Host ""

# Get OpenAI API Key
Write-Host "3. OpenAI API Key (Alternative to Gemini)" -ForegroundColor Yellow
Write-Host "   Get it from: https://platform.openai.com/api-keys" -ForegroundColor Gray
$openaiKey = Read-Host "   Enter your OpenAI API key (or press Enter to skip)"

if ($openaiKey) {
    (Get-Content .env) -replace 'OPENAI_API_KEY=.*', "OPENAI_API_KEY=$openaiKey" | Set-Content .env
    Write-Host "   [OK] OpenAI API key saved" -ForegroundColor Green
} else {
    Write-Host "   [INFO] Skipping OpenAI" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""

# Test the setup
Write-Host "Would you like to test your API keys? (y/n)" -ForegroundColor Cyan
$test = Read-Host

if ($test -eq 'y') {
    Write-Host ""
    Write-Host "[>] Testing Groq API..." -ForegroundColor Yellow
    
    # Load the .env file
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }
    
    # Run the check script
    & .\check-groq-models.ps1
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run 'python test_ai_processing.py' to test the document processing" -ForegroundColor White
Write-Host "2. Your .env file is gitignored and safe from being pushed to GitHub" -ForegroundColor White
Write-Host "3. See API_KEYS_GUIDE.md for more details" -ForegroundColor White
Write-Host ""
