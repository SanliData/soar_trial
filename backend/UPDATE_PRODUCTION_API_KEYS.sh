***REMOVED***!/bin/bash
***REMOVED*** Update Production API Keys on Google Cloud Run
***REMOVED*** Bash script for Cloud Shell

set -e

echo ""
echo "================================================================"
echo "SOAR B2B - Production API Keys Update (Cloud Shell)"
echo "================================================================"
echo ""

***REMOVED*** Set SOARB2B_API_KEYS via Secret Manager / secure channel (do not hardcode here)
API_KEYS="${SOARB2B_API_KEYS:-}"

REGION="us-central1"
SERVICE_NAME="soarb2b"
CORS_ORIGINS="https://soarb2b.com,https://www.soarb2b.com"

echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""
if [ -z "$API_KEYS" ]; then
  echo "ERROR: SOARB2B_API_KEYS is not set. Refusing to proceed."
  exit 2
fi

echo "Updating API keys (value not echoed)..."
echo ""

***REMOVED*** Update env vars - set-env-vars kullan (tüm env vars'ı set eder)
gcloud run services update "$SERVICE_NAME" \
  --region "$REGION" \
  --set-env-vars "SOARB2B_API_KEYS=$API_KEYS,FINDEROS_CORS_ORIGINS=$CORS_ORIGINS,ENV=production"

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================"
    echo "✅ API KEYS BAŞARIYLA GÜNCELLENDİ!"
    echo "================================================================"
    echo ""
    echo "✅ Updated. (Keys are not printed.)"
    echo ""
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format "value(status.url)" 2>/dev/null)
    if [ -n "$SERVICE_URL" ]; then
        echo "Test için:"
        echo "  curl -H \"X-API-Key: <YOUR_KEY>\" $SERVICE_URL/api/v1/b2b/demo/hotels"
    fi
else
    echo ""
    echo "================================================================"
    echo "❌ GÜNCELLEME BAŞARISIZ!"
    echo "================================================================"
    exit 1
fi

echo ""
