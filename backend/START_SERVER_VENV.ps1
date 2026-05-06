***REMOVED*** Start Server using venv Python
***REMOVED*** This script activates venv and starts the server

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SOAR B2B - Starting Server with venv" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

***REMOVED*** Get backend directory (script location)
$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendPath

***REMOVED*** Check for venv
$venvPython = $null
if (Test-Path ".venv\Scripts\python.exe") {
    $venvPython = ".\.venv\Scripts\python.exe"
    Write-Host "Found venv: .venv" -ForegroundColor Green
} elseif (Test-Path "venv\Scripts\python.exe") {
    $venvPython = ".\venv\Scripts\python.exe"
    Write-Host "Found venv: venv" -ForegroundColor Green
} else {
    Write-Host "ERROR: No venv found!" -ForegroundColor Red
    Write-Host "Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor White
    Write-Host "  .venv\Scripts\Activate.ps1" -ForegroundColor White
    exit 1
}

***REMOVED*** Test Python
Write-Host "Testing Python..." -ForegroundColor Yellow
try {
    $pythonVersion = & $venvPython --version 2>&1
    Write-Host "  $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python executable not working!" -ForegroundColor Red
    exit 1
}

***REMOVED*** Set environment variables
$env:PYTHONPATH = (Resolve-Path $backendPath).Path
$env:ENV = "development"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Server..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server URL: http://localhost:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Results Hub:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000/ui/en/soarb2b_results_hub.html?plan_id=TEST" -ForegroundColor White
Write-Host ""
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

***REMOVED*** Start server (--reload-dir src to avoid watching .venv)
& $venvPython -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir src
