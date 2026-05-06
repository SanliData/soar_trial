***REMOVED***!/bin/bash
***REMOVED*** Find UPAP Upload Endpoint

echo "========================================"
echo "SEARCHING FOR UPAP ENDPOINT"
echo "========================================"
echo ""

echo "1️⃣ Search for 'upap' in all files:"
grep -r "upap\|UPAP" backend/src 2>/dev/null | head -10
echo ""

echo "2️⃣ Search for '/upload' endpoints:"
grep -r "/upload\|@router.*upload" backend/src/http 2>/dev/null | head -10
echo ""

echo "3️⃣ List all router files:"
find backend/src/http/v1 -name "*router*.py" -type f | sort
echo ""

echo "4️⃣ Search for 'upload' in router files:"
grep -r "upload" backend/src/http/v1/*router*.py 2>/dev/null | grep -i "def\|@router\|path\|endpoint" | head -10
echo ""

echo "5️⃣ Check router registry for all registered routers:"
grep -r "include_router\|router.*=" backend/src/app.py | grep -v "^***REMOVED***" | head -20
echo ""

echo "6️⃣ Search for 'User not found' error message:"
grep -r "User not found" backend/src --include="*.py" | head -5
echo ""

echo "========================================"
echo "CHECKING AUTHENTICATION DEPENDENCIES"
echo "========================================"
echo ""

echo "7️⃣ Find endpoints using get_current_user_dependency:"
grep -r "get_current_user_dependency\|get_current_user" backend/src/http/v1 --include="*.py" | head -10
echo ""
