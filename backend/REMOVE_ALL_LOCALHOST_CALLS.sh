***REMOVED***!/bin/bash
***REMOVED*** REMOVE_ALL_LOCALHOST_CALLS.sh
***REMOVED*** PURPOSE: Remove ALL localhost:7243 API calls from production UI files
***REMOVED*** ENCODING: UTF-8 WITHOUT BOM
***REMOVED*** USAGE: Run from Cloud Shell or local terminal

set -e  ***REMOVED*** Exit on error

echo "🔧 Removing ALL localhost API calls from production UI files"
echo "============================================================"
echo ""

***REMOVED*** Base directory (adjust if needed)
BASE_DIR="${1:-Finder_os/backend/src/ui}"

if [ ! -d "$BASE_DIR" ]; then
    echo "❌ ERROR: Directory not found: $BASE_DIR"
    echo "Usage: $0 [base_directory]"
    echo "Example: $0 Finder_os/backend/src/ui"
    exit 1
fi

echo "📁 Scanning directory: $BASE_DIR"
echo ""

***REMOVED*** Count total occurrences before removal
TOTAL_BEFORE=$(grep -r "127\.0\.0\.1:7243" "$BASE_DIR" 2>/dev/null | wc -l || echo "0")
echo "📊 Found $TOTAL_BEFORE localhost call(s) before removal"
echo ""

if [ "$TOTAL_BEFORE" -eq 0 ]; then
    echo "✅ No localhost calls found. Files are already clean."
    exit 0
fi

***REMOVED*** Find all HTML files
HTML_FILES=$(find "$BASE_DIR" -name "*.html" -type f)

FIXED_COUNT=0
TOTAL_REMOVED=0

for file in $HTML_FILES; do
    ***REMOVED*** Count occurrences in this file
    COUNT=$(grep -c "127\.0\.0\.1:7243" "$file" 2>/dev/null || echo "0")
    
    if [ "$COUNT" -gt 0 ]; then
        echo "🔍 Found $COUNT localhost call(s) in: $file"
        
        ***REMOVED*** Create backup
        cp "$file" "${file}.bak"
        
        ***REMOVED*** Remove lines containing localhost:7243
        ***REMOVED*** This removes the entire line, including surrounding comments if on same line
        sed -i "/127\.0\.0\.1:7243/d" "$file"
        
        ***REMOVED*** Also remove surrounding comment blocks if they're on separate lines
        ***REMOVED*** Remove lines with "// ***REMOVED***region agent log" that are followed by localhost calls
        ***REMOVED*** Remove lines with "// ***REMOVED***endregion" that are after localhost calls
        sed -i '/\/\/ ***REMOVED***region agent log/,/\/\/ ***REMOVED***endregion/{/127\.0\.0\.1:7243/d;}' "$file" 2>/dev/null || true
        
        ***REMOVED*** Verify removal
        REMAINING=$(grep -c "127\.0\.0\.1:7243" "$file" 2>/dev/null || echo "0")
        
        if [ "$REMAINING" -eq 0 ]; then
            echo "  ✅ Removed $COUNT call(s) from $file"
            FIXED_COUNT=$((FIXED_COUNT + 1))
            TOTAL_REMOVED=$((TOTAL_REMOVED + COUNT))
            ***REMOVED*** Remove backup if successful
            rm -f "${file}.bak"
        else
            echo "  ⚠️  WARNING: $REMAINING call(s) still remain in $file"
            ***REMOVED*** Restore backup
            mv "${file}.bak" "$file"
        fi
    fi
done

echo ""
echo "=============================================="
echo "Summary:"
echo "  Files scanned: $(echo "$HTML_FILES" | wc -l)"
echo "  Files with localhost calls: $FIXED_COUNT"
echo "  Total calls removed: $TOTAL_REMOVED"
echo ""

***REMOVED*** Final verification
TOTAL_AFTER=$(grep -r "127\.0\.0\.1:7243" "$BASE_DIR" 2>/dev/null | wc -l || echo "0")

if [ "$TOTAL_AFTER" -eq 0 ]; then
    echo "✅ SUCCESS: All localhost calls removed!"
    echo "✅ Verification: No remaining localhost calls found"
else
    echo "⚠️  WARNING: $TOTAL_AFTER localhost call(s) still remain"
    echo "   Run 'grep -r \"127.0.0.1:7243\" $BASE_DIR' to find them"
fi

echo "=============================================="
