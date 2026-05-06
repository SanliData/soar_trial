***REMOVED***!/bin/bash
***REMOVED*** GitHub vs Local Comparison

echo "========================================"
echo "GITHUB vs LOCAL COMPARISON"
echo "========================================"
echo ""

GITHUB_URL="https://raw.githubusercontent.com/SanliData/Finder_os/main/backend/src/ui/en/soarb2b_onboarding_5q.html"
LOCAL_FILE="backend/src/ui/en/soarb2b_onboarding_5q.html"

echo "1️⃣ GITHUB - Result Message Check"
echo "========================================"
curl -s "$GITHUB_URL" 2>/dev/null | grep -A 2 -B 2 "result-subtitle" | grep -v "^--$" | head -10
echo ""

echo "2️⃣ GITHUB - Auto-Start Toggle Check"
echo "========================================"
echo "autoStartQueries occurrences:"
curl -s "$GITHUB_URL" 2>/dev/null | grep -c "autoStartQueries" || echo "0"
echo ""

echo "3️⃣ GITHUB - Critical String Check"
echo "========================================"
echo "Old text (English request):"
curl -s "$GITHUB_URL" 2>/dev/null | grep -c "We have received your English request" || echo "0"
echo "New text (successfully received):"
curl -s "$GITHUB_URL" 2>/dev/null | grep -c "Your request has been successfully received" || echo "0"
echo ""

echo "4️⃣ LOCAL - Critical String Check"
echo "========================================"
if [ -f "$LOCAL_FILE" ]; then
    echo "Old text (English request):"
    grep -c "We have received your English request" "$LOCAL_FILE" || echo "0"
    echo "New text (successfully received):"
    grep -c "Your request has been successfully received" "$LOCAL_FILE" || echo "0"
    echo "autoStartQueries occurrences:"
    grep -c "autoStartQueries" "$LOCAL_FILE" || echo "0"
else
    echo "Local file not found: $LOCAL_FILE"
fi
echo ""

echo "5️⃣ DIFF ANALYSIS"
echo "========================================"
echo "Checking for differences in result screen section..."
echo ""

***REMOVED*** Download GitHub version temporarily
TMP_FILE="/tmp/github_onboarding.html"
curl -s "$GITHUB_URL" > "$TMP_FILE" 2>/dev/null

if [ -f "$LOCAL_FILE" ] && [ -f "$TMP_FILE" ]; then
    echo "Comparing result-subtitle section:"
    echo ""
    echo "--- GITHUB ---"
    grep -A 3 "result-subtitle" "$TMP_FILE" | head -5
    echo ""
    echo "--- LOCAL ---"
    grep -A 3 "result-subtitle" "$LOCAL_FILE" | head -5
    echo ""
    
    echo "Line-by-line diff (result screen section only):"
    diff <(grep -A 10 "resultScreen" "$TMP_FILE") <(grep -A 10 "resultScreen" "$LOCAL_FILE") | head -20
fi

rm -f "$TMP_FILE"

echo ""
echo "========================================"
echo "PRODUCTION CHECK"
echo "========================================"
echo ""

echo "Production (Cloud Run):"
curl -s https://soarb2b-274308964876.us-central1.run.app/ui/en/soarb2b_onboarding_5q.html 2>/dev/null | grep -A 2 "result-subtitle" | head -3
echo ""

echo "Production (Cloudflare):"
curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html 2>/dev/null | grep -A 2 "result-subtitle" | head -3
echo ""
