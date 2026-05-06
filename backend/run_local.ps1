***REMOVED*** Run backend locally (Windows PowerShell)

Write-Host "Starting SOAR B2B Backend..." -ForegroundColor Cyan
Write-Host ""

***REMOVED*** Change to backend directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

***REMOVED*** Activate virtual environment if exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

***REMOVED*** Run safe_run.py
Write-Host "Starting uvicorn server..." -ForegroundColor Yellow
Write-Host ""
python -m src.scripts.safe_run
