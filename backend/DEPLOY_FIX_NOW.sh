***REMOVED***!/bin/bash
***REMOVED*** IMMEDIATE FIX: Deploy SOAR B2B with OAuth working
***REMOVED*** Run this script to fix the 503 error

set -e

PROJECT_ID="finderos-entegrasyon-480708"
REGION="us-central1"
SERVICE_NAME="soarb2b"
SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"

echo "=========================================="
echo "SOAR B2B OAuth 503 Fix"
echo "=========================================="
echo ""

***REMOVED*** Step 1: Create secrets in Secret Manager
echo "Step 1: Creating secrets in Secret Manager..."
echo ""

***REMOVED*** Generate secure JWT_SECRET
if command -v python3 &> /dev/null; then
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
else
    echo "ERROR: python3 not found. Install Python 3 to generate secure JWT_SECRET."
    exit 1
fi

GOOGLE_CLIENT_ID="274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com"

***REMOVED*** Create GOOGLE_CLIENT_ID secret
echo "Creating GOOGLE_CLIENT_ID secret..."
if gcloud secrets describe GOOGLE_CLIENT_ID --project="$PROJECT_ID" &>/dev/null; then
    echo "  Secret already exists, adding new version..."
    echo -n "$GOOGLE_CLIENT_ID" | gcloud secrets versions add GOOGLE_CLIENT_ID \
        --project="$PROJECT_ID" \
        --data-file=-
else
    echo -n "$GOOGLE_CLIENT_ID" | gcloud secrets create GOOGLE_CLIENT_ID \
        --project="$PROJECT_ID" \
        --replication-policy="automatic" \
        --data-file=-
    echo "  ✓ Created"
fi

***REMOVED*** Create JWT_SECRET secret
echo "Creating JWT_SECRET secret..."
if gcloud secrets describe JWT_SECRET --project="$PROJECT_ID" &>/dev/null; then
    echo "  Secret already exists, adding new version..."
    echo -n "$JWT_SECRET" | gcloud secrets versions add JWT_SECRET \
        --project="$PROJECT_ID" \
        --data-file=-
else
    echo -n "$JWT_SECRET" | gcloud secrets create JWT_SECRET \
        --project="$PROJECT_ID" \
        --replication-policy="automatic" \
        --data-file=-
    echo "  ✓ Created"
fi

echo ""

***REMOVED*** Step 2: Grant service account access
echo "Step 2: Granting service account access..."
gcloud secrets add-iam-policy-binding GOOGLE_CLIENT_ID \
    --project="$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" \
    --quiet 2>/dev/null || echo "  ✓ Access already granted"

gcloud secrets add-iam-policy-binding JWT_SECRET \
    --project="$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" \
    --quiet 2>/dev/null || echo "  ✓ Access already granted"

echo ""

***REMOVED*** Step 3: Determine env-vars file path
echo "Step 3: Deploying service..."
ENV_FILE="backend/env-vars-cloudrun.yaml"

if [ ! -f "$ENV_FILE" ]; then
    ***REMOVED*** Try alternative path
    if [ -f "/home/isanli058/env-vars.yaml" ]; then
        ENV_FILE="/home/isanli058/env-vars.yaml"
        echo "  Using env file: $ENV_FILE"
    else
        echo "  WARNING: env-vars file not found, using inline env vars"
        ENV_FILE=""
    fi
else
    echo "  Using env file: $ENV_FILE"
fi

***REMOVED*** Step 4: Deploy
if [ -n "$ENV_FILE" ] && [ -f "$ENV_FILE" ]; then
    gcloud run deploy "$SERVICE_NAME" \
        --source backend \
        --region "$REGION" \
        --allow-unauthenticated \
        --env-vars-file "$ENV_FILE" \
        --service-account "$SERVICE_ACCOUNT" \
        --project "$PROJECT_ID"
else
    ***REMOVED*** Fallback: use inline env vars
    echo "  Deploying with inline environment variables..."
    gcloud run deploy "$SERVICE_NAME" \
        --source backend \
        --region "$REGION" \
        --allow-unauthenticated \
        --set-env-vars "ENV=production,GOOGLE_CLOUD_PROJECT_ID=${PROJECT_ID},GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID},JWT_SECRET=${JWT_SECRET}" \
        --service-account "$SERVICE_ACCOUNT" \
        --project "$PROJECT_ID"
fi

echo ""
echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
echo ""

***REMOVED*** Step 5: Verify
echo "Step 4: Verifying deployment..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(status.url)" 2>/dev/null)

if [ -n "$SERVICE_URL" ]; then
    echo "Service URL: $SERVICE_URL"
    echo ""
    echo "Testing /v1/auth/config endpoint:"
    echo "-----------------------------------"
    
    RESPONSE=$(curl -s "$SERVICE_URL/v1/auth/config")
    
    if command -v jq &> /dev/null; then
        echo "$RESPONSE" | jq
    else
        echo "$RESPONSE"
    fi
    
    echo ""
    
    ***REMOVED*** Check if oauth_enabled is true
    if echo "$RESPONSE" | grep -q '"oauth_enabled":\s*true'; then
        echo "✓ SUCCESS: OAuth is enabled!"
    elif echo "$RESPONSE" | grep -q '"oauth_enabled":\s*false'; then
        echo "✗ WARNING: OAuth is still disabled. Check Cloud Run logs."
        echo ""
        echo "Check logs with:"
        echo "  gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}\" --limit=20 --project=${PROJECT_ID}"
    else
        echo "✗ ERROR: Unexpected response. Check the output above."
    fi
else
    echo "Could not determine service URL"
fi

echo ""
echo "=========================================="
echo "Fix complete!"
echo "=========================================="
