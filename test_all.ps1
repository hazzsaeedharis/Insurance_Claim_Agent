# Insurance Claim Agent - Complete System Test

Write-Host ""
Write-Host "===== INSURANCE CLAIM AGENT - SYSTEM TEST =====" -ForegroundColor Cyan
Write-Host ""

$passed = 0
$failed = 0

# Test Python Environment
Write-Host "Testing Python Environment..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe --version
if ($LASTEXITCODE -eq 0) { $passed++ } else { $failed++ }

# Test Logging Module
Write-Host "`nTesting Logging Module..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe -c "from services.common.logger import get_logger; logger = get_logger('test'); logger.info('Test'); print('Logger OK')"
if ($LASTEXITCODE -eq 0) { $passed++ } else { $failed++ }

# Test Metrics Module  
Write-Host "`nTesting Metrics Module..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe -c "from services.common.metrics import increment; increment('test'); print('Metrics OK')"
if ($LASTEXITCODE -eq 0) { $passed++ } else { $failed++ }

# Test Auth Module
Write-Host "`nTesting Auth Module..." -ForegroundColor Yellow
cd services\common
..\..\..\.venv\Scripts\python.exe -c "from auth_middleware import JWTAuthenticator; print('Auth OK')"
if ($LASTEXITCODE -eq 0) { $passed++ } else { $failed++ }
cd ..\..

# Test Claims Generator
Write-Host "`nTesting Claims Generator..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe data\gen_synthetic_claims.py
if ($LASTEXITCODE -eq 0) { $passed++ } else { $failed++ }

# Check Docker Services
Write-Host "`nChecking Docker Services..." -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check Project Structure
Write-Host "`nChecking Project Structure..." -ForegroundColor Yellow
Get-ChildItem -Directory | Select-Object Name

# Summary
Write-Host ""
Write-Host "===== TEST SUMMARY =====" -ForegroundColor Cyan
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red

if ($failed -eq 0) {
    Write-Host "`nALL TESTS PASSED!" -ForegroundColor Green
} else {
    Write-Host "`nSome tests failed." -ForegroundColor Red
}