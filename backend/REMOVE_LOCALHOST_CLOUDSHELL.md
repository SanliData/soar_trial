***REMOVED*** Remove Localhost Calls - Cloud Shell Direct Commands

***REMOVED******REMOVED*** ⚡ Quick Fix (No Script Needed)

Cloud Shell'de doğrudan çalıştır:

```bash
cd /home/isanli058

***REMOVED*** 1. Önce kaç tane var kontrol et
echo "📊 Checking for localhost calls..."
grep -r "127\.0\.0\.1:7243" Finder_os/backend/src/ui 2>/dev/null | wc -l

***REMOVED*** 2. Hangi dosyalarda var göster
echo "📁 Files with localhost calls:"
grep -r "127\.0\.0\.1:7243" Finder_os/backend/src/ui 2>/dev/null | cut -d: -f1 | sort -u

***REMOVED*** 3. TÜM localhost çağrılarını kaldır
echo "🔧 Removing localhost calls..."
find Finder_os/backend/src/ui -name "*.html" -type f -exec sed -i '/127\.0\.0\.1:7243/d' {} \;

***REMOVED*** 4. Doğrula - 0 olmalı
echo "✅ Verification:"
REMAINING=$(grep -r "127\.0\.0\.1:7243" Finder_os/backend/src/ui 2>/dev/null | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    echo "✅ SUCCESS: All localhost calls removed!"
else
    echo "❌ WARNING: $REMAINING call(s) still remain"
    grep -r "127\.0\.0\.1:7243" Finder_os/backend/src/ui 2>/dev/null
fi
```

***REMOVED******REMOVED*** 📋 Step-by-Step (Safer)

```bash
cd /home/isanli058

***REMOVED*** Step 1: Check what we have
grep -r "127\.0\.0\.1:7243" Finder_os/backend/src/ui 2>/dev/null

***REMOVED*** Step 2: Create backup (optional but recommended)
cp -r Finder_os/backend/src/ui Finder_os/backend/src/ui.backup

***REMOVED*** Step 3: Remove all localhost calls
find Finder_os/backend/src/ui -name "*.html" -type f -exec sed -i '/127\.0\.0\.1:7243/d' {} \;

***REMOVED*** Step 4: Verify
grep -r "127\.0\.0\.1:7243" Finder_os/backend/src/ui 2>/dev/null || echo "✅ CLEAN"

***REMOVED*** Step 5: Check git status
cd Finder_os
git status
git diff --stat backend/src/ui
```

***REMOVED******REMOVED*** 🎯 One-Liner (Fastest)

```bash
cd /home/isanli058 && find Finder_os/backend/src/ui -name "*.html" -type f -exec sed -i '/127\.0\.0\.1:7243/d' {} \; && echo "✅ Done" && grep -r "127\.0\.0\.1:7243" Finder_os/backend/src/ui 2>/dev/null | wc -l
```

**Expected output:** `✅ Done` and `0` (zero remaining calls)
