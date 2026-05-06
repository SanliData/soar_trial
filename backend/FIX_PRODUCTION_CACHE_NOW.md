***REMOVED*** Production Cache Fix - Acil Çözüm

**Problem:** Production'da hala eski metin görünüyor

---

***REMOVED******REMOVED*** 🔍 Durum Kontrolü

***REMOVED******REMOVED******REMOVED*** 1️⃣ Push Durumu (Local → GitHub)

**PowerShell'de kontrol:**
```powershell
cd C:\Users\issan\OneDrive\ISMAIL_SANLI\FINDER_OS
git status
git log --oneline -3
```

**Eğer push edilmemişse:**
```powershell
git push origin main
```

---

***REMOVED******REMOVED******REMOVED*** 2️⃣ Deploy Durumu (GitHub → Cloud Run)

**Cloud Shell'de:**
```bash
cd /home/isanli058/Finder_os

***REMOVED*** Pull latest from GitHub
git pull origin main

***REMOVED*** Deploy to Cloud Run
gcloud run deploy soarb2b \
  --source backend \
  --region us-central1 \
  --project finderos-entegrasyon-480708 \
  --service-account soarb2b@finderos-entegrasyon-480708.iam.gserviceaccount.com \
  --set-secrets="GOOGLE_CLIENT_ID=google-client-id:latest,JWT_SECRET=jwt-secret:latest,QUOTE_SECRET=quote-secret:latest" \
  --allow-unauthenticated
```

---

***REMOVED******REMOVED******REMOVED*** 3️⃣ Cloudflare Cache Purge

**Cloudflare Dashboard'da:**
1. **Cache → Purge Everything** yap
2. Veya **Cache Rules** ile `/ui/*.html` için **Bypass** aktif et

**API ile (Cloud Shell'de):**
```bash
***REMOVED*** Cloudflare API Token gerekli
***REMOVED*** Dashboard → My Profile → API Tokens
curl -X POST "https://api.cloudflare.com/client/v4/zones/YOUR_ZONE_ID/purge_cache" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

---

***REMOVED******REMOVED*** 🚨 Hızlı Çözüm (Tüm Adımlar)

***REMOVED******REMOVED******REMOVED*** Step 1: Push (Eğer edilmemişse)

```powershell
cd C:\Users\issan\OneDrive\ISMAIL_SANLI\FINDER_OS
git push origin main
```

***REMOVED******REMOVED******REMOVED*** Step 2: Cloud Shell'de Pull + Deploy

```bash
cd /home/isanli058/Finder_os
git pull origin main

***REMOVED*** Deploy
gcloud run deploy soarb2b \
  --source backend \
  --region us-central1 \
  --project finderos-entegrasyon-480708 \
  --service-account soarb2b@finderos-entegrasyon-480708.iam.gserviceaccount.com \
  --set-secrets="GOOGLE_CLIENT_ID=google-client-id:latest,JWT_SECRET=jwt-secret:latest,QUOTE_SECRET=quote-secret:latest" \
  --allow-unauthenticated
```

***REMOVED******REMOVED******REMOVED*** Step 3: Cloudflare Cache Purge

**Cloudflare Dashboard:**
- **Caching → Configuration → Purge Everything**

**VEYA Cache Rules:**
- **Caching → Cache Rules → Create rule**
- **IF:** URI Path contains `/ui/` AND ends with `.html`
- **THEN:** Bypass cache

***REMOVED******REMOVED******REMOVED*** Step 4: Doğrula

```bash
***REMOVED*** Cloud Run direct (bypass Cloudflare)
curl -s https://soarb2b-274308964876.us-central1.run.app/ui/en/soarb2b_onboarding_5q.html | grep -i "successfully received"

***REMOVED*** Cloudflare üzerinden
curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html | grep -i "successfully received"
```

**Beklenen:** "Your request has been successfully received..." görünmeli

---

***REMOVED******REMOVED*** 📋 Kontrol Komutları

***REMOVED******REMOVED******REMOVED*** Production Metin Kontrolü

```bash
***REMOVED*** Eski metin var mı? (olmamalı)
curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html | grep -i "We have received your English request"

***REMOVED*** Yeni metin var mı? (olmalı)
curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html | grep -i "Your request has been successfully received"
```

***REMOVED******REMOVED******REMOVED*** Cache Headers Kontrolü

```bash
curl -I https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html | grep -i "cf-cache-status\|cache-control"
```

**Beklenen:**
- `cf-cache-status: BYPASS` veya `DYNAMIC`
- `cache-control: no-store, no-cache, must-revalidate, max-age=0`

---

***REMOVED******REMOVED*** ⚡ Tek Komutla Kontrol (Cloud Shell)

```bash
echo "=== PRODUCTION X-RAY ===" && \
echo "Eski metin var mı?" && \
curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html | grep -c "We have received your English request" && \
echo "Yeni metin var mı?" && \
curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html | grep -c "Your request has been successfully received" && \
echo "Auto-start toggle var mı?" && \
curl -s https://soarb2b.com/ui/en/soarb2b_onboarding_5q.html | grep -c "autoStartQueries"
```

**Beklenen:**
- Eski metin: `0`
- Yeni metin: `1` veya daha fazla
- Auto-start toggle: `2` (checkbox + backend submission)
