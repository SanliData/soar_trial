***REMOVED*** PowerShell script to setup Google Cloud Secret Manager secrets for SOAR B2B
***REMOVED*** Run this script to create secrets in Secret Manager

$ErrorActionPreference = "Stop"

$PROJECT_ID = if ($env:GOOGLE_CLOUD_PROJECT_ID) { $env:GOOGLE_CLOUD_PROJECT_ID } else { "finderos-entegrasyon-480708" }
$REGION = if ($env:REGION) { $env:REGION } else { "us-central1" }

Write-Host "Setting up secrets for project: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

***REMOVED*** Generate secure JWT_SECRET (64 bytes = 86 chars in base64)
try {
    $JWT_SECRET = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 86 | ForEach-Object {[char]$_})
    ***REMOVED*** Use a more secure method if available
    $bytes = New-Object byte[] 64
    [System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
    $JWT_SECRET = [Convert]::ToBase64String($bytes).Substring(0, 86)
} catch {
    Write-Host "Warning: Using less secure random generation" -ForegroundColor Yellow
    $JWT_SECRET = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 86 | ForEach-Object {[char]$_})
}

if ([string]::IsNullOrEmpty($JWT_SECRET)) {
    Write-Host "ERROR: Failed to generate JWT_SECRET" -ForegroundColor Red
    exit 1
}

***REMOVED*** Get GOOGLE_CLIENT_ID from env-vars file or use default
$GOOGLE_CLIENT_ID = if ($env:GOOGLE_CLIENT_ID) { $env:GOOGLE_CLIENT_ID } else { "274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com" }

if ([string]::IsNullOrEmpty($GOOGLE_CLIENT_ID)) {
    Write-Host "ERROR: GOOGLE_CLIENT_ID not set" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Creating secrets in Secret Manager..." -ForegroundColor Cyan
Write-Host ""

***REMOVED*** Create GOOGLE_CLIENT_ID secret
Write-Host "Creating GOOGLE_CLIENT_ID secret..." -ForegroundColor Yellow
try {
    gcloud secrets create GOOGLE_CLIENT_ID `
        --project="$PROJECT_ID" `
        --replication-policy="automatic" 2>$null
    Write-Host "  Created new secret" -ForegroundColor Green
} catch {
    Write-Host "  Secret already exists" -ForegroundColor Yellow
}

$GOOGLE_CLIENT_ID | gcloud secrets versions add GOOGLE_CLIENT_ID `
    --project="$PROJECT_ID" `
    --data-file=-

***REMOVED*** Create JWT_SECRET secret
Write-Host "Creating JWT_SECRET secret..." -ForegroundColor Yellow
try {
    gcloud secrets create JWT_SECRET `
        --project="$PROJECT_ID" `
        --replication-policy="automatic" 2>$null
    Write-Host "  Created new secret" -ForegroundColor Green
} catch {
    Write-Host "  Secret already exists" -ForegroundColor Yellow
}

$JWT_SECRET | gcloud secrets versions add JWT_SECRET `
    --project="$PROJECT_ID" `
    --data-file=-

Write-Host ""
Write-Host "Granting Cloud Run service account access to secrets..." -ForegroundColor Cyan
Write-Host ""

***REMOVED*** Get Cloud Run service account email
$SERVICE_ACCOUNT = if ($env:CLOUD_RUN_SERVICE_ACCOUNT) { 
    $env:CLOUD_RUN_SERVICE_ACCOUNT 
} else { 
    "$PROJECT_ID@appspot.gserviceaccount.com"
}

Write-Host "Using service account: $SERVICE_ACCOUNT" -ForegroundColor Yellow

***REMOVED*** Grant Secret Manager Secret Accessor role
gcloud secrets add-iam-policy-binding GOOGLE_CLIENT_ID `
    --project="$PROJECT_ID" `
    --member="serviceAccount:$SERVICE_ACCOUNT" `
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding JWT_SECRET `
    --project="$PROJECT_ID" `
    --member="serviceAccount:$SERVICE_ACCOUNT" `
    --role="roles/secretmanager.secretAccessor"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Secrets setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Created secrets:" -ForegroundColor Cyan
Write-Host "  - GOOGLE_CLIENT_ID: $GOOGLE_CLIENT_ID"
Write-Host "  - JWT_SECRET: [REDACTED - 86 characters]"
Write-Host ""
Write-Host "Service account granted access: $SERVICE_ACCOUNT"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Deploy Cloud Run service with GOOGLE_CLOUD_PROJECT_ID env var set"
Write-Host "2. Verify secrets are accessible: gcloud secrets versions access latest --secret=GOOGLE_CLIENT_ID"
Write-Host ""
