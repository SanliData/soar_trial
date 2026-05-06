***REMOVED***!/bin/bash
***REMOVED*** Update Production API Keys on Google Cloud Run
***REMOVED*** Bash script for Cloud Shell

set -e

echo ""
echo "================================================================"
echo "SOAR B2B - Production API Keys Update (Cloud Shell)"
echo "================================================================"
echo ""

***REMOVED*** Yeni API key'ler (bu script'i çalıştırmadan önce güncelleyin)
API_KEYS="<REDACTED_SOARB2B_API_KEY>,V7YqHkC3VtFdaQ1CoukebzqkI0B22RaL7yMw9ODcLDg,-CTkzDe8fFkGqnomj-tUw8F4FHK8hRhBxDP64LL-bFk"

REGION="us-central1"
SERVICE_NAME="soarb2b"
CORS_ORIGINS="https://soarb2b.com,https://www.soarb2b.com"

echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""
echo "Updating API keys..."
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
    echo "Yeni API Key'ler:"
    IFS=',' read -ra KEYS <<< "$API_KEYS"
    for i in "${!KEYS[@]}"; do
        echo "  Key $((i+1)): ${KEYS[i]}"
    done
    echo ""
    echo "⚠️  ÖNEMLİ: Bu key'leri GÜVENLİ bir yerde saklayın!"
    echo "⚠️  GitHub'a ASLA commit etmeyin!"
    echo ""
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format "value(status.url)" 2>/dev/null)
    if [ -n "$SERVICE_URL" ]; then
        echo "Test için:"
        echo "  curl -H \"X-API-Key: ${KEYS[0]}\" $SERVICE_URL/api/v1/b2b/demo/hotels"
    fi
else
    echo ""
    echo "================================================================"
    echo "❌ GÜNCELLEME BAŞARISIZ!"
    echo "================================================================"
    exit 1
fi

echo ""
