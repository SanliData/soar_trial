***REMOVED*** Google Cloud Run - Quick Start Guide

***REMOVED******REMOVED*** 🚀 Tek Komutla Deploy

***REMOVED******REMOVED******REMOVED*** Önkoşullar

1. **Google Cloud Account** (billing enabled)
2. **gcloud CLI** kurulu
3. **GCP Project** oluşturulmuş

***REMOVED******REMOVED******REMOVED*** Hızlı Başlangıç (5 Dakika)

```powershell
***REMOVED*** 1. Authenticate
gcloud auth login
gcloud auth application-default login

***REMOVED*** 2. Project Set Et
$env:GCP_PROJECT_ID = "your-project-id"
***REMOVED*** Veya: gcloud config set project your-project-id

***REMOVED*** 3. APIs Enable Et (İlk seferde)
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

***REMOVED*** 4. .env Hazırla (backend/.env)
ENV=production
SOARB2B_API_KEYS=your-production-key-1,your-production-key-2,your-production-key-3
FINDEROS_CORS_ORIGINS=https://soarb2b.com,https://www.soarb2b.com
FINDEROS_CORS_ALLOW_ALL=false

***REMOVED*** 5. DEPLOY!
.\deploy_gcp.ps1
```

***REMOVED******REMOVED******REMOVED*** ✅ Doğrulama

Script otomatik olarak service URL'i gösterecek:

```powershell
***REMOVED*** Health check
Invoke-WebRequest "$serviceUrl/healthz" -UseBasicParsing

***REMOVED*** Homepage
Start-Process "$serviceUrl/ui/soarb2b_home.html"
```

---

***REMOVED******REMOVED*** 📋 Detaylı Adımlar

***REMOVED******REMOVED******REMOVED*** Adım 1: Google Cloud CLI Kurulumu

**Windows:**
```powershell
***REMOVED*** Chocolatey ile
choco install gcloudsdk

***REMOVED*** Veya manuel: https://cloud.google.com/sdk/docs/install
```

**Doğrulama:**
```powershell
gcloud --version
```

***REMOVED******REMOVED******REMOVED*** Adım 2: Authentication

```powershell
***REMOVED*** User authentication
gcloud auth login

***REMOVED*** Application default credentials (Cloud Run için gerekli)
gcloud auth application-default login
```

***REMOVED******REMOVED******REMOVED*** Adım 3: Project Setup

```powershell
***REMOVED*** Projeleri listele
gcloud projects list

***REMOVED*** Project set et
gcloud config set project YOUR_PROJECT_ID

***REMOVED*** Veya environment variable
$env:GCP_PROJECT_ID = "YOUR_PROJECT_ID"
```

***REMOVED******REMOVED******REMOVED*** Adım 4: APIs Enable

```powershell
***REMOVED*** Required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

***REMOVED*** Doğrulama
gcloud services list --enabled | Select-String "run\|build"
```

***REMOVED******REMOVED******REMOVED*** Adım 5: Environment Variables

`backend/.env` dosyası oluştur:

```env
ENV=production
SOARB2B_API_KEYS=production-key-1,production-key-2,production-key-3
FINDEROS_CORS_ORIGINS=https://soarb2b.com,https://www.soarb2b.com
FINDEROS_CORS_ALLOW_ALL=false
```

**Production API Key'leri oluştur:**
```powershell
***REMOVED*** Güvenli key oluştur (32 karakter)
$key1 = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
Write-Host $key1
```

***REMOVED******REMOVED******REMOVED*** Adım 6: Deploy

```powershell
***REMOVED*** Project root'tan
.\deploy_gcp.ps1
```

**Beklenen süre:** 3-5 dakika

---

***REMOVED******REMOVED*** 🎯 Deployment Sonrası

***REMOVED******REMOVED******REMOVED*** Service URL

Script deployment sonrası service URL'i gösterecek:

```
https://soarb2b-xxxxx-ew.a.run.app
```

***REMOVED******REMOVED******REMOVED*** Test Endpoints

```powershell
$url = "https://soarb2b-xxxxx-ew.a.run.app"

***REMOVED*** Health check
Invoke-WebRequest "$url/healthz" -UseBasicParsing

***REMOVED*** Homepage
Invoke-WebRequest "$url/ui/soarb2b_home.html" -UseBasicParsing

***REMOVED*** Root redirect (301)
Invoke-WebRequest "$url/" -MaximumRedirection 0 -ErrorAction SilentlyContinue

***REMOVED*** API test
$headers = @{"X-API-Key" = "your-production-key"}
Invoke-WebRequest -Uri "$url/api/v1/b2b/demo/hotels" -Headers $headers -UseBasicParsing
```

***REMOVED******REMOVED******REMOVED*** Logs

```powershell
gcloud run logs read soarb2b --region europe-west3 --limit 50
gcloud run logs read soarb2b --region europe-west3 --follow
```

***REMOVED******REMOVED******REMOVED*** Service Info

```powershell
gcloud run services describe soarb2b --region europe-west3
```

---

***REMOVED******REMOVED*** 🌍 Region Seçimi

**Mevcut:** `europe-west3` (Frankfurt)

