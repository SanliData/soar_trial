***REMOVED*** SOAR B2B - Port 9000'de baslat
Set-Location $PSScriptRoot
if (Test-Path .venv\Scripts\Activate.ps1) { .\.venv\Scripts\Activate.ps1 }
Write-Host "Sunucu baslatiliyor: http://127.0.0.1:9000" -ForegroundColor Cyan
Write-Host "Durdurmak icin Ctrl+C" -ForegroundColor Yellow
python -m uvicorn src.app:app --host 127.0.0.1 --port 9000
