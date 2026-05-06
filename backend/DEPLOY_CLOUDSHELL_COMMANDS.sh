***REMOVED***!/bin/bash
***REMOVED*** DEPLOY_CLOUDSHELL_COMMANDS.sh
***REMOVED*** PURPOSE: Commands to find and deploy backend from Cloud Shell
***REMOVED*** ENCODING: UTF-8 WITHOUT BOM

echo "🔍 Finding backend directory..."
echo ""

***REMOVED*** Find backend directory
BACKEND_DIR=$(find ~ -name "backend" -type d 2>/dev/null | grep -i finder | head -1)

if [ -z "$BACKEND_DIR" ]; then
    echo "❌ Backend directory not found!"
    echo ""
    echo "Please check:"
    echo "  pwd"
    echo "  ls -la"
    echo "  find ~ -name 'backend' -type d"
    exit 1
fi

echo "✅ Found backend: $BACKEND_DIR"
echo ""

***REMOVED*** Get parent directory (project root)
PROJECT_ROOT=$(dirname "$BACKEND_DIR")
echo "📁 Project root: $PROJECT_ROOT"
echo ""

***REMOVED*** Navigate to project root
cd "$PROJECT_ROOT"

echo "🚀 Deploying from: $(pwd)"
echo ""

***REMOVED*** Deploy
gcloud run deploy soarb2b \
  --source backend \
  --region us-central1 \
  --project finderos-entegrasyon-480708 \
  --service-account soarb2b@finderos-entegrasyon-480708.iam.gserviceaccount.com \
  --set-secrets="GOOGLE_CLIENT_ID=google-client-id:latest,JWT_SECRET=jwt-secret:latest,QUOTE_SECRET=quote-secret:latest" \
  --allow-unauthenticated

echo ""
echo "✅ Deployment complete!"