**Türkiye için en iyi seçenekler:**
- `europe-west3` (Frankfurt) - **Önerilen** ✅
- `europe-west1` (Belgium)
- `europe-central2` (Warsaw)

**Region değiştirmek için:**

```powershell
***REMOVED*** deploy_gcp.ps1 içinde REGION değiştir
$REGION = "europe-west1"  ***REMOVED*** veya başka region
```

---

***REMOVED******REMOVED*** 🔐 Custom Domain (Opsiyonel)

***REMOVED******REMOVED******REMOVED*** Cloud Run Domain Mapping

```powershell
gcloud run domain-mappings create `
  --service soarb2b `
  --domain www.soarb2b.com `
  --region europe-west3
```

Script DNS yapılandırma talimatları verecek.

***REMOVED******REMOVED******REMOVED*** DNS Ayarları

Cloud Console'dan verilen CNAME kaydını DNS'e ekle:

```
CNAME: www.soarb2b.com → ghs.googlehosted.com
```

---

***REMOVED******REMOVED*** 💰 Maliyet Tahmini

**Cloud Run (Pay-as-you-go):**
- İlk 2M request: **ÜCRETSİZ** 🎉
- Sonrası: ~$0.40 per 1M requests
- CPU: $0.00002400 per vCPU-second
- Memory: $0.00000250 per GiB-second

**SOAR B2B tahmini aylık maliyet:**
- Hafif kullanım (10K requests): **$0-2/month**
- Orta kullanım (100K requests): **$5-10/month**
- Yoğun kullanım (1M requests): **$40-60/month**

**Free Tier:**
- 2M requests/month ücretsiz
- 360K GiB-seconds memory
- 180K vCPU-seconds compute

---

***REMOVED******REMOVED*** 🐛 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Build Fails

```powershell
***REMOVED*** Build logs
gcloud builds list --limit 5
gcloud builds log BUILD_ID

***REMOVED*** Common issues:
***REMOVED*** - Dockerfile syntax error
***REMOVED*** - Missing requirements.txt
***REMOVED*** - Insufficient permissions
```

***REMOVED******REMOVED******REMOVED*** Service Won't Start

```powershell
***REMOVED*** Service status
gcloud run services describe soarb2b --region europe-west3

***REMOVED*** Logs
gcloud run logs read soarb2b --region europe-west3 --limit 100

***REMOVED*** Common issues:
***REMOVED*** - PORT environment variable not set (should be 8080)
***REMOVED*** - Health check failing
***REMOVED*** - Environment variables missing
```

***REMOVED******REMOVED******REMOVED*** Static Files Not Loading

**Kontrol et:**
1. Dockerfile'da `COPY src/ ./src/` var mı? ✅
2. `src/ui/` klasörü container'da var mı?
3. `app.py`'de static files mount doğru mu?

**Test:**
```powershell
***REMOVED*** Container içinde kontrol (development)
docker build -t soarb2b-test .
docker run --rm -it soarb2b-test ls -la /app/src/ui/
```

***REMOVED******REMOVED******REMOVED*** Port Issues

Cloud Run otomatik olarak `PORT=8080` set eder. Kontrol:

```powershell
gcloud run services describe soarb2b --region europe-west3 --format="value(spec.template.spec.containers[0].ports[0].containerPort)"
```

---

***REMOVED******REMOVED*** 📊 Monitoring

***REMOVED******REMOVED******REMOVED*** Cloud Console

- **Services:** https://console.cloud.google.com/run
- **Logs:** https://console.cloud.google.com/run/detail/europe-west3/soarb2b/logs
- **Metrics:** https://console.cloud.google.com/run/detail/europe-west3/soarb2b/metrics

***REMOVED******REMOVED******REMOVED*** CLI

```powershell
***REMOVED*** Service metrics
gcloud run services describe soarb2b --region europe-west3 --format="value(status.conditions)"

***REMOVED*** Request count
gcloud run services describe soarb2b --region europe-west3 --format="value(status.observedGeneration)"
```

---

***REMOVED******REMOVED*** 🔄 Update Deployment

Değişiklik sonrası yeniden deploy:

```powershell
.\deploy_gcp.ps1
```

Veya manuel:

```powershell
cd backend
gcloud builds submit --tag gcr.io/$env:GCP_PROJECT_ID/soarb2b-v1

gcloud run deploy soarb2b `
  --image gcr.io/$env:GCP_PROJECT_ID/soarb2b-v1 `
  --region europe-west3
```

---

***REMOVED******REMOVED*** 🗑️ Delete Service

```powershell
gcloud run services delete soarb2b --region europe-west3
```

---

***REMOVED******REMOVED*** ✅ Pre-Deployment Checklist

- [ ] gcloud CLI kurulu ve authenticated
- [ ] GCP project set edilmiş
- [ ] Required APIs enabled (run, cloudbuild)
- [ ] `backend/.env` dosyası hazır (production API keys)
- [ ] Dockerfile doğru (src/ kopyalanıyor)
- [ ] PORT 8080 (Cloud Run standardı)
- [ ] Region seçilmiş (europe-west3)

---

**Hazır mısın?** `.\deploy_gcp.ps1` çalıştır! 🚀
