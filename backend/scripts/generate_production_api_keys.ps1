***REMOVED*** Generate Production API Keys for SOAR B2B
***REMOVED*** PowerShell script to generate secure API keys

Write-Host ""
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "SOAR B2B - Production API Key Generator" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Cyan
Write-Host ""

***REMOVED*** Try Python from common locations
$python = $null
$pythonPaths = @(
    "python",
    "python3",
    ".venv\Scripts\python.exe",
    "venv\Scripts\python.exe",
    "C:\Python311\python.exe",
    "C:\Python312\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe"
)

foreach ($path in $pythonPaths) {
    if (Test-Path $path -ErrorAction SilentlyContinue) {
        try {
            $result = & $path --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $python = $path
                break
            }
        } catch {
            continue
        }
    }
}

if ($python) {
    Write-Host "Using Python: $python" -ForegroundColor Yellow
    Write-Host ""
    & $python "scripts\generate_production_api_keys.py"
} else {
    Write-Host "Python bulunamadı. Manuel olarak şu komutu çalıştırın:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  python scripts/generate_production_api_keys.py" -ForegroundColor White
    Write-Host ""
    Write-Host "VEYA PowerShell ile:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "***REMOVED*** Generate 3 random API keys" -ForegroundColor Gray
    Write-Host '$keys = @(); 1..3 | ForEach-Object { $keys += -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 43 | ForEach-Object {[char]$_}) }; "SOARB2B_API_KEYS=" + ($keys -join ",")' -ForegroundColor White
    Write-Host ""
}
