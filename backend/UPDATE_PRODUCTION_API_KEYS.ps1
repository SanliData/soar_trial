***REMOVED*** Update Production API Keys on Google Cloud Run
***REMOVED*** Bu script yeni API key'leri Cloud Run'a günceller

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "SOAR B2B - Production API Keys Update" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Cyan
Write-Host ""

***REMOVED*** 1. Yeni API Key'leri oluştur
Write-Host "[1/4] Yeni Production API Keys oluşturuluyor..." -ForegroundColor Yellow
Write-Host ""
& "scripts\generate_production_api_keys.ps1"
Write-Host ""

***REMOVED*** 2. API Key'leri kullanıcıdan al
Write-Host "[2/4] Yeni API key'leri kopyalayın:" -ForegroundColor Yellow
Write-Host ""
$apiKeys = Read-Host "SOARB2B_API_KEYS (comma-separated, yukarıdaki çıktıdan kopyalayın)"

if ([string]::IsNullOrWhiteSpace($apiKeys)) {
    Write-Host "HATA: API key'leri girmeniz gerekiyor!" -ForegroundColor Red
    exit 1
}

***REMOVED*** 3. GCP Project ID kontrol
Write-Host ""
Write-Host "[3/4] Google Cloud Project kontrol ediliyor..." -ForegroundColor Yellow
$projectId = $env:GCP_PROJECT_ID
if (-not $projectId) {
    $projectId = gcloud config get-value project 2>&1
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($projectId)) {
        $projectId = Read-Host "GCP Project ID girin"
        gcloud config set project $projectId
    }
}

Write-Host "Project ID: $projectId" -ForegroundColor Green

***REMOVED*** 4. Mevcut environment variables'ı al
Write-Host ""
Write-Host "[4/4] Google Cloud Run service güncelleniyor..." -ForegroundColor Yellow

$region = "us-central1"
$serviceName = "soarb2b"

***REMOVED*** Mevcut env vars'ı al (CORS'u korumak için)
Write-Host "Mevcut environment variables kontrol ediliyor..." -ForegroundColor Cyan
$currentEnvVars = gcloud run services describe $serviceName --region $region --format "value(spec.template.spec.containers[0].env)" 2>&1

***REMOVED*** CORS origins'ı koru (varsayılan)
$corsOrigins = "https://soarb2b.com,https://www.soarb2b.com"

***REMOVED*** Update komutu
Write-Host ""
Write-Host "API key'leri güncelleniyor..." -ForegroundColor Cyan
Write-Host "Service: $serviceName" -ForegroundColor White
Write-Host "Region: $region" -ForegroundColor White
Write-Host ""

gcloud run services update $serviceName `
    --region $region `
    --update-env-vars "SOARB2B_API_KEYS=$apiKeys" `
    --update-env-vars "FINDEROS_CORS_ORIGINS=$corsOrigins" `
    --update-env-vars "ENV=production"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "="*70 -ForegroundColor Green
    Write-Host "✅ API KEYS BAŞARIYLA GÜNCELLENDİ!" -ForegroundColor Green
    Write-Host "="*70 -ForegroundColor Green
    Write-Host ""
    Write-Host "Yeni API Key'leri:" -ForegroundColor Cyan
    $keys = $apiKeys -split ","
    for ($i = 0; $i -lt $keys.Length; $i++) {
        Write-Host "  Key $($i+1): $($keys[$i])" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "⚠️  ÖNEMLİ: Bu key'leri GÜVENLİ bir yerde saklayın!" -ForegroundColor Yellow
    Write-Host "⚠️  GitHub'a ASLA commit etmeyin!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Test için:" -ForegroundColor Cyan
    $serviceUrl = gcloud run services describe $serviceName --region $region --format "value(status.url)" 2>&1
    if ($serviceUrl) {
        Write-Host "  curl -H `"X-API-Key: $($keys[0])`" $serviceUrl/api/v1/b2b/demo/hotels" -ForegroundColor White
    }
} else {
    Write-Host ""
    Write-Host "="*70 -ForegroundColor Red
    Write-Host "❌ GÜNCELLEME BAŞARISIZ!" -ForegroundColor Red
    Write-Host "="*70 -ForegroundColor Red
    Write-Host ""
    Write-Host "Hata detayları yukarıda gösterilmiştir." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
