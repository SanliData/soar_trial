***REMOVED***!/bin/bash
***REMOVED*** Check Duplicate Finder Folders

echo "========================================"
echo "İKİ FINDER KLASÖRÜ KONTROLÜ"
echo "========================================"
echo ""

FINDER_SMALL="/home/isanli058/Finder_os"
FINDER_BIG="/home/isanli058/FINDER_OS"

echo "1️⃣ Finder_os (küçük harf)"
echo "========================================"
if [ -d "$FINDER_SMALL" ]; then
    echo "✅ Klasör mevcut"
    if [ -f "$FINDER_SMALL/backend/src/ui/en/soarb2b_onboarding_5q.html" ]; then
        TOGGLE=$(grep -c "autoStartQueries" "$FINDER_SMALL/backend/src/ui/en/soarb2b_onboarding_5q.html" 2>/dev/null || echo "0")
        OLD_TEXT=$(grep -c "We have received your English request" "$FINDER_SMALL/backend/src/ui/en/soarb2b_onboarding_5q.html" 2>/dev/null || echo "0")
        NEW_TEXT=$(grep -c "Your request has been successfully received" "$FINDER_SMALL/backend/src/ui/en/soarb2b_onboarding_5q.html" 2>/dev/null || echo "0")
        
        echo "  Auto-start toggle: $TOGGLE"
        echo "  Eski metin: $OLD_TEXT"
        echo "  Yeni metin: $NEW_TEXT"
        
        cd "$FINDER_SMALL" 2>/dev/null
        if [ -d ".git" ]; then
            LAST_COMMIT=$(git log -1 --format="%ct %H" 2>/dev/null)
            if [ -n "$LAST_COMMIT" ]; then
                COMMIT_TIME=$(echo "$LAST_COMMIT" | cut -d' ' -f1)
                COMMIT_HASH=$(echo "$LAST_COMMIT" | cut -d' ' -f2)
                COMMIT_DATE=$(date -d "@$COMMIT_TIME" +"%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "N/A")
                echo "  Son commit: $COMMIT_DATE ($COMMIT_HASH)"
                echo "$COMMIT_TIME" > /tmp/finder_small_time.txt
            fi
        fi
    else
        echo "  ❌ UI dosyası yok"
    fi
else
    echo "  ❌ Klasör yok"
fi
echo ""

echo "2️⃣ FINDER_OS (büyük harf)"
echo "========================================"
if [ -d "$FINDER_BIG" ]; then
    echo "✅ Klasör mevcut"
    if [ -f "$FINDER_BIG/backend/src/ui/en/soarb2b_onboarding_5q.html" ]; then
        TOGGLE=$(grep -c "autoStartQueries" "$FINDER_BIG/backend/src/ui/en/soarb2b_onboarding_5q.html" 2>/dev/null || echo "0")
        OLD_TEXT=$(grep -c "We have received your English request" "$FINDER_BIG/backend/src/ui/en/soarb2b_onboarding_5q.html" 2>/dev/null || echo "0")
        NEW_TEXT=$(grep -c "Your request has been successfully received" "$FINDER_BIG/backend/src/ui/en/soarb2b_onboarding_5q.html" 2>/dev/null || echo "0")
        
        echo "  Auto-start toggle: $TOGGLE"
        echo "  Eski metin: $OLD_TEXT"
        echo "  Yeni metin: $NEW_TEXT"
        
        cd "$FINDER_BIG" 2>/dev/null
        if [ -d ".git" ]; then
            LAST_COMMIT=$(git log -1 --format="%ct %H" 2>/dev/null)
            if [ -n "$LAST_COMMIT" ]; then
                COMMIT_TIME=$(echo "$LAST_COMMIT" | cut -d' ' -f1)
                COMMIT_HASH=$(echo "$LAST_COMMIT" | cut -d' ' -f2)
                COMMIT_DATE=$(date -d "@$COMMIT_TIME" +"%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "N/A")
                echo "  Son commit: $COMMIT_DATE ($COMMIT_HASH)"
                echo "$COMMIT_TIME" > /tmp/finder_big_time.txt
            fi
        fi
    else
        echo "  ❌ UI dosyası yok"
    fi
else
    echo "  ❌ Klasör yok"
fi
echo ""

echo "3️⃣ KARŞILAŞTIRMA"
echo "========================================"
if [ -f "/tmp/finder_small_time.txt" ] && [ -f "/tmp/finder_big_time.txt" ]; then
    SMALL_TIME=$(cat /tmp/finder_small_time.txt)
    BIG_TIME=$(cat /tmp/finder_big_time.txt)
    
    if [ "$SMALL_TIME" -gt "$BIG_TIME" ]; then
        echo "✅ Finder_os (küçük harf) DAHA YENİ"
        echo "   Önerilen: /home/isanli058/Finder_os"
    elif [ "$BIG_TIME" -gt "$SMALL_TIME" ]; then
        echo "✅ FINDER_OS (büyük harf) DAHA YENİ"
        echo "   Önerilen: /home/isanli058/FINDER_OS"
    else
        echo "⚠️  İki klasör de aynı commit zamanına sahip"
    fi
fi

echo ""
echo "========================================"
echo "ÖNERİLEN DEPLOY KOMUTU"
echo "========================================"
if [ -f "/tmp/finder_small_time.txt" ] && [ -f "/tmp/finder_big_time.txt" ]; then
    SMALL_TIME=$(cat /tmp/finder_small_time.txt)
    BIG_TIME=$(cat /tmp/finder_big_time.txt)
    
    if [ "$SMALL_TIME" -ge "$BIG_TIME" ]; then
        echo "cd /home/isanli058/Finder_os"
    else
        echo "cd /home/isanli058/FINDER_OS"
    fi
else
    echo "cd /home/isanli058/Finder_os  ***REMOVED*** Varsayılan"
fi

echo "gcloud run deploy soarb2b \\"
echo "  --source backend \\"
echo "  --region us-central1 \\"
echo "  --project finderos-entegrasyon-480708 \\"
echo "  --service-account soarb2b@finderos-entegrasyon-480708.iam.gserviceaccount.com \\"
echo "  --set-secrets=\"GOOGLE_CLIENT_ID=google-client-id:latest,JWT_SECRET=jwt-secret:latest,QUOTE_SECRET=quote-secret:latest\" \\"
echo "  --allow-unauthenticated"

***REMOVED*** Cleanup
rm -f /tmp/finder_small_time.txt /tmp/finder_big_time.txt
