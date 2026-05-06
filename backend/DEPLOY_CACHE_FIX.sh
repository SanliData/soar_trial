***REMOVED***!/bin/bash
***REMOVED*** DEPLOY_CACHE_FIX.sh
***REMOVED*** PURPOSE: Deploy cache fix to Cloud Run
***REMOVED*** ENCODING: UTF-8 WITHOUT BOM

set -e

PROJECT_ID="finderos-entegrasyon-480708"
REGION="us-central1"
SERVICE_NAME="soarb2b"
SERVICE_ACCOUNT="soarb2b@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🚀 Deploying cache fix to Cloud Run"
echo "===================================="
echo ""

***REMOVED*** Deploy with no-cache to force rebuild
echo "📦 Building and deploying..."
gcloud run deploy "$SERVICE_NAME" \
  --source backend \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --service-account "$SERVICE_ACCOUNT" \
  --set-secrets="GOOGLE_CLIENT_ID=google-client-id:latest,JWT_SECRET=jwt-secret:latest,QUOTE_SECRET=quote-secret:latest" \
  --allow-unauthenticated \
  --no-cache

echo ""
echo "✅ Deployment complete!"
echo ""

***REMOVED*** Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format="value(status.url)" 2>/dev/null)

if [ -n "$SERVICE_URL" ]; then
    echo "🔍 Verifying cache headers..."
    echo ""
    
    ***REMOVED*** Check headers
    echo "Testing: ${SERVICE_URL}/ui/tr/soarb2b_onboarding_5q.html"
    curl -I "${SERVICE_URL}/ui/tr/soarb2b_onboarding_5q.html" 2>/dev/null | grep -i "cache-control\|pragma\|expires\|cf-cache-status" || echo "Headers not found"
    
    echo ""
    echo "✅ Verification complete"
    echo ""
    echo "⚠️  NEXT STEPS:"
    echo "1. Configure Cloudflare page rules (see CLOUDFLARE_PAGE_RULES.md)"
    echo "2. Disable Rocket Loader in Cloudflare dashboard"
    echo "3. Disable HTML minification in Cloudflare dashboard"
    echo "4. Purge Cloudflare cache"
fi
