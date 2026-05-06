***REMOVED*** Check and optionally kill process holding a port
***REMOVED*** Usage: .\scripts\check_port.ps1 [--port 8000] [--kill]

param(
    [int]$Port = 8000,
    [switch]$Kill
)

$ErrorActionPreference = "Stop"

***REMOVED*** Find Python executable
$pythonExe = $null
if (Test-Path ".venv\Scripts\python.exe") {
    $pythonExe = ".venv\Scripts\python.exe"
} elseif (Test-Path "venv\Scripts\python.exe") {
    $pythonExe = "venv\Scripts\python.exe"
} else {
    $pythonExe = "python"
}

Write-Host "Checking port $Port..." -ForegroundColor Yellow
Write-Host ""

if ($Kill) {
    & $pythonExe -m src.core.port_check --kill $Port
} else {
    & $pythonExe -m src.core.port_check --check $Port
}
