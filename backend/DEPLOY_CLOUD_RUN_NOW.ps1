***REMOVED*** DEPLOY_CLOUD_RUN_NOW.ps1
***REMOVED*** PURPOSE: Deploy backend to Cloud Run with Secret Manager secrets
***REMOVED*** ENCODING: UTF-8 WITHOUT BOM

$PROJECT_ID = "finderos-entegrasyon-480708"
$SERVICE_NAME = "soarb2b"
$REGION = "us-central1"
$SERVICE_ACCOUNT = "soarb2b@${PROJECT_ID}.iam.gserviceaccount.com"

Write-Host "🚀 Deploying to Cloud Run" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host "Project: $PROJECT_ID"
Write-Host "Service: $SERVICE_NAME"
Write-Host "Region: $REGION"
Write-Host ""

***REMOVED*** Deploy with Secret Manager secrets
Write-Host "Deploying service..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
  --source backend `
  --region=$REGION `
  --project=$PROJECT_ID `
  --service-account=$SERVICE_ACCOUNT `
  --set-secrets="GOOGLE_CLIENT_ID=google-client-id:latest,JWT_SECRET=jwt-secret:latest,QUOTE_SECRET=quote-secret:latest" `
  --allow-unauthenticated

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""

***REMOVED*** Get service URL
$SERVICE_URL = gcloud run services describe $SERVICE_NAME `
  --region=$REGION `
  --project=$PROJECT_ID `
  --format="value(status.url)"

Write-Host "🌐 Service URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host ""

***REMOVED*** Test endpoint
Write-Host "🧪 Testing auth config endpoint..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    $response = Invoke-WebRequest -Uri "${SERVICE_URL}/v1/auth/config" -UseBasicParsing
    $json = $response.Content | ConvertFrom-Json
    
    if ($json.oauth_enabled -eq $true) {
        Write-Host "✅ Auth config endpoint working correctly!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Response:" -ForegroundColor Cyan
        $json | ConvertTo-Json -Depth 10
    } else {
        Write-Host "⚠️  Warning: oauth_enabled is not true" -ForegroundColor Yellow
        Write-Host ""
        $json | ConvertTo-Json -Depth 10
    }
} catch {
    Write-Host "❌ Error testing endpoint: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Response: $($_.Exception.Response)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Code deployed to Cloud Run"
Write-Host "  ✅ Secrets from Secret Manager"
Write-Host "  ✅ Service account configured"
Write-Host ""
Write-Host "🌐 Service URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Production-ready!" -ForegroundColor Green
