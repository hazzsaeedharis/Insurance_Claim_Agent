# Insurance Claim Agent - System Test Runner
# Tests all components and validates the build

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host " Insurance Claim Agent - System Test" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$testsPassed = 0
$testsFailed = 0

function Test-Component {
    param($Name, $Command, $ExpectedOutput)
    
    Write-Host "`n[TEST] $Name" -ForegroundColor Yellow
    try {
        $output = Invoke-Expression $Command 2>&1
        if ($LASTEXITCODE -eq 0 -or $output -match $ExpectedOutput) {
            Write-Host "  ✓ PASSED" -ForegroundColor Green
            $global:testsPassed++
            return $true
        } else {
            Write-Host "  ✗ FAILED" -ForegroundColor Red
            $global:testsFailed++
            return $false
        }
    } catch {
        Write-Host "  ✗ ERROR: $_" -ForegroundColor Red
        $global:testsFailed++
        return $false
    }
}

# Test 1: Python environment
Test-Component "Python Environment" ".\.venv\Scripts\python.exe --version" "Python 3"

# Test 2: Logger module
Test-Component "Logger Module" ".\.venv\Scripts\python.exe -c 'from services.common.logger import get_logger; print(""OK"")'" "OK"

# Test 3: Metrics module
Test-Component "Metrics Module" ".\.venv\Scripts\python.exe -c 'from services.common.metrics import increment; increment(""test""); print(""OK"")'" "OK"

# Test 4: Auth middleware
Test-Component "Auth Middleware" "cd services\common; ..\..\..\.venv\Scripts\python.exe -c 'from auth_middleware import JWTAuthenticator; print(""OK"")'; cd ..\.." "OK"

# Test 5: Data generation
Test-Component "Claims Generator" ".\.venv\Scripts\python.exe data\gen_synthetic_claims.py" "Successfully generated"

# Test 6: Docker availability
Test-Component "Docker" "docker --version" "Docker version"

# Test 7: Check services status
Write-Host "`n[CHECK] Service Status" -ForegroundColor Yellow
$services = @(
    @{Name="PostgreSQL"; Port=5432},
    @{Name="MinIO"; Port=9000},
    @{Name="Redis"; Port=6379},
    @{Name="RabbitMQ"; Port=5672},
    @{Name="Keycloak"; Port=8080}
)

foreach ($service in $services) {
    $result = Test-NetConnection -ComputerName localhost -Port $service.Port -WarningAction SilentlyContinue
    if ($result.TcpTestSucceeded) {
        Write-Host "  ✓ $($service.Name) is running on port $($service.Port)" -ForegroundColor Green
    } else {
        Write-Host "  ○ $($service.Name) not available on port $($service.Port)" -ForegroundColor Gray
    }
}

# Test 8: File structure
Write-Host "`n[CHECK] Project Structure" -ForegroundColor Yellow
$requiredDirs = @(
    "services\common",
    "services\claims", 
    "data\synthetic",
    "data\policies",
    "infra\migrations",
    "auth",
    "specs"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "  ✓ $dir exists" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ✗ $dir missing" -ForegroundColor Red
        $testsFailed++
    }
}

# Test 9: Critical files
Write-Host "`n[CHECK] Critical Files" -ForegroundColor Yellow
$criticalFiles = @(
    "services\common\logger.py",
    "services\common\metrics.py",
    "services\common\auth_middleware.py",
    "services\claims\api.py",
    "auth\roles.json",
    "specs\claim.json",
    "infra\docker-compose.yml",
    "infra\migrations\0001_create_claims.sql",
    "infra\migrations\0002_create_documents.sql"
)

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ✗ $file missing" -ForegroundColor Red
        $testsFailed++
    }
}

# Summary
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host " Test Summary" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Tests Passed: $testsPassed" -ForegroundColor Green
Write-Host "Tests Failed: $testsFailed" -ForegroundColor $(if ($testsFailed -eq 0) {"Green"} else {"Red"})

if ($testsFailed -eq 0) {
    Write-Host "`n✓ ALL TESTS PASSED! System is ready." -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n✗ Some tests failed. Review the output above." -ForegroundColor Red
    exit 1
}