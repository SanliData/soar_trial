***REMOVED*** Port 8000 kullanan islemi kapat
$port = 8000
$pids = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique | Where-Object { $_ -gt 0 }
if ($pids) {
    foreach ($pid in $pids) {
        Write-Host "Port $port kullanan PID: $pid - Kapatiliyor..."
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Write-Host "Tamam. Simdi sunucuyu tekrar baslatabilirsiniz: python -m uvicorn src.app:app --host 127.0.0.1 --port 8000"
} else {
    Write-Host "Port $port kullanan islem bulunamadi."
}
