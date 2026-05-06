***REMOVED*** Cloudflare Cache Rules - Detaylı Süreç

***REMOVED******REMOVED*** 📋 Adım Adım Kurulum

***REMOVED******REMOVED******REMOVED*** ADIM 1: Cloudflare Dashboard'a Giriş

1. **Tarayıcıda aç:**
   - https://dash.cloudflare.com
   - Giriş yap (eğer giriş yapmadıysan)

2. **Domain seç:**
   - Ana sayfada `soarb2b.com` domain'ini bul
   - Üzerine tıkla

---

***REMOVED******REMOVED******REMOVED*** ADIM 2: Cache'i Temizle (ÖNEMLİ - ÖNCE BUNU YAP!)

**Neden önce purge?**
- Edge cache'de eski HTML dosyaları olabilir
- Kuralları oluştursan bile eski içerik servis edilebilir
- Purge yapmadan kurallar etkisiz kalabilir

**Nasıl yapılır:**

1. **Sol menüden:**
   - **Caching** → **Configuration** → **Purge Cache**

2. **Purge seçenekleri:**
   - **Purge Everything** seçeneğini işaretle
   - (Tüm cache'i temizler)

3. **Onayla:**
   - **Purge Everything** butonuna tıkla
   - Onay mesajını bekle (birkaç saniye sürebilir)

**✅ Başarı mesajı:**
- "Cache purged successfully" gibi bir mesaj görürsün

---

***REMOVED******REMOVED******REMOVED*** ADIM 3: Cache Rules Oluştur

**Neden Cache Rules?**
- HTML dosyalarının cache'lenmesini engellemek için
- Her zaman origin'den fresh content almak için
- Cloudflare edge'in HTML'i cache'lememesini sağlamak için

***REMOVED******REMOVED******REMOVED******REMOVED*** KURAL 1: HTML Dosyalarını Bypass Et

**1. Cache Rules sayfasına git:**
   - Sol menü: **Caching** → **Configuration** → **Cache Rules**
   - **Create rule** butonuna tıkla

**2. Rule adı:**
   - **Rule name:** `Bypass HTML Files`
   - (İstediğin bir isim verebilirsin)

**3. IF (Koşul) kısmı:**

   **Koşul 1:**
   - **Field:** `URI Path` seç
   - **Operator:** `ends with` seç
   - **Value:** `.html` yaz

   **AND butonuna tıkla** (ikinci koşul eklemek için)

   **Koşul 2:**
   - **Field:** `URI Path` seç
   - **Operator:** `contains` seç
   - **Value:** `/ui/` yaz

   **Sonuç:**
   - Bu kural: `/ui/` içeren VE `.html` ile biten tüm path'ler için geçerli

**4. THEN (Aksiyon) kısmı:**

   **Cache status:**
   - **Bypass** seç
   - (Bu, Cloudflare'in bu dosyaları cache'lememesini sağlar)

**5. Kaydet:**
   - **Deploy** veya **Save** butonuna tıkla
   - Kural aktif olur (birkaç saniye sürebilir)

***REMOVED******REMOVED******REMOVED******REMOVED*** KURAL 2: UI Klasörünü Bypass Et

**1. Yeni kural oluştur:**
   - **Create rule** butonuna tekrar tıkla

**2. Rule adı:**
   - **Rule name:** `Bypass UI Directory`

**3. IF (Koşul):**

   **Koşul:**
   - **Field:** `URI Path` seç
   - **Operator:** `starts with` seç
   - **Value:** `/ui/` yaz

   **Not:** Bu kural daha geniş kapsamlı - `/ui/` ile başlayan HER ŞEY için geçerli

**4. THEN (Aksiyon):**

   **Cache status:**
   - **Bypass** seç

**5. Kaydet:**
   - **Deploy** veya **Save** butonuna tıkla

---

***REMOVED******REMOVED******REMOVED*** ADIM 4: Speed Optimizasyonlarını Kapat

**Neden?**
- Rocket Loader, HTML Minify gibi optimizasyonlar HTML'i değiştirebilir
- Bu, cache sorunlarına yol açabilir
- HTML dosyaları için bu optimizasyonlar gerekli değil

***REMOVED******REMOVED******REMOVED******REMOVED*** Rocket Loader'ı Kapat

1. **Sol menü:**
   - **Speed** → **Optimization**

2. **Rocket Loader:**
   - **Off** konumuna getir
   - **Save** butonuna tıkla

***REMOVED******REMOVED******REMOVED******REMOVED*** HTML Minification'ı Kapat

1. **Aynı sayfada (Speed → Optimization):**
   - **Auto Minify** bölümünü bul

2. **HTML:**
   - **Off** yap
   - **Save** butonuna tıkla

***REMOVED******REMOVED******REMOVED******REMOVED*** APO'yu Kapat (Eğer aktifse)

1. **Aynı sayfada:**
   - **APO (Automatic Platform Optimization)** bölümünü bul

2. **Off yap:**
   - Eğer aktifse, **Off** yap
   - **Save** butonuna tıkla

---

***REMOVED******REMOVED******REMOVED*** ADIM 5: Doğrulama

**Cloud Shell'de test et:**

```bash
curl -I https://soarb2b.com/ui/tr/soarb2b_home.html | grep -i "cf-cache-status\|cache-control"
```

**Beklenen çıktı:**

```
cf-cache-status: BYPASS
cache-control: no-store, no-cache, must-revalidate, max-age=0
```

**Açıklama:**
- `cf-cache-status: BYPASS` → Cloudflare edge cache'i bypass ediyor ✅
- `cache-control: ...` → Backend'den gelen header'lar doğru ✅

---

***REMOVED******REMOVED*** 📊 Kural Önceliği

**Cloudflare Cache Rules sırası:**
1. En spesifik kural önce çalışır
2. İlk eşleşen kural uygulanır
3. Bizim kurallarımız:
   - Kural 1: `/ui/*.html` dosyaları için
   - Kural 2: `/ui/*` her şey için (daha geniş)

**Sonuç:**
- HTML dosyaları → Kural 1 uygulanır
- Diğer UI dosyaları → Kural 2 uygulanır
- Her ikisi de **Bypass** yapar

---

***REMOVED******REMOVED*** ⚠️ Önemli Notlar

1. **Purge önce yapılmalı:**
   - Kuralları oluşturmadan önce cache'i temizle
   - Aksi halde eski içerik servis edilmeye devam eder

2. **Kurallar hemen aktif olmaz:**
   - Deploy sonrası 1-2 dakika sürebilir
   - Global edge network'e yayılması gerekir

3. **Test et:**
   - Kuralları oluşturduktan sonra mutlaka test et
   - `cf-cache-status: BYPASS` görüyorsan başarılı

4. **Backend header'ları:**
   - Backend zaten doğru header'ları gönderiyor
   - Cloudflare kuralları bunu destekliyor

---

***REMOVED******REMOVED*** 🎯 Özet Checklist

- [ ] Cloudflare Dashboard'a giriş yap
- [ ] Domain seç (`soarb2b.com`)
- [ ] **Purge Cache** yap (Purge Everything)
- [ ] **Cache Rules** oluştur:
  - [ ] Kural 1: HTML dosyaları bypass
  - [ ] Kural 2: UI klasörü bypass
- [ ] **Speed Optimizations** kapat:
  - [ ] Rocket Loader: Off
  - [ ] HTML Minify: Off
  - [ ] APO: Off (eğer aktifse)
- [ ] Test et (`curl` komutu)
- [ ] `cf-cache-status: BYPASS` görüyorsan ✅ BAŞARILI

---

**Status:** ⚠️ **MANUEL YAPILANDIRMA GEREKLİ**  
**Süre:** ~5-10 dakika  
**Zorluk:** Kolay (adım adım takip et)
