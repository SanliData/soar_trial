***REMOVED*** Localhost Çağrılarını Kaldır - Basit Yöntem

***REMOVED******REMOVED*** ⚡ Cloud Shell'de Çalıştır

```bash
***REMOVED*** 1. Dizine git
cd /home/isanli058
cd Finder_os/backend/src/ui

***REMOVED*** 2. Kaç tane var kontrol et
grep -r "127.0.0.1:7243" . | wc -l

***REMOVED*** 3. Hangi dosyalarda var
grep -r "127.0.0.1:7243" . | cut -d: -f1 | sort -u

***REMOVED*** 4. Kaldır (her dosya için)
find . -name "*.html" -type f -exec sh -c 'grep -v "127.0.0.1:7243" "$1" > "$1.tmp" && mv "$1.tmp" "$1"' _ {} \;

***REMOVED*** 5. Doğrula
grep -r "127.0.0.1:7243" . || echo "✅ TEMİZ"
```

***REMOVED******REMOVED*** 🎯 Tek Komut (En Basit)

```bash
cd /home/isanli058/Finder_os/backend/src/ui && find . -name "*.html" -type f -exec sh -c 'grep -v "127.0.0.1:7243" "$1" > "$1.tmp" && mv "$1.tmp" "$1"' _ {} \; && echo "✅ Tamamlandı" && grep -r "127.0.0.1:7243" . 2>/dev/null | wc -l
```

**Beklenen çıktı:** `✅ Tamamlandı` ve `0`

***REMOVED******REMOVED*** 📋 Adım Adım (En Güvenli)

```bash
***REMOVED*** 1. Dizine git
cd /home/isanli058/Finder_os/backend/src/ui

***REMOVED*** 2. Kontrol et
echo "Kontrol ediliyor..."
grep -r "127.0.0.1:7243" . 

***REMOVED*** 3. Her HTML dosyasını temizle
for file in $(find . -name "*.html" -type f); do
    echo "İşleniyor: $file"
    grep -v "127.0.0.1:7243" "$file" > "$file.new"
    mv "$file.new" "$file"
done

***REMOVED*** 4. Doğrula
echo "Doğrulanıyor..."
grep -r "127.0.0.1:7243" . || echo "✅ HEPsi temiz!"
```

***REMOVED******REMOVED*** 🔍 Sadece Kontrol Etmek İçin

```bash
cd /home/isanli058/Finder_os/backend/src/ui
grep -r "127.0.0.1:7243" . | wc -l
```

**0 olmalı** - eğer 0 değilse, yukarıdaki komutları çalıştır.
