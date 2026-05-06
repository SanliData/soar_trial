***REMOVED*** Run SOAR B2B locally
***REMOVED*** This script activates venv and starts the server

$ErrorActionPreference = "Stop"

$backendPath = (Get-Location).Path
if (-not (Test-Path "src")) {
    Write-Host "Error: Must run from backend directory" -ForegroundColor Red
    exit 1
}

***REMOVED*** Activate virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".venv\Scripts\Activate.ps1"
} elseif (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

***REMOVED*** Determine Python executable (prefer venv python)
$PYTHON = "python"
if (Test-Path ".\.venv\Scripts\python.exe") {
    $PYTHON = ".\.venv\Scripts\python.exe"
    Write-Host "Using venv Python: $PYTHON" -ForegroundColor Green
} elseif (Test-Path "venv\Scripts\python.exe") {
    $PYTHON = "venv\Scripts\python.exe"
    Write-Host "Using venv Python: $PYTHON" -ForegroundColor Green
} else {
    Write-Host "Using system Python (venv not found)" -ForegroundColor Yellow
}

***REMOVED*** Set PYTHONPATH
$env:PYTHONPATH = $backendPath
$env:ENV = "development"

***REMOVED*** Create data directory if needed
if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
    Write-Host "Created data directory" -ForegroundColor Green
}

***REMOVED*** Print UI URLs
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SOAR B2B - Local Development Server" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will start on: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "UI Pages:" -ForegroundColor Yellow
Write-Host "  - Home: http://127.0.0.1:8000/ui/soarb2b_home.html" -ForegroundColor White
Write-Host "  - Onboarding: http://127.0.0.1:8000/ui/soarb2b_onboarding_5q.html" -ForegroundColor White
Write-Host "  - Demo: http://127.0.0.1:8000/ui/demo_showcase.html" -ForegroundColor White
Write-Host "  - Case Library: http://127.0.0.1:8000/ui/case_library_index.html" -ForegroundColor White
Write-Host ""
Write-Host "API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

***REMOVED*** Start server using safe_run (handles port conflicts automatically)
***REMOVED*** safe_run will check port, ask to kill blocking processes, and start uvicorn
& $PYTHON -m src.scripts.safe_run

***REMOVED*** If safe_run exits with error, stop script
if ($LASTEXITCODE -ne 0) {
    Write-Host "" -ForegroundColor Red
    Write-Host "Failed to start server (exit code: $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}
