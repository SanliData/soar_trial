***REMOVED*** SOAR B2B - Simple Deployment Script
***REMOVED*** Windows PowerShell

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SOAR B2B Production Deployment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendPath

***REMOVED*** Check Docker
Write-Host "[1/5] Checking Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "  Docker is ready" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

***REMOVED*** Check .env file
Write-Host "[2/5] Checking .env file..." -ForegroundColor Yellow
$envFile = Join-Path $backendPath ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "  .env file not found. Creating from template..." -ForegroundColor Yellow
    
    ***REMOVED*** Generate API keys
    Write-Host "  Generating production API keys..." -ForegroundColor Yellow
    $pythonExe = $null
    if (Test-Path ".venv\Scripts\python.exe") {
        $pythonExe = ".venv\Scripts\python.exe"
    } else {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            $pythonExe = "python"
        }
    }
    
    if ($pythonExe) {
        $apiKeysOutput = & $pythonExe -c "import secrets; keys = [secrets.token_urlsafe(32) for _ in range(3)]; print(','.join(keys))"
        $apiKeys = $apiKeysOutput.Trim()
    } else {
        Write-Host "  WARNING: Python not found. Using default keys (CHANGE IN PRODUCTION!)" -ForegroundColor Yellow
        $apiKeys = "dev-key-12345,dev-key-67890,dev-key-abcde"
    }
    
    ***REMOVED*** Create .env file
    @"
ENV=production
PORT=8000
SOARB2B_API_KEYS=$apiKeys
FINDEROS_CORS_ORIGINS=https://soarb2b.com,https://www.soarb2b.com
FINDEROS_CORS_ALLOW_ALL=false
FINDEROS_HOST=0.0.0.0
FINDEROS_PORT=8000
"@ | Out-File -FilePath $envFile -Encoding utf8
    
    Write-Host "  .env file created with API keys" -ForegroundColor Green
} else {
    Write-Host "  .env file exists" -ForegroundColor Green
    
    ***REMOVED*** Check if SOARB2B_API_KEYS is set
    $envContent = Get-Content $envFile -Raw
    if ($envContent -notmatch "SOARB2B_API_KEYS") {
        Write-Host "  WARNING: SOARB2B_API_KEYS not found in .env" -ForegroundColor Yellow
        Write-Host "  Add: SOARB2B_API_KEYS=your-key-1,your-key-2,your-key-3" -ForegroundColor Yellow
    }
}

***REMOVED*** Build Docker image
Write-Host "[3/5] Building Docker image..." -ForegroundColor Yellow
try {
    docker build -t soarb2b:latest . 2>&1 | Out-Null
    Write-Host "  Docker image built successfully" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Docker build failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

***REMOVED*** Stop existing container
Write-Host "[4/5] Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>&1 | Out-Null
$existing = docker ps -a --filter "name=soarb2b" --format "{{.Names}}"
if ($existing) {
    docker stop $existing 2>&1 | Out-Null
    docker rm $existing 2>&1 | Out-Null
    Write-Host "  Existing containers stopped" -ForegroundColor Green
}

***REMOVED*** Start with docker-compose
Write-Host "[5/5] Starting application..." -ForegroundColor Yellow
try {
    docker-compose up -d 2>&1 | Out-Null
    Start-Sleep -Seconds 3
    
    ***REMOVED*** Check health
    $healthCheck = Invoke-WebRequest -Uri "http://127.0.0.1:8000/healthz" -UseBasicParsing -ErrorAction SilentlyContinue
    if ($healthCheck -and $healthCheck.StatusCode -eq 200) {
        Write-Host "  Application started successfully" -ForegroundColor Green
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Deployment Complete!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Application URL:" -ForegroundColor Cyan
        Write-Host "  http://127.0.0.1:8000/ui/soarb2b_home.html" -ForegroundColor White
        Write-Host ""
        Write-Host "Health Check:" -ForegroundColor Cyan
        Write-Host "  http://127.0.0.1:8000/healthz" -ForegroundColor White
        Write-Host ""
        Write-Host "View logs:" -ForegroundColor Cyan
        Write-Host "  docker-compose logs -f" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "  WARNING: Health check failed. Check logs:" -ForegroundColor Yellow
        Write-Host "  docker-compose logs" -ForegroundColor White
    }
} catch {
    Write-Host "  ERROR: Failed to start application" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Check logs: docker-compose logs" -ForegroundColor Yellow
    exit 1
}
