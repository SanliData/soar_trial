***REMOVED*** Port 9001'i kullanan islemi kapat, sonra sunucuyu baslat
$port = 9001
$found = netstat -ano | findstr ":$port.*LISTENING"
if ($found) {
    $pidLine = ($found -split '\s+')[-1]
    if ($pidLine -match '^\d+$') {
        Write-Host "Port $port kullanan islem (PID $pidLine) kapatiliyor..." -ForegroundColor Yellow
        taskkill /F /PID $pidLine 2>$null
        Start-Sleep -Seconds 1
    }
}
Write-Host "Sunucu baslatiliyor: http://127.0.0.1:$port" -ForegroundColor Cyan
Set-Location $PSScriptRoot
python -m uvicorn src.app:app --host 127.0.0.1 --port $port
