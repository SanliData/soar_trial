***REMOVED***!/bin/bash
***REMOVED*** VERIFY_CACHE_HEADERS.sh
***REMOVED*** PURPOSE: Verify cache headers after deploy
***REMOVED*** ENCODING: UTF-8 WITHOUT BOM

URL="https://soarb2b-274308964876.us-central1.run.app/ui/tr/soarb2b_home.html"

echo "🔍 Checking cache headers..."
echo "URL: ${URL}"
echo ""

***REMOVED*** Get headers
HEADERS=$(curl -I "${URL}" 2>/dev/null)

echo "📋 Response Headers:"
echo "==================="
echo "${HEADERS}"
echo ""

***REMOVED*** Check for cache headers
echo "✅ Expected Headers Check:"
echo "=========================="

if echo "${HEADERS}" | grep -qi "cache-control.*no-store"; then
    echo "✅ Cache-Control: PRESENT"
else
    echo "❌ Cache-Control: MISSING"
fi

if echo "${HEADERS}" | grep -qi "pragma.*no-cache"; then
    echo "✅ Pragma: PRESENT"
else
    echo "❌ Pragma: MISSING"
fi

if echo "${HEADERS}" | grep -qi "expires.*0"; then
    echo "✅ Expires: PRESENT"
else
    echo "❌ Expires: MISSING"
fi

if echo "${HEADERS}" | grep -qi "cdn-cache-control"; then
    echo "✅ CDN-Cache-Control: PRESENT"
else
    echo "❌ CDN-Cache-Control: MISSING"
fi

echo ""
echo "❌ Should NOT have:"

if echo "${HEADERS}" | grep -qi "etag"; then
    echo "❌ ETag: STILL PRESENT (should be removed)"
else
    echo "✅ ETag: REMOVED"
fi

if echo "${HEADERS}" | grep -qi "last-modified"; then
    echo "❌ Last-Modified: STILL PRESENT (should be removed)"
else
    echo "✅ Last-Modified: REMOVED"
fi

echo ""
echo "=========================================="
