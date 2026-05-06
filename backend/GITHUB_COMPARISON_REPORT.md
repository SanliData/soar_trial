***REMOVED*** GitHub vs Local vs Production - Karşılaştırma Raporu

**Tarih:** 2026-01-20  
**Dosya:** `backend/src/ui/en/soarb2b_onboarding_5q.html`

---

***REMOVED******REMOVED*** 🔍 Kontrol Komutları

***REMOVED******REMOVED******REMOVED*** 1️⃣ Local Kontrol (Windows)

```powershell
cd C:\Users\issan\OneDrive\ISMAIL_SANLI\FINDER_OS

***REMOVED*** Metin kontrolü
Select-String -Path "backend\src\ui\en\soarb2b_onboarding_5q.html" -Pattern "result-subtitle" -Context 0,2

***REMOVED*** Auto-start toggle
Select-String -Path "backend\src\ui\en\soarb2b_onboarding_5q.html" -Pattern "autoStartQueries"
```

***REMOVED******REMOVED******REMOVED*** 2️⃣ GitHub Kontrolü

```bash
***REMOVED*** GitHub raw URL
GITHUB_URL="https://raw.githubusercontent.com/SanliData/Finder_os/main/backend/src/ui/en/soarb2b_onboarding_5q.html"

***REMOVED*** Result subtitle metni
curl -s "$GITHUB_URL" | grep -A 2 "result-subtitle"

***REMOVED*** Eski metin var mı?
curl -s "$GITHUB_URL" | grep -c "We have received your English request" || echo "0"

***REMOVED*** Yeni metin var mı?
curl -s "$GITHUB_URL" | grep -c "Your request has been successfully received" || echo "0"

***REMOVED*** Auto-start toggle var mı?
curl -s "$GITHUB_URL" | grep -c "autoStartQueries" || echo "0"
```

***REMOVED******REMOVED******REMOVED*** 3️⃣ Production Kontrolü

```bash
***REMOVED*** Cloud Run (direct)
curl -s https://soarb2b-274308964876.us-central1.run.app/ui/en/soarb2b_onboarding_5q.html | grep -A 2 "result-subtitle"

***REMOVED*** Cloudflare
curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html | grep -A 2 "result-subtitle"
```

---

***REMOVED******REMOVED*** 📊 Karşılaştırma Tablosu

| Kontrol | Local | GitHub | Production (Cloud Run) | Production (Cloudflare) |
|---------|-------|--------|------------------------|-------------------------|
| **Eski metin** ("We have received your English request") | ❌ 0 | ? | ? | ? |
| **Yeni metin** ("Your request has been successfully received") | ✅ 1 | ? | ? | ? |
| **Auto-start toggle** | ✅ 2 | ? | ? | ? |

---

***REMOVED******REMOVED*** 🔧 Tek Komutla Tüm Kontroller (Cloud Shell)

```bash
***REMOVED***!/bin/bash
echo "=== GITHUB vs LOCAL vs PRODUCTION ==="
echo ""

GITHUB_URL="https://raw.githubusercontent.com/SanliData/Finder_os/main/backend/src/ui/en/soarb2b_onboarding_5q.html"

echo "1. GITHUB - Result Subtitle:"
curl -s "$GITHUB_URL" | grep -A 1 "result-subtitle" | grep -v "^--$" | head -3
echo ""

echo "2. GITHUB - Old Text Count:"
curl -s "$GITHUB_URL" | grep -c "We have received your English request" || echo "0"
echo ""

echo "3. GITHUB - New Text Count:"
curl -s "$GITHUB_URL" | grep -c "Your request has been successfully received" || echo "0"
echo ""

echo "4. GITHUB - Auto-Start Toggle Count:"
curl -s "$GITHUB_URL" | grep -c "autoStartQueries" || echo "0"
echo ""

echo "5. PRODUCTION (Cloud Run) - Result Subtitle:"
curl -s https://soarb2b-274308964876.us-central1.run.app/ui/en/soarb2b_onboarding_5q.html | grep -A 1 "result-subtitle" | grep -v "^--$" | head -3
echo ""

echo "6. PRODUCTION (Cloudflare) - Result Subtitle:"
curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html | grep -A 1 "result-subtitle" | grep -v "^--$" | head -3
echo ""

echo "7. PRODUCTION (Cloud Run) - Old Text Count:"
curl -s https://soarb2b-274308964876.us-central1.run.app/ui/en/soarb2b_onboarding_5q.html | grep -c "We have received your English request" || echo "0"
echo ""

echo "8. PRODUCTION (Cloud Run) - New Text Count:"
curl -s https://soarb2b-274308964876.us-central1.run.app/ui/en/soarb2b_onboarding_5q.html | grep -c "Your request has been successfully received" || echo "0"
echo ""

echo "9. PRODUCTION (Cloudflare) - Old Text Count:"
curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html | grep -c "We have received your English request" || echo "0"
echo ""

echo "10. PRODUCTION (Cloudflare) - New Text Count:"
curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html | grep -c "Your request has been successfully received" || echo "0"
echo ""
```

---

***REMOVED******REMOVED*** 📋 Beklenen Sonuçlar

***REMOVED******REMOVED******REMOVED*** ✅ Local (Doğru)
- Eski metin: **0**
- Yeni metin: **1**
- Auto-start toggle: **2**

***REMOVED******REMOVED******REMOVED*** ✅ GitHub (Push sonrası beklenen)
- Eski metin: **0**
- Yeni metin: **1**
- Auto-start toggle: **2**

***REMOVED******REMOVED******REMOVED*** ✅ Production (Deploy sonrası beklenen)
- Eski metin: **0**
- Yeni metin: **1**
- Auto-start toggle: **2**

---

***REMOVED******REMOVED*** 🚨 Fark Bulunursa

**Eğer GitHub'da eski metin varsa:**
1. Push yapılmamış demektir
2. `git push origin main` yapın

**Eğer Production'da eski metin varsa:**
1. Deploy yapılmamış demektir
2. Cloud Shell'de pull + deploy yapın
3. Cloudflare cache purge yapın

---

***REMOVED******REMOVED*** 🎯 Hızlı Kontrol (Cloud Shell)

```bash
bash backend/GITHUB_VS_LOCAL_COMPARISON.sh
```
