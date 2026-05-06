***REMOVED***!/bin/bash
***REMOVED*** VERIFY_CACHE_FIX.sh
***REMOVED*** PURPOSE: Verify cache fix is working
***REMOVED*** ENCODING: UTF-8 WITHOUT BOM

SERVICE_URL="${1:-https://soarb2b-274308964876.us-central1.run.app}"

echo "🔍 Verifying cache fix"
echo "======================"
echo ""

***REMOVED*** Test URLs
URLS=(
    "${SERVICE_URL}/ui/tr/soarb2b_onboarding_5q.html"
    "${SERVICE_URL}/ui/en/soarb2b_onboarding_5q.html"
    "${SERVICE_URL}/ui/tr/soarb2b_home.html"
    "${SERVICE_URL}/ui/en/soarb2b_home.html"
)

for url in "${URLS[@]}"; do
    echo "Testing: $url"
    echo "----------------------------------------"
    
    ***REMOVED*** Check headers
    HEADERS=$(curl -I "$url" 2>/dev/null)
    
    ***REMOVED*** Check cache-control
    if echo "$HEADERS" | grep -qi "cache-control:.*no-store.*no-cache"; then
        echo "✅ Cache-Control: OK"
    else
        echo "❌ Cache-Control: MISSING or INCORRECT"
    fi
    
    ***REMOVED*** Check pragma
    if echo "$HEADERS" | grep -qi "pragma:.*no-cache"; then
        echo "✅ Pragma: OK"
    else
        echo "❌ Pragma: MISSING"
    fi
    
    ***REMOVED*** Check expires
    if echo "$HEADERS" | grep -qi "expires:.*0"; then
        echo "✅ Expires: OK"
    else
        echo "❌ Expires: MISSING or INCORRECT"
    fi
    
    ***REMOVED*** Check CF cache status (if behind Cloudflare)
    if echo "$HEADERS" | grep -qi "cf-cache-status"; then
        CF_STATUS=$(echo "$HEADERS" | grep -i "cf-cache-status" | cut -d: -f2 | tr -d ' ')
        if [ "$CF_STATUS" = "BYPASS" ]; then
            echo "✅ CF-Cache-Status: BYPASS"
        else
            echo "⚠️  CF-Cache-Status: $CF_STATUS (should be BYPASS)"
        fi
    else
        echo "ℹ️  CF-Cache-Status: Not present (not behind Cloudflare or not set)"
    fi
    
    echo ""
done

echo "=========================================="
echo "Verification complete"
echo ""
echo "If all checks pass, cache fix is working!"
echo "If CF-Cache-Status is not BYPASS, configure Cloudflare page rules."
