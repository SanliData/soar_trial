***REMOVED***!/bin/bash
***REMOVED*** Deploy SOAR B2B to Cloud Run with Secret Manager integration
***REMOVED*** This script deploys the service with proper environment variables

set -e

PROJECT_ID="${GOOGLE_CLOUD_PROJECT_ID:-finderos-entegrasyon-480708}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="soarb2b"

echo "Deploying $SERVICE_NAME to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

***REMOVED*** Verify secrets exist
echo "Verifying secrets in Secret Manager..."
if ! gcloud secrets describe GOOGLE_CLIENT_ID --project="$PROJECT_ID" &>/dev/null; then
    echo "ERROR: GOOGLE_CLIENT_ID secret not found in Secret Manager"
    echo "Run: ./scripts/setup_secrets.sh"
    exit 1
fi

if ! gcloud secrets describe JWT_SECRET --project="$PROJECT_ID" &>/dev/null; then
    echo "ERROR: JWT_SECRET secret not found in Secret Manager"
    echo "Run: ./scripts/setup_secrets.sh"
    exit 1
fi

echo "✓ Secrets verified"
echo ""

***REMOVED*** Get service account
SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"

***REMOVED*** Deploy
echo "Deploying service..."
gcloud run deploy "$SERVICE_NAME" \
    --source backend \
    --region "$REGION" \
    --allow-unauthenticated \
    --env-vars-file backend/env-vars-cloudrun.yaml \
    --service-account "$SERVICE_ACCOUNT" \
    --project "$PROJECT_ID"

echo ""
echo "Deployment complete!"
echo ""
echo "Testing /v1/auth/config endpoint..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="value(status.url)")

if [ -n "$SERVICE_URL" ]; then
    echo "Service URL: $SERVICE_URL"
    echo ""
    curl -s "$SERVICE_URL/v1/auth/config" | python3 -m json.tool || echo "Failed to get response"
else
    echo "Could not determine service URL"
fi
