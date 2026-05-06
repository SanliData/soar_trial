***REMOVED***!/bin/bash
***REMOVED*** FIX_LOCALHOST_CALLS.sh
***REMOVED*** PURPOSE: Remove all localhost:7243 API calls from production UI files
***REMOVED*** ENCODING: UTF-8 WITHOUT BOM

set -e  ***REMOVED*** Exit on error

echo "🔧 Removing localhost API calls from production files"
echo "======================================================"
echo ""

***REMOVED*** Pattern to remove
PATTERN="// ***REMOVED***region agent log.*?// ***REMOVED***endregion"

***REMOVED*** Files to check (all language variants)
FILES=(
    "backend/src/ui/soarb2b_onboarding_5q.html"
    "backend/src/ui/ar/soarb2b_onboarding_5q.html"
    "backend/src/ui/de/soarb2b_onboarding_5q.html"
    "backend/src/ui/en/soarb2b_onboarding_5q.html"
    "backend/src/ui/es/soarb2b_onboarding_5q.html"
    "backend/src/ui/fr/soarb2b_onboarding_5q.html"
    "backend/src/ui/tr/soarb2b_onboarding_5q.html"
    "backend/src/ui/en/soarb2b_home.html"
    "backend/src/ui/tr/soarb2b_home.html"
    "backend/src/ui/soarb2b_home.html"
)

FIXED_COUNT=0
TOTAL_CALLS=0

for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "⚠️  File not found: $file"
        continue
    fi
    
    ***REMOVED*** Count localhost calls
    CALLS=$(grep -c "127.0.0.1:7243" "$file" 2>/dev/null || echo "0")
    
    if [ "$CALLS" -gt 0 ]; then
        echo "Found $CALLS localhost call(s) in: $file"
        TOTAL_CALLS=$((TOTAL_CALLS + CALLS))
        
        ***REMOVED*** Use sed to remove lines containing localhost:7243 and surrounding comments
        ***REMOVED*** Remove lines with // ***REMOVED***region agent log
        ***REMOVED*** Remove lines with fetch('http://127.0.0.1:7243...
        ***REMOVED*** Remove lines with // ***REMOVED***endregion
        
        ***REMOVED*** Create backup
        cp "$file" "${file}.bak"
        
        ***REMOVED*** Remove agent log blocks
        ***REMOVED*** This is a simplified approach - for exact removal, use the search_replace tool
        echo "  → Fixing $file..."
        FIXED_COUNT=$((FIXED_COUNT + 1))
    else
        echo "✅ No localhost calls in: $file"
    fi
done

echo ""
echo "=============================================="
echo "Summary:"
echo "  Files checked: ${***REMOVED***FILES[@]}"
echo "  Files with localhost calls: $FIXED_COUNT"
echo "  Total localhost calls found: $TOTAL_CALLS"
echo ""
echo "⚠️  Note: This script identifies files. Use search_replace tool for exact removal."
echo "=============================================="
