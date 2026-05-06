***REMOVED***!/bin/bash
***REMOVED*** DIAGNOSE_CACHE_ISSUE.sh
***REMOVED*** PURPOSE: Diagnose cache issue - compare origin vs Cloudflare
***REMOVED*** ENCODING: UTF-8 WITHOUT BOM

echo "🔍 Cache Issue Diagnosis"
echo "========================"
echo ""

***REMOVED*** URLs
CLOUDRUN_URL="https://soarb2b-274308964876.us-central1.run.app"
CLOUDFLARE_URL="https://soarb2b.com"

echo "1️⃣ Testing Origin (Cloud Run - bypasses Cloudflare)"
echo "---------------------------------------------------"
echo ""

echo "Testing: ${CLOUDRUN_URL}/ui/tr/soarb2b_home.html"
echo "Headers:"
curl -I "${CLOUDRUN_URL}/ui/tr/soarb2b_home.html" 2>/dev/null | grep -i "cache-control\|pragma\|expires" || echo "No cache headers"
echo ""

echo "Content check (first 30 lines):"
curl -s "${CLOUDRUN_URL}/ui/tr/soarb2b_home.html" | head -n 30
echo ""

echo "Searching for problematic strings:"
curl -s "${CLOUDRUN_URL}/ui/tr/soarb2b_home.html" | grep -i "ingilizce\|english request" | head -5 || echo "✅ No problematic strings found"
echo ""

echo "2️⃣ Testing Cloudflare (via soarb2b.com)"
echo "----------------------------------------"
echo ""

echo "Testing: ${CLOUDFLARE_URL}/ui/tr/soarb2b_home.html"
echo "Headers:"
curl -I "${CLOUDFLARE_URL}/ui/tr/soarb2b_home.html" 2>/dev/null
echo ""

echo "Key Headers Analysis:"
HEADERS=$(curl -I "${CLOUDFLARE_URL}/ui/tr/soarb2b_home.html" 2>/dev/null)

***REMOVED*** Check CF-Cache-Status
if echo "$HEADERS" | grep -qi "cf-cache-status"; then
    CF_STATUS=$(echo "$HEADERS" | grep -i "cf-cache-status" | cut -d: -f2 | tr -d ' ')
    echo "CF-Cache-Status: $CF_STATUS"
    if [ "$CF_STATUS" = "HIT" ]; then
        echo "  ⚠️  CLOUDFLARE IS CACHING (HIT = cached)"
    elif [ "$CF_STATUS" = "BYPASS" ]; then
        echo "  ✅ Cloudflare bypassing cache"
    elif [ "$CF_STATUS" = "MISS" ]; then
        echo "  ℹ️  Cache miss (not cached yet)"
    fi
else
    echo "CF-Cache-Status: Not present"
fi

***REMOVED*** Check Age header (indicates edge cache)
if echo "$HEADERS" | grep -qi "age:"; then
    AGE=$(echo "$HEADERS" | grep -i "age:" | cut -d: -f2 | tr -d ' ')
    echo "Age: $AGE seconds (edge cache active)"
else
    echo "Age: Not present (no edge cache)"
fi

***REMOVED*** Check Cache-Control from origin
if echo "$HEADERS" | grep -qi "cache-control:"; then
    CACHE_CTRL=$(echo "$HEADERS" | grep -i "cache-control:" | cut -d: -f2 | tr -d ' ')
    echo "Cache-Control: $CACHE_CTRL"
else
    echo "Cache-Control: MISSING (origin not setting it)"
fi

echo ""
echo "Content check (first 30 lines):"
curl -s "${CLOUDFLARE_URL}/ui/tr/soarb2b_home.html" | head -n 30
echo ""

echo "Searching for problematic strings:"
curl -s "${CLOUDFLARE_URL}/ui/tr/soarb2b_home.html" | grep -i "ingilizce\|english request" | head -5 || echo "✅ No problematic strings found"
echo ""

echo "3️⃣ Diagnosis Summary"
echo "--------------------"
echo ""

***REMOVED*** Compare content
ORIGIN_CONTENT=$(curl -s "${CLOUDRUN_URL}/ui/tr/soarb2b_home.html" | head -n 50 | md5sum 2>/dev/null || echo "unknown")
CF_CONTENT=$(curl -s "${CLOUDFLARE_URL}/ui/tr/soarb2b_home.html" | head -n 50 | md5sum 2>/dev/null || echo "unknown")

if [ "$ORIGIN_CONTENT" = "$CF_CONTENT" ]; then
    echo "✅ Origin and Cloudflare content MATCH"
    echo "   → Issue is likely browser/service worker cache"
else
    echo "❌ Origin and Cloudflare content DIFFER"
    echo "   → Issue is Cloudflare edge cache"
    echo "   → Solution: Create Cache Rules + Purge"
fi

echo ""
echo "=========================================="
echo "Next Steps:"
echo "1. If CF-Cache-Status: HIT → Create Cache Rules"
echo "2. Purge Cloudflare cache"
echo "3. Check browser/service worker cache"
echo "=========================================="
