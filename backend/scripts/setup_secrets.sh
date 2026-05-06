***REMOVED***!/bin/bash
***REMOVED*** Setup Google Cloud Secret Manager secrets for SOAR B2B
***REMOVED*** Run this script to create secrets in Secret Manager

set -e

PROJECT_ID="${GOOGLE_CLOUD_PROJECT_ID:-finderos-entegrasyon-480708}"
REGION="${REGION:-us-central1}"

echo "Setting up secrets for project: $PROJECT_ID"
echo "=========================================="

***REMOVED*** Generate secure JWT_SECRET (64 bytes = 86 chars in base64)
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))" 2>/dev/null || \
             openssl rand -base64 64 | tr -d '\n' | head -c 86)

if [ -z "$JWT_SECRET" ]; then
    echo "ERROR: Failed to generate JWT_SECRET"
    exit 1
fi

***REMOVED*** Get GOOGLE_CLIENT_ID from env-vars file or prompt
GOOGLE_CLIENT_ID="${GOOGLE_CLIENT_ID:-274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com}"

if [ -z "$GOOGLE_CLIENT_ID" ]; then
    echo "ERROR: GOOGLE_CLIENT_ID not set"
    exit 1
fi

echo ""
echo "Creating secrets in Secret Manager..."
echo ""

***REMOVED*** Create GOOGLE_CLIENT_ID secret
echo "Creating GOOGLE_CLIENT_ID secret..."
gcloud secrets create GOOGLE_CLIENT_ID \
    --project="$PROJECT_ID" \
    --replication-policy="automatic" \
    2>/dev/null || echo "Secret GOOGLE_CLIENT_ID already exists"

echo -n "$GOOGLE_CLIENT_ID" | gcloud secrets versions add GOOGLE_CLIENT_ID \
    --project="$PROJECT_ID" \
    --data-file=-

***REMOVED*** Create JWT_SECRET secret
echo "Creating JWT_SECRET secret..."
gcloud secrets create JWT_SECRET \
    --project="$PROJECT_ID" \
    --replication-policy="automatic" \
    2>/dev/null || echo "Secret JWT_SECRET already exists"

echo -n "$JWT_SECRET" | gcloud secrets versions add JWT_SECRET \
    --project="$PROJECT_ID" \
    --data-file=-

echo ""
echo "Granting Cloud Run service account access to secrets..."
echo ""

***REMOVED*** Get Cloud Run service account email
SERVICE_ACCOUNT="${CLOUD_RUN_SERVICE_ACCOUNT:-$(gcloud iam service-accounts list --project="$PROJECT_ID" --filter="displayName:Compute Engine default service account" --format="value(email)" 2>/dev/null || echo "")}"

if [ -z "$SERVICE_ACCOUNT" ]; then
    ***REMOVED*** Try to get the default compute service account
    SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"
    echo "Using default service account: $SERVICE_ACCOUNT"
else
    echo "Using service account: $SERVICE_ACCOUNT"
fi

***REMOVED*** Grant Secret Manager Secret Accessor role
gcloud secrets add-iam-policy-binding GOOGLE_CLIENT_ID \
    --project="$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None

gcloud secrets add-iam-policy-binding JWT_SECRET \
    --project="$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None

echo ""
echo "=========================================="
echo "Secrets setup complete!"
echo ""
echo "Created secrets:"
echo "  - GOOGLE_CLIENT_ID: $GOOGLE_CLIENT_ID"
echo "  - JWT_SECRET: [REDACTED - 86 characters]"
echo ""
echo "Service account granted access: $SERVICE_ACCOUNT"
echo ""
echo "Next steps:"
echo "1. Deploy Cloud Run service with GOOGLE_CLOUD_PROJECT_ID env var set"
echo "2. Verify secrets are accessible: gcloud secrets versions access latest --secret=GOOGLE_CLIENT_ID"
echo ""
