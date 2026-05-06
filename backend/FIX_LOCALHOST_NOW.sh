***REMOVED***!/bin/bash
***REMOVED*** FIX_LOCALHOST_NOW.sh - Cloud Shell için basit ve güvenilir
***REMOVED*** Tüm localhost çağrılarını kaldırır

set -e

echo "🔧 Localhost çağrılarını kaldırıyor..."
echo ""

***REMOVED*** Önce kontrol et
cd /home/isanli058/Finder_os/backend/src/ui 2>/dev/null || cd /home/isanli058/FINDER_OS/backend/src/ui 2>/dev/null || {
    echo "❌ HATA: Finder_os dizini bulunamadı"
    echo "Mevcut dizin: $(pwd)"
    echo "Lütfen doğru dizine gidin"
    exit 1
}

***REMOVED*** Kaç tane var?
COUNT=$(grep -r "127\.0\.0\.1:7243" . 2>/dev/null | wc -l)
echo "📊 Bulunan localhost çağrısı: $COUNT"
echo ""

if [ "$COUNT" -eq 0 ]; then
    echo "✅ Zaten temiz!"
    exit 0
fi

***REMOVED*** Hangi dosyalarda var?
echo "📁 Etkilenen dosyalar:"
grep -r "127\.0\.0\.1:7243" . 2>/dev/null | cut -d: -f1 | sort -u
echo ""

***REMOVED*** Kaldır
echo "🔧 Kaldırılıyor..."
find . -name "*.html" -type f | while read file; do
    if grep -q "127\.0\.0\.1:7243" "$file" 2>/dev/null; then
        ***REMOVED*** Backup oluştur
        cp "$file" "${file}.bak"
        ***REMOVED*** Localhost satırlarını kaldır
        grep -v "127\.0\.0\.1:7243" "$file" > "${file}.tmp"
        mv "${file}.tmp" "$file"
        echo "  ✅ $file temizlendi"
    fi
done

***REMOVED*** Doğrula
REMAINING=$(grep -r "127\.0\.0\.1:7243" . 2>/dev/null | wc -l)
echo ""
if [ "$REMAINING" -eq 0 ]; then
    echo "✅ BAŞARILI: Tüm localhost çağrıları kaldırıldı!"
    ***REMOVED*** Backup dosyalarını sil
    find . -name "*.bak" -type f -delete
else
    echo "⚠️  UYARI: $REMAINING çağrı hala var"
    grep -r "127\.0\.0\.1:7243" . 2>/dev/null
fi
