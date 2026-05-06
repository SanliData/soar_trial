***REMOVED*** Simple FinderOS Server Start Script
***REMOVED*** Run this from the backend directory

$ErrorActionPreference = "Stop"

$backendPath = (Get-Location).Path
$pythonExe = "C:\Users\issan\AppData\Local\Programs\Python\Python311\python.exe"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting FinderOS Server" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

***REMOVED*** Activate virtual environment if exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".venv\Scripts\Activate.ps1"
} elseif (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

***REMOVED*** Set PYTHONPATH
$env:PYTHONPATH = $backendPath
Write-Host "PYTHONPATH set to: $env:PYTHONPATH" -ForegroundColor Green

***REMOVED*** Start server
Write-Host ""
Write-Host "Starting server on http://localhost:8000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

***REMOVED*** Check port availability before starting
Write-Host "Checking port 8000..." -ForegroundColor Yellow
$portCheck = & $pythonExe -m src.core.port_check --check 8000 2>&1
if ($LASTEXITCODE -ne 0 -or $portCheck -match "is in use") {
    Write-Host "WARNING: Port 8000 may be in use" -ForegroundColor Yellow
    Write-Host "To free the port, run: python -m src.core.port_check --kill 8000" -ForegroundColor Yellow
    Write-Host ""
}

***REMOVED*** Use uvicorn directly (reload disabled on Windows by default in main.py)
***REMOVED*** Server will check port and exit with clear error if unavailable
& $pythonExe src/main.py


