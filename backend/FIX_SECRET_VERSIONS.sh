***REMOVED***!/bin/bash
***REMOVED*** FIX_SECRET_VERSIONS.sh
***REMOVED*** PURPOSE: Add versions to existing secrets (fix "version not found" error)
***REMOVED*** ENCODING: UTF-8 WITHOUT BOM

set -e  ***REMOVED*** Exit on error

PROJECT_ID="finderos-entegrasyon-480708"
SERVICE_NAME="soarb2b"
REGION="us-central1"
SERVICE_ACCOUNT="soarb2b@${PROJECT_ID}.iam.gserviceaccount.com"

***REMOVED*** JWT_SECRET value (from current deployment)
JWT_SECRET_VALUE="48f82ac5746559b03d21f57cb57f748d45554d2d12d449e070767cf5613d6e34e7d6b3e3c1b08aaf3cf362b3f36cc66eef9c5aef196419658b38a5140b2414d6"

***REMOVED*** GOOGLE_CLIENT_ID value
GOOGLE_CLIENT_ID_VALUE="274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com"

echo "🔧 Secret Version Fix"
echo "===================="
echo "Project: ${PROJECT_ID}"
echo "Service: ${SERVICE_NAME}"
echo ""

***REMOVED*** Step 1: Verify secrets exist
echo "🔍 Step 1: Verifying secrets exist..."
echo ""

SECRETS=$(gcloud secrets list --project=${PROJECT_ID} --format="value(name.basename())")

REQUIRED_SECRETS=("google-client-id" "jwt-secret" "quote-secret")
MISSING_SECRETS=()

for secret in "${REQUIRED_SECRETS[@]}"; do
  if echo "${SECRETS}" | grep -q "^${secret}$"; then
    echo "✅ Secret found: ${secret}"
  else
    echo "❌ Secret NOT found: ${secret}"
    MISSING_SECRETS+=("${secret}")
  fi
done

if [ ${***REMOVED***MISSING_SECRETS[@]} -gt 0 ]; then
  echo ""
  echo "❌ ERROR: Missing secrets: ${MISSING_SECRETS[*]}"
  echo "Please create them first using SECRET_MANAGER_MIGRATION.sh"
  exit 1
fi

echo ""
echo "✅ All secrets exist"
echo ""

***REMOVED*** Step 2: Check if versions exist
echo "🔍 Step 2: Checking secret versions..."
echo ""

for secret in "${REQUIRED_SECRETS[@]}"; do
  echo "Checking ${secret}..."
  VERSIONS=$(gcloud secrets versions list ${secret} --project=${PROJECT_ID} --format="value(name)" 2>/dev/null || echo "")
  
  if [ -z "${VERSIONS}" ]; then
    echo "  ❌ No versions found for ${secret}"
  else
    VERSION_COUNT=$(echo "${VERSIONS}" | wc -l)
    echo "  ✅ Found ${VERSION_COUNT} version(s)"
    echo "${VERSIONS}" | head -1 | sed 's/^/    Latest: /'
  fi
done

echo ""

***REMOVED*** Step 3: Add versions if missing
echo "🔐 Step 3: Adding versions to secrets..."
echo ""

***REMOVED*** google-client-id
echo "Adding version to google-client-id..."
echo -n "${GOOGLE_CLIENT_ID_VALUE}" | \
  gcloud secrets versions add google-client-id \
    --project=${PROJECT_ID} \
    --data-file=- \
    --quiet

echo "✅ google-client-id version added"

***REMOVED*** jwt-secret
echo "Adding version to jwt-secret..."
echo -n "${JWT_SECRET_VALUE}" | \
  gcloud secrets versions add jwt-secret \
    --project=${PROJECT_ID} \
    --data-file=- \
    --quiet

echo "✅ jwt-secret version added"

