***REMOVED*** Localhost Çağrılarını Kaldır - Cloud Shell Final

***REMOVED******REMOVED*** ✅ Doğru Komutlar (Cloud Shell Çalışma Klasörü)

```bash
***REMOVED*** 1. Çalışma klasörüne git
cd ~

***REMOVED*** 2. Finder_os dizinini bul ve git
if [ -d "Finder_os" ]; then
    cd Finder_os/backend/src/ui
elif [ -d "FINDER_OS" ]; then
    cd FINDER_OS/backend/src/ui
else
    echo "❌ Finder_os dizini bulunamadı"
    ls -la | grep -i finder
    exit 1
fi

***REMOVED*** 3. Kaç tane var kontrol et
echo "📊 Kontrol ediliyor..."
COUNT=$(grep -r "127.0.0.1:7243" . 2>/dev/null | wc -l)
echo "Bulunan: $COUNT adet"

***REMOVED*** 4. Eğer varsa, kaldır
if [ "$COUNT" -gt 0 ]; then
    echo "🔧 Kaldırılıyor..."
    find . -name "*.html" -type f | while read file; do
        if grep -q "127.0.0.1:7243" "$file" 2>/dev/null; then
            grep -v "127.0.0.1:7243" "$file" > "$file.tmp"
            mv "$file.tmp" "$file"
            echo "  ✅ $(basename $file)"
        fi
    done
    
    ***REMOVED*** 5. Doğrula
    REMAINING=$(grep -r "127.0.0.1:7243" . 2>/dev/null | wc -l)
    if [ "$REMAINING" -eq 0 ]; then
        echo "✅ BAŞARILI: Hepsi temiz!"
    else
        echo "❌ Hala $REMAINING adet var"
    fi
else
    echo "✅ Zaten temiz!"
fi
```

***REMOVED******REMOVED*** 🎯 Tek Komut (Kopyala-Yapıştır)

```bash
cd ~ && if [ -d "Finder_os" ]; then cd Finder_os/backend/src/ui; elif [ -d "FINDER_OS" ]; then cd FINDER_OS/backend/src/ui; else echo "Dizin bulunamadı"; exit 1; fi && find . -name "*.html" -type f -exec sh -c 'if grep -q "127.0.0.1:7243" "$1"; then grep -v "127.0.0.1:7243" "$1" > "$1.tmp" && mv "$1.tmp" "$1"; fi' _ {} \; && echo "✅ Tamamlandı" && echo "Kalan: $(grep -r '127.0.0.1:7243' . 2>/dev/null | wc -l)"
```

***REMOVED******REMOVED*** 📋 Adım Adım (En Güvenli)

```bash
***REMOVED*** 1. Home dizinine git
cd ~

***REMOVED*** 2. Dizini bul
ls -la | grep -i finder

***REMOVED*** 3. Doğru dizine git (bulduğun isme göre)
cd Finder_os/backend/src/ui
***REMOVED*** VEYA
cd FINDER_OS/backend/src/ui

***REMOVED*** 4. Kontrol et
grep -r "127.0.0.1:7243" . 2>/dev/null | wc -l

***REMOVED*** 5. Kaldır
find . -name "*.html" -type f | while read file; do
    if grep -q "127.0.0.1:7243" "$file" 2>/dev/null; then
        grep -v "127.0.0.1:7243" "$file" > "$file.tmp"
        mv "$file.tmp" "$file"
    fi
done

***REMOVED*** 6. Doğrula
grep -r "127.0.0.1:7243" . 2>/dev/null || echo "✅ TEMİZ"
```

***REMOVED******REMOVED*** 🔍 Sadece Kontrol

```bash
cd ~
cd Finder_os/backend/src/ui 2>/dev/null || cd FINDER_OS/backend/src/ui
grep -r "127.0.0.1:7243" . 2>/dev/null | wc -l
```

**0 çıkmalı** - eğer 0 değilse, yukarıdaki kaldırma komutunu çalıştır.
