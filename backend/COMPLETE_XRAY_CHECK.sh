***REMOVED***!/bin/bash
***REMOVED*** Complete X-Ray: Local vs GitHub vs Production

echo "========================================"
echo "COMPLETE X-RAY - en/soarb2b_onboarding_5q.html"
echo "========================================"
echo ""

GITHUB_URL="https://raw.githubusercontent.com/SanliData/Finder_os/main/backend/src/ui/en/soarb2b_onboarding_5q.html"
LOCAL_FILE="backend/src/ui/en/soarb2b_onboarding_5q.html"

echo "1️⃣ LOCAL FILE (if exists in Cloud Shell)"
echo "========================================"
if [ -f "$LOCAL_FILE" ]; then
    echo "Old text (English request):"
    grep -c "We have received your English request" "$LOCAL_FILE" || echo "0"
    echo "New text (successfully received):"
    grep -c "Your request has been successfully received" "$LOCAL_FILE" || echo "0"
    echo "autoStartQueries count:"
    grep -c "autoStartQueries" "$LOCAL_FILE" || echo "0"
    echo ""
    echo "Result subtitle line:"
    grep "result-subtitle" "$LOCAL_FILE" | head -1
else
    echo "Local file not found in Cloud Shell"
fi
echo ""

echo "2️⃣ GITHUB (main branch)"
echo "========================================"
echo "Checking: $GITHUB_URL"
echo ""

***REMOVED*** Download to temp file for analysis
TMP_GITHUB="/tmp/github_file.html"
curl -s "$GITHUB_URL" > "$TMP_GITHUB" 2>/dev/null

if [ -f "$TMP_GITHUB" ] && [ -s "$TMP_GITHUB" ]; then
    echo "Old text (English request):"
    grep -c "We have received your English request" "$TMP_GITHUB" || echo "0"
    echo "New text (successfully received):"
    grep -c "Your request has been successfully received" "$TMP_GITHUB" || echo "0"
    echo "autoStartQueries count:"
    grep -c "autoStartQueries" "$TMP_GITHUB" || echo "0"
    echo ""
    echo "Result subtitle line:"
    grep "result-subtitle" "$TMP_GITHUB" | head -1
else
    echo "❌ ERROR: Could not fetch GitHub file"
    echo "URL: $GITHUB_URL"
fi
echo ""

echo "3️⃣ PRODUCTION - Cloud Run (Direct)"
echo "========================================"
TMP_PROD="/tmp/prod_cloudrun.html"
curl -s https://soarb2b-274308964876.us-central1.run.app/ui/en/soarb2b_onboarding_5q.html > "$TMP_PROD" 2>/dev/null

if [ -f "$TMP_PROD" ] && [ -s "$TMP_PROD" ]; then
    echo "Old text (English request):"
    grep -c "We have received your English request" "$TMP_PROD" || echo "0"
    echo "New text (successfully received):"
    grep -c "Your request has been successfully received" "$TMP_PROD" || echo "0"
    echo "autoStartQueries count:"
    grep -c "autoStartQueries" "$TMP_PROD" || echo "0"
    echo ""
    echo "Result subtitle line:"
    grep "result-subtitle" "$TMP_PROD" | head -1
else
    echo "❌ ERROR: Could not fetch Cloud Run file"
fi
echo ""

echo "4️⃣ PRODUCTION - Cloudflare"
echo "========================================"
TMP_CF="/tmp/prod_cloudflare.html"
curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html > "$TMP_CF" 2>/dev/null

if [ -f "$TMP_CF" ] && [ -s "$TMP_CF" ]; then
    echo "Old text (English request):"
    grep -c "We have received your English request" "$TMP_CF" || echo "0"
    echo "New text (successfully received):"
    grep -c "Your request has been successfully received" "$TMP_CF" || echo "0"
    echo "autoStartQueries count:"
    grep -c "autoStartQueries" "$TMP_CF" || echo "0"
    echo ""
    echo "Result subtitle line:"
    grep "result-subtitle" "$TMP_CF" | head -1
else
    echo "❌ ERROR: Could not fetch Cloudflare file"
fi
echo ""

echo "5️⃣ DIFF: GitHub vs Production (Cloud Run)"
echo "========================================"
if [ -f "$TMP_GITHUB" ] && [ -f "$TMP_PROD" ]; then
    echo "Differences in result-subtitle section:"
    diff <(grep -A 3 "result-subtitle" "$TMP_GITHUB") <(grep -A 3 "result-subtitle" "$TMP_PROD") || echo "No differences (or both have same content)"
fi
echo ""

echo "6️⃣ SUMMARY TABLE"
echo "========================================"
printf "%-25s | %-5s | %-5s | %-5s\n" "Source" "Old" "New" "Toggle"
echo "----------------------------------------|-------|-------|-------"

if [ -f "$TMP_GITHUB" ]; then
    OLD_GITHUB=$(grep -c "We have received your English request" "$TMP_GITHUB" || echo "0")
    NEW_GITHUB=$(grep -c "Your request has been successfully received" "$TMP_GITHUB" || echo "0")
    TOGGLE_GITHUB=$(grep -c "autoStartQueries" "$TMP_GITHUB" || echo "0")
    printf "%-25s | %-5s | %-5s | %-5s\n" "GitHub" "$OLD_GITHUB" "$NEW_GITHUB" "$TOGGLE_GITHUB"
fi

if [ -f "$TMP_PROD" ]; then
    OLD_PROD=$(grep -c "We have received your English request" "$TMP_PROD" || echo "0")
    NEW_PROD=$(grep -c "Your request has been successfully received" "$TMP_PROD" || echo "0")
    TOGGLE_PROD=$(grep -c "autoStartQueries" "$TMP_PROD" || echo "0")
    printf "%-25s | %-5s | %-5s | %-5s\n" "Production (Cloud Run)" "$OLD_PROD" "$NEW_PROD" "$TOGGLE_PROD"
fi

if [ -f "$TMP_CF" ]; then
    OLD_CF=$(grep -c "We have received your English request" "$TMP_CF" || echo "0")
    NEW_CF=$(grep -c "Your request has been successfully received" "$TMP_CF" || echo "0")
    TOGGLE_CF=$(grep -c "autoStartQueries" "$TMP_CF" || echo "0")
    printf "%-25s | %-5s | %-5s | %-5s\n" "Production (Cloudflare)" "$OLD_CF" "$NEW_CF" "$TOGGLE_CF"
fi

echo ""

***REMOVED*** Cleanup
rm -f "$TMP_GITHUB" "$TMP_PROD" "$TMP_CF"

echo "========================================"
echo "ANALYSIS COMPLETE"
echo "========================================"
