***REMOVED***!/bin/bash
***REMOVED*** VERIFY_LOCALHOST_REMOVAL.sh
***REMOVED*** PURPOSE: Verify all localhost:7243 calls are removed
***REMOVED*** ENCODING: UTF-8 WITHOUT BOM

BASE_DIR="${1:-Finder_os/backend/src/ui}"

echo "🔍 Verifying localhost call removal"
echo "==================================="
echo ""

***REMOVED*** Count remaining occurrences
REMAINING=$(grep -r "127\.0\.0\.1:7243" "$BASE_DIR" 2>/dev/null | wc -l || echo "0")

if [ "$REMAINING" -eq 0 ]; then
    echo "✅ SUCCESS: No localhost calls found"
    echo "✅ All files are clean"
    exit 0
else
    echo "❌ FAILED: $REMAINING localhost call(s) still remain"
    echo ""
    echo "Files with remaining calls:"
    grep -r "127\.0\.0\.1:7243" "$BASE_DIR" 2>/dev/null | cut -d: -f1 | sort -u
    echo ""
    echo "Run REMOVE_ALL_LOCALHOST_CALLS.sh to remove them"
    exit 1
fi
