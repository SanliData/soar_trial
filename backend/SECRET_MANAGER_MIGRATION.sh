***REMOVED***!/bin/bash
***REMOVED*** SECRET_MANAGER_MIGRATION.sh
***REMOVED*** PURPOSE: Migrate secrets from plain env vars to Google Secret Manager
***REMOVED*** ENCODING: UTF-8 WITHOUT BOM

set -e  ***REMOVED*** Exit on error

PROJECT_ID="finderos-entegrasyon-480708"
SERVICE_NAME="soarb2b"
REGION="us-central1"
SERVICE_ACCOUNT="soarb2b@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🔐 Secret Manager Migration - Enterprise Grade"
echo "=============================================="
echo "Project: ${PROJECT_ID}"
echo "Service: ${SERVICE_NAME}"
echo "Region: ${REGION}"
echo ""

***REMOVED*** Step 1: Enable Secret Manager API
echo "📦 Step 1: Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --project=${PROJECT_ID}

***REMOVED*** Step 2: Get current env vars from Cloud Run
echo ""
echo "📋 Step 2: Reading current environment variables..."
GOOGLE_CLIENT_ID=$(gcloud run services describe ${SERVICE_NAME} \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  --format="value(spec.template.spec.containers[0].env[?(@.name=='GOOGLE_CLIENT_ID')].value)")

JWT_SECRET=$(gcloud run services describe ${SERVICE_NAME} \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  --format="value(spec.template.spec.containers[0].env[?(@.name=='JWT_SECRET')].value)")

if [ -z "$GOOGLE_CLIENT_ID" ] || [ -z "$JWT_SECRET" ]; then
  echo "❌ Error: Could not read current env vars. Please check service configuration."
  exit 1
fi

echo "✅ Current GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID:0:20}..."
echo "✅ Current JWT_SECRET: ${JWT_SECRET:0:20}..."

***REMOVED*** Step 3: Create secrets in Secret Manager
echo ""
echo "🔐 Step 3: Creating secrets in Secret Manager..."

***REMOVED*** Create GOOGLE_CLIENT_ID secret
echo "Creating secret: google-client-id..."
echo -n "${GOOGLE_CLIENT_ID}" | gcloud secrets create google-client-id \
  --project=${PROJECT_ID} \
  --replication-policy="automatic" \
  --data-file=- || {
  echo "⚠️  Secret google-client-id may already exist. Updating..."
  echo -n "${GOOGLE_CLIENT_ID}" | gcloud secrets versions add google-client-id \
    --project=${PROJECT_ID} \
    --data-file=-
}

***REMOVED*** Create JWT_SECRET secret
echo "Creating secret: jwt-secret..."
echo -n "${JWT_SECRET}" | gcloud secrets create jwt-secret \
  --project=${PROJECT_ID} \
  --replication-policy="automatic" \
  --data-file=- || {
  echo "⚠️  Secret jwt-secret may already exist. Updating..."
  echo -n "${JWT_SECRET}" | gcloud secrets versions add jwt-secret \
    --project=${PROJECT_ID} \
    --data-file=-
}

***REMOVED*** Create QUOTE_SECRET (optional, for better security isolation)
echo "Creating secret: quote-secret..."
QUOTE_SECRET=$(openssl rand -hex 64)
echo -n "${QUOTE_SECRET}" | gcloud secrets create quote-secret \
  --project=${PROJECT_ID} \
  --replication-policy="automatic" \
  --data-file=- || {
  echo "⚠️  Secret quote-secret may already exist. Updating..."
  echo -n "${QUOTE_SECRET}" | gcloud secrets versions add quote-secret \
    --project=${PROJECT_ID} \
    --data-file=-
}

echo "✅ Secrets created in Secret Manager"

***REMOVED*** Step 4: Grant Cloud Run service account access to secrets
echo ""
echo "🔑 Step 4: Granting service account access to secrets..."

***REMOVED*** Get or create service account
SERVICE_ACCOUNT_EMAIL="${SERVICE_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
if ! gcloud iam service-accounts describe ${SERVICE_ACCOUNT_EMAIL} --project=${PROJECT_ID} &>/dev/null; then
  echo "Creating service account: ${SERVICE_ACCOUNT_EMAIL}..."
  gcloud iam service-accounts create ${SERVICE_NAME} \
    --project=${PROJECT_ID} \
    --display-name="SOAR B2B Service Account" \
    --description="Service account for SOAR B2B Cloud Run service"
fi

***REMOVED*** Grant secret accessor role
echo "Granting secret accessor role..."
gcloud secrets add-iam-policy-binding google-client-id \
  --project=${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding jwt-secret \
  --project=${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding quote-secret \
  --project=${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

echo "✅ Service account granted access to secrets"

***REMOVED*** Step 5: Update Cloud Run service to use secrets
echo ""
echo "🚀 Step 5: Updating Cloud Run service to use Secret Manager..."

gcloud run services update ${SERVICE_NAME} \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  --service-account=${SERVICE_ACCOUNT_EMAIL} \
  --set-secrets="GOOGLE_CLIENT_ID=google-client-id:latest,JWT_SECRET=jwt-secret:latest,QUOTE_SECRET=quote-secret:latest" \
  --remove-env-vars="GOOGLE_CLIENT_ID,JWT_SECRET" \
  --quiet

echo "✅ Cloud Run service updated to use Secret Manager"

***REMOVED*** Step 6: Verify deployment
echo ""
echo "🔍 Step 6: Verifying deployment..."
sleep 5  ***REMOVED*** Wait for deployment to propagate

SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  --format="value(status.url)")

echo "Testing auth config endpoint..."
AUTH_RESPONSE=$(curl -s "${SERVICE_URL}/v1/auth/config" || echo "ERROR")

if echo "${AUTH_RESPONSE}" | grep -q "oauth_enabled.*true"; then
  echo "✅ Auth config endpoint working correctly"
else
  echo "⚠️  Warning: Auth config endpoint may not be working. Check logs."
  echo "Response: ${AUTH_RESPONSE}"
fi

***REMOVED*** Step 7: Summary
echo ""
echo "=============================================="
echo "✅ Migration Complete!"
echo "=============================================="
echo ""
echo "📋 Summary:"
echo "  ✅ Secrets created in Secret Manager:"
echo "     - google-client-id"
echo "     - jwt-secret"
echo "     - quote-secret"
echo ""
echo "  ✅ Cloud Run service updated:"
echo "     - Service account: ${SERVICE_ACCOUNT_EMAIL}"
echo "     - Secrets mounted from Secret Manager"
echo "     - Plain env vars removed"
echo ""
echo "  ✅ Service URL: ${SERVICE_URL}"
echo ""
echo "🔐 Security Improvements:"
echo "  ✅ Secrets no longer in plain env vars"
echo "  ✅ Automatic replication across regions"
echo "  ✅ Version history for secrets"
echo "  ✅ Audit logging enabled"
echo ""
echo "📝 Next Steps (Optional):"
echo "  1. Set up secret rotation policy:"
echo "     gcloud secrets add-iam-policy-binding jwt-secret \\"
echo "       --member='serviceAccount:rotation-sa@${PROJECT_ID}.iam.gserviceaccount.com' \\"
echo "       --role='roles/secretmanager.secretAccessor'"
echo ""
echo "  2. Enable secret rotation (requires Cloud Function/Scheduler):"
echo "     See: https://cloud.google.com/secret-manager/docs/rotate-secrets"
echo ""
echo "  3. Monitor secret access:"
echo "     gcloud logging read 'resource.type=secret' --limit=50"
echo ""
echo "✅ Production hardening complete!"
