***REMOVED*** SOAR B2B - Production Deployment Script
***REMOVED*** Google Cloud Run'a deploy etmek için hazır script

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "SOAR B2B - Production Deployment to Google Cloud Run" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Cyan
Write-Host ""

***REMOVED*** 1. API Key'leri oluştur
Write-Host "[1/5] Production API Keys oluşturuluyor..." -ForegroundColor Yellow
& "scripts\generate_production_api_keys.ps1"
Write-Host ""

***REMOVED*** 2. API Key'leri kullanıcıdan al
Write-Host "[2/5] API Key'leri Google Cloud Run'a eklemek için hazırlanıyor..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Yukarıda oluşturulan API key'leri kopyalayın ve aşağıya yapıştırın:" -ForegroundColor Cyan
$apiKeys = Read-Host "SOARB2B_API_KEYS (comma-separated)"

if ([string]::IsNullOrWhiteSpace($apiKeys)) {
    Write-Host "HATA: API key'leri girmeniz gerekiyor!" -ForegroundColor Red
    exit 1
}

***REMOVED*** 3. GCP Project ID kontrol
Write-Host ""
Write-Host "[3/5] Google Cloud Project kontrol ediliyor..." -ForegroundColor Yellow
$projectId = $env:GCP_PROJECT_ID
if (-not $projectId) {
    $projectId = gcloud config get-value project 2>&1
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($projectId)) {
        $projectId = Read-Host "GCP Project ID girin"
        gcloud config set project $projectId
    }
}

Write-Host "Project ID: $projectId" -ForegroundColor Green

***REMOVED*** 4. Domain/CORS ayarları
Write-Host ""
Write-Host "[4/5] CORS ayarları..." -ForegroundColor Yellow
$corsOrigins = Read-Host "CORS Origins (comma-separated, örn: https://soarb2b.com,https://www.soarb2b.com)"
if ([string]::IsNullOrWhiteSpace($corsOrigins)) {
    $corsOrigins = "https://soarb2b.com,https://www.soarb2b.com"
    Write-Host "Varsayılan kullanılıyor: $corsOrigins" -ForegroundColor Yellow
}

***REMOVED*** 5. Deployment
Write-Host ""
Write-Host "[5/5] Google Cloud Run'a deploy ediliyor..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Deployment başlatılıyor..." -ForegroundColor Cyan
Write-Host "Bu işlem birkaç dakika sürebilir..." -ForegroundColor Yellow
Write-Host ""

$region = "us-central1"
$serviceName = "soarb2b"

$deployCmd = @(
    "gcloud", "run", "deploy", $serviceName,
    "--source", ".",
    "--region", $region,
    "--platform", "managed",
    "--allow-unauthenticated",
    "--memory", "512Mi",
    "--cpu", "1",
    "--timeout", "300",
    "--max-instances", "10",
    "--set-env-vars", "ENV=production,SOARB2B_API_KEYS=$apiKeys,FINDEROS_CORS_ORIGINS=$corsOrigins"
)

& $deployCmd[0] $deployCmd[1..($deployCmd.Length-1)]

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "="*70 -ForegroundColor Green
    Write-Host "✅ DEPLOYMENT BAŞARILI!" -ForegroundColor Green
    Write-Host "="*70 -ForegroundColor Green
    Write-Host ""
    
    ***REMOVED*** Service URL'ini al
    $serviceUrl = gcloud run services describe $serviceName --region $region --format "value(status.url)" 2>&1
    if ($LASTEXITCODE -eq 0 -and $serviceUrl) {
        Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Test komutları:" -ForegroundColor Yellow
        Write-Host "  Health Check: Invoke-WebRequest $serviceUrl/healthz -UseBasicParsing" -ForegroundColor White
        Write-Host "  Homepage: Start-Process $serviceUrl/ui/tr/soarb2b_home.html" -ForegroundColor White
        Write-Host ""
        Write-Host "API Key'leri GÜVENLİ bir yerde sakladığınızdan emin olun!" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "="*70 -ForegroundColor Red
    Write-Host "❌ DEPLOYMENT BAŞARISIZ!" -ForegroundColor Red
    Write-Host "="*70 -ForegroundColor Red
    Write-Host ""
    Write-Host "Hata detayları yukarıda gösterilmiştir." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
