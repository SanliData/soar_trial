***REMOVED***!/bin/bash
***REMOVED*** DEPLOY_TO_CLOUD_RUN.sh
***REMOVED*** PURPOSE: Deploy backend to Cloud Run with Secret Manager secrets
***REMOVED*** ENCODING: UTF-8 WITHOUT BOM

set -e  ***REMOVED*** Exit on error

PROJECT_ID="finderos-entegrasyon-480708"
SERVICE_NAME="soarb2b"
REGION="us-central1"
SERVICE_ACCOUNT="soarb2b@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🚀 Deploying to Cloud Run"
echo "========================"
echo "Project: ${PROJECT_ID}"
echo "Service: ${SERVICE_NAME}"
echo "Region: ${REGION}"
echo ""

***REMOVED*** Deploy with Secret Manager secrets
echo "Deploying service..."
gcloud run deploy ${SERVICE_NAME} \
  --source backend \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  --service-account=${SERVICE_ACCOUNT} \
  --set-secrets="GOOGLE_CLIENT_ID=google-client-id:latest,JWT_SECRET=jwt-secret:latest,QUOTE_SECRET=quote-secret:latest" \
  --allow-unauthenticated \
  --quiet

echo ""
echo "✅ Deployment complete!"
echo ""

***REMOVED*** Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  --format="value(status.url)")

echo "🌐 Service URL: ${SERVICE_URL}"
echo ""

***REMOVED*** Test endpoint
echo "🧪 Testing auth config endpoint..."
sleep 3  ***REMOVED*** Wait for service to be ready

AUTH_RESPONSE=$(curl -s "${SERVICE_URL}/v1/auth/config" || echo "ERROR")

if echo "${AUTH_RESPONSE}" | grep -q "oauth_enabled.*true"; then
  echo "✅ Auth config endpoint working correctly!"
  echo ""
  echo "Response:"
  echo "${AUTH_RESPONSE}" | jq . 2>/dev/null || echo "${AUTH_RESPONSE}"
else
  echo "⚠️  Warning: Auth config endpoint may not be working correctly"
  echo ""
  echo "Response:"
  echo "${AUTH_RESPONSE}"
fi

echo ""
echo "=============================================="
echo "✅ Deployment Complete!"
echo "=============================================="
echo ""
echo "📋 Summary:"
echo "  ✅ Code deployed to Cloud Run"
echo "  ✅ Secrets from Secret Manager"
echo "  ✅ Service account configured"
echo ""
echo "🌐 Service URL: ${SERVICE_URL}"
echo ""
echo "✅ Production-ready!"
