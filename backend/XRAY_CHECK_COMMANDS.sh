***REMOVED***!/bin/bash
***REMOVED*** X-Ray Check: Local vs GitHub vs Production

echo "========================================"
echo "X-RAY COMPARISON - en/soarb2b_onboarding_5q.html"
echo "========================================"
echo ""

echo "1️⃣ LOCAL CHECK (Windows)"
echo "Run in PowerShell:"
echo 'Select-String -Path "backend\src\ui\en\soarb2b_onboarding_5q.html" -Pattern "English request|successfully received"'
echo ""

echo "2️⃣ GITHUB CHECK"
echo "curl -s https://raw.githubusercontent.com/SanliData/Finder_os/main/backend/src/ui/en/soarb2b_onboarding_5q.html | grep -n \"English request\\|successfully received\""
echo ""
curl -s https://raw.githubusercontent.com/SanliData/Finder_os/main/backend/src/ui/en/soarb2b_onboarding_5q.html 2>/dev/null | grep -n "English request\|successfully received" | head -5
echo ""

echo "3️⃣ PRODUCTION CHECK (Cloud Run - Direct)"
echo "curl -s https://soarb2b-274308964876.us-central1.run.app/ui/en/soarb2b_onboarding_5q.html | grep -n \"English request\\|successfully received\""
echo ""
curl -s https://soarb2b-274308964876.us-central1.run.app/ui/en/soarb2b_onboarding_5q.html 2>/dev/null | grep -n "English request\|successfully received" | head -5
echo ""

echo "4️⃣ PRODUCTION CHECK (Cloudflare)"
echo "curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html | grep -n \"English request\\|successfully received\""
echo ""
curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html 2>/dev/null | grep -n "English request\|successfully received" | head -5
echo ""

echo "========================================"
echo "AUTO-START TOGGLE CHECK"
echo "========================================"
echo ""

echo "GitHub autoStartQueries count:"
curl -s https://raw.githubusercontent.com/SanliData/Finder_os/main/backend/src/ui/en/soarb2b_onboarding_5q.html 2>/dev/null | grep -c "autoStartQueries" || echo "0"
echo ""

echo "Production (Cloud Run) autoStartQueries count:"
curl -s https://soarb2b-274308964876.us-central1.run.app/ui/en/soarb2b_onboarding_5q.html 2>/dev/null | grep -c "autoStartQueries" || echo "0"
echo ""

echo "Production (Cloudflare) autoStartQueries count:"
curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html 2>/dev/null | grep -c "autoStartQueries" || echo "0"
echo ""

echo "========================================"
echo "CACHE HEADERS CHECK"
echo "========================================"
echo ""

echo "Cloud Run headers:"
curl -I https://soarb2b-274308964876.us-central1.run.app/ui/en/soarb2b_onboarding_5q.html 2>/dev/null | grep -i "cache-control\|pragma\|expires\|cf-cache-status" | head -5
echo ""

echo "Cloudflare headers:"
curl -I https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html 2>/dev/null | grep -i "cache-control\|pragma\|expires\|cf-cache-status" | head -5
echo ""