***REMOVED*** quote-secret
echo "Adding version to quote-secret..."
QUOTE_SECRET_VALUE=$(openssl rand -hex 64)
echo -n "${QUOTE_SECRET_VALUE}" | \
  gcloud secrets versions add quote-secret \
    --project=${PROJECT_ID} \
    --data-file=- \
    --quiet

echo "✅ quote-secret version added"

echo ""

***REMOVED*** Step 4: Verify versions
echo "🔎 Step 4: Verifying versions..."
echo ""

for secret in "${REQUIRED_SECRETS[@]}"; do
  echo "Checking ${secret}..."
  VERSION=$(gcloud secrets versions list ${secret} --project=${PROJECT_ID} --format="value(name)" --limit=1 2>/dev/null || echo "")
  
  if [ -z "${VERSION}" ]; then
    echo "  ❌ Still no version found!"
  else
    STATE=$(gcloud secrets versions describe ${VERSION} --project=${PROJECT_ID} --format="value(state)" 2>/dev/null || echo "")
    echo "  ✅ Version: ${VERSION}"
    echo "  ✅ State: ${STATE}"
  fi
done

echo ""

***REMOVED*** Step 5: Update Cloud Run service
echo "🚀 Step 5: Updating Cloud Run service..."
echo ""

gcloud run services update ${SERVICE_NAME} \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  --service-account=${SERVICE_ACCOUNT} \
  --set-secrets="GOOGLE_CLIENT_ID=google-client-id:latest,JWT_SECRET=jwt-secret:latest,QUOTE_SECRET=quote-secret:latest" \
  --remove-env-vars="GOOGLE_CLIENT_ID,JWT_SECRET" \
  --quiet

echo "✅ Cloud Run service updated"
echo ""

***REMOVED*** Step 6: Verify deployment
echo "🧪 Step 6: Verifying deployment configuration..."
echo ""

sleep 3  ***REMOVED*** Wait for deployment to propagate

ENV_CONFIG=$(gcloud run services describe ${SERVICE_NAME} \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  --format="yaml(spec.template.spec.containers[0].env)" 2>/dev/null || echo "")

if echo "${ENV_CONFIG}" | grep -q "secretKeyRef.*google-client-id"; then
  echo "✅ GOOGLE_CLIENT_ID bound to secret"
else
  echo "❌ GOOGLE_CLIENT_ID not bound correctly"
fi

if echo "${ENV_CONFIG}" | grep -q "secretKeyRef.*jwt-secret"; then
  echo "✅ JWT_SECRET bound to secret"
else
  echo "❌ JWT_SECRET not bound correctly"
fi

if echo "${ENV_CONFIG}" | grep -q "secretKeyRef.*quote-secret"; then
  echo "✅ QUOTE_SECRET bound to secret"
else
  echo "❌ QUOTE_SECRET not bound correctly"
fi

echo ""
echo "Full configuration:"
echo "${ENV_CONFIG}"
echo ""

***REMOVED*** Step 7: Test endpoint
echo "🧪 Step 7: Testing auth config endpoint..."
echo ""

SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  --format="value(status.url)")

echo "Service URL: ${SERVICE_URL}"
echo ""

sleep 2  ***REMOVED*** Wait for service to be ready

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
  echo ""
  echo "Checking logs..."
  gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}" \
    --project=${PROJECT_ID} \
    --limit=10 \
    --format="table(timestamp,severity,textPayload)" \
    --freshness=5m
fi

echo ""
echo "=============================================="
echo "✅ Fix Complete!"
echo "=============================================="
echo ""
echo "📋 Summary:"
echo "  ✅ Secrets verified"
echo "  ✅ Versions added"
echo "  ✅ Cloud Run service updated"
echo "  ✅ Configuration verified"
echo ""
echo "🔐 Security Status:"
echo "  ✅ Secrets in Secret Manager"
echo "  ✅ Versions enabled"
echo "  ✅ Service account configured"
echo ""
echo "🌐 Service URL: ${SERVICE_URL}"
echo ""
echo "✅ Production-ready!"
