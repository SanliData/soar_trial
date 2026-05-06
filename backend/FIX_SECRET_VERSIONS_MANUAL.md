***REMOVED*** Secret Version Fix - Manuel Adımlar

***REMOVED******REMOVED*** 🔴 Problem Analizi

Cloud Run hatası:
- ❌ `Secret version not found` → Secret var ama version yok

**Root Cause:** Secret'lar oluşturulmuş ama içlerine data eklenmemiş (version yok).

---

***REMOVED******REMOVED*** ✅ KESİN ve TEMİZ FIX

Aşağıdaki adımları **sırayla** uygula:

---

***REMOVED******REMOVED******REMOVED*** 🔍 1️⃣ Secret'ların gerçekten bu project'te olduğunu doğrula

```bash
gcloud secrets list --project finderos-entegrasyon-480708
```

**Beklenen çıktı:**
```
NAME               CREATED              REPLICATION
google-client-id   2025-01-09T...       AUTOMATIC
jwt-secret         2025-01-09T...       AUTOMATIC
quote-secret       2025-01-09T...       AUTOMATIC
```

**Eğer yoksa:** Yanlış project'te yaratmışsın. Doğru project'te oluştur.

---

***REMOVED******REMOVED******REMOVED*** 🔍 2️⃣ Her secret'ın VERSION'ı var mı?

```bash
***REMOVED*** google-client-id
gcloud secrets versions list google-client-id --project finderos-entegrasyon-480708

***REMOVED*** jwt-secret
gcloud secrets versions list jwt-secret --project finderos-entegrasyon-480708

***REMOVED*** quote-secret
gcloud secrets versions list quote-secret --project finderos-entegrasyon-480708
```

**Beklenen çıktı (her biri için):**
```
NAME                                    STATE    CREATED              DESTROYED
projects/.../secrets/.../versions/1     ENABLED  2025-01-09T...       -
```

**Eğer boş gelirse veya version yoksa:** İşte sorun burada! Adım 3'e geç.

---

***REMOVED******REMOVED******REMOVED*** 🔐 3️⃣ Eğer version YOKSA → ŞİMDİ EKLE (FIX)

**⚠️ ÖNEMLİ:** JWT_SECRET değerini mevcut deployment'tan al. Eğer bilmiyorsan, yeni bir tane oluştur.

***REMOVED******REMOVED******REMOVED******REMOVED*** google-client-id version ekle

```bash
echo -n "274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com" | \
  gcloud secrets versions add google-client-id \
    --project finderos-entegrasyon-480708 \
    --data-file=-
```

**Beklenen çıktı:**
```
Created version [1] of the secret [google-client-id].
```

***REMOVED******REMOVED******REMOVED******REMOVED*** jwt-secret version ekle

**Mevcut JWT_SECRET değerini kullan:**
```bash
echo -n "48f82ac5746559b03d21f57cb57f748d45554d2d12d449e070767cf5613d6e34e7d6b3e3c1b08aaf3cf362b3f36cc66eef9c5aef196419658b38a5140b2414d6" | \
  gcloud secrets versions add jwt-secret \
    --project finderos-entegrasyon-480708 \
    --data-file=-
```

**VEYA yeni bir JWT_SECRET oluştur:**
```bash
echo -n "$(openssl rand -hex 64)" | \
  gcloud secrets versions add jwt-secret \
    --project finderos-entegrasyon-480708 \
    --data-file=-
```

**⚠️ DİKKAT:** Eğer yeni JWT_SECRET oluşturursan, mevcut JWT token'lar geçersiz olur. Kullanıcılar tekrar login olmak zorunda kalır.

***REMOVED******REMOVED******REMOVED******REMOVED*** quote-secret version ekle

```bash
echo -n "$(openssl rand -hex 64)" | \
  gcloud secrets versions add quote-secret \
    --project finderos-entegrasyon-480708 \
    --data-file=-
```

**Beklenen çıktı (her biri için):**
```
Created version [1] of the secret [jwt-secret].
```

---

***REMOVED******REMOVED******REMOVED*** 🔎 4️⃣ Tekrar kontrol

```bash
gcloud secrets versions list google-client-id --project finderos-entegrasyon-480708
gcloud secrets versions list jwt-secret --project finderos-entegrasyon-480708
gcloud secrets versions list quote-secret --project finderos-entegrasyon-480708
```

**Mutlaka görmelisin:**
```
NAME                                    STATE    CREATED
projects/.../secrets/.../versions/1     ENABLED  2025-01-09T...
```

**Her birinde:**
- ✅ `VERSION: 1` (veya daha yüksek)
- ✅ `STATE: ENABLED`

---

***REMOVED******REMOVED******REMOVED*** 🚀 5️⃣ Şimdi tekrar Cloud Run update (bu sefer geçecek)

```bash
gcloud run services update soarb2b \
  --region us-central1 \
  --project finderos-entegrasyon-480708 \
  --service-account soarb2b@finderos-entegrasyon-480708.iam.gserviceaccount.com \
  --set-secrets \
GOOGLE_CLIENT_ID=google-client-id:latest,\
JWT_SECRET=jwt-secret:latest,\
QUOTE_SECRET=quote-secret:latest \
  --remove-env-vars GOOGLE_CLIENT_ID,JWT_SECRET
```

**Beklenen çıktı:**
```
Deploying...
  Creating Revision...done
  Routing traffic...done
Done.
Service [soarb2b] revision [soarb2b-000XX-xxx] has been deployed and is serving 100 percent of traffic.
```

**❌ Hata alırsan:**
- `Permission denied` → IAM binding kontrolü yap (FIX_SECRET_IAM.sh)
- `Secret not found` → Adım 1'de secret'ı kontrol et
- `Version not found` → Adım 3'ü tekrar çalıştır

---

***REMOVED******REMOVED******REMOVED*** 🧪 6️⃣ Final doğrulama

```bash
gcloud run services describe soarb2b \
  --region us-central1 \
  --project finderos-entegrasyon-480708 \
  --format="yaml(spec.template.spec.containers[0].env)"
```

**Beklenen yapı:**
```yaml
env:
- name: GOOGLE_CLIENT_ID
  valueFrom:
    secretKeyRef:
      name: google-client-id
      key: latest
- name: JWT_SECRET
  valueFrom:
    secretKeyRef:
      name: jwt-secret
      key: latest
- name: QUOTE_SECRET
  valueFrom:
    secretKeyRef:
      name: quote-secret
      key: latest
```

**❌ Eğer `value:` görüyorsan (plain text):**
- Secret binding başarısız olmuş
- Adım 5'i tekrar çalıştır

---

***REMOVED******REMOVED******REMOVED*** 🧪 7️⃣ Endpoint test

```bash
curl https://soarb2b-274308964876.us-central1.run.app/v1/auth/config | jq
```

**Beklenen cevap:**
```json
{
  "enabled": true,
  "provider": "google",
  "google_client_id": "274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com",
  "oauth_enabled": true
}
```

**❌ 503 hatası alırsan:**
```bash
***REMOVED*** Logları kontrol et
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=soarb2b" \
  --project finderos-entegrasyon-480708 \
  --limit=20 \
  --format="table(timestamp,severity,textPayload)"
```

---

***REMOVED******REMOVED*** 🎯 NET HÜKÜM

| Konu | Durum |
|------|-------|
| Secret'lar | ✅ var |
| IAM | ✅ doğru |
| Secret versions | ❌ **eksikti** → **Adım 3 ile düzeliyor** |
| Cloud Run binding | ❌ fail → **Adım 5 ile geçecek** |
| Yaklaşım | ✅ doğru |
| Hata | Secret version eksikliği |

---

***REMOVED******REMOVED*** 🚀 Otomatik Fix (Script)

Eğer manuel adımları uygulamak istemiyorsan:

```bash
cd backend
bash FIX_SECRET_VERSIONS.sh
```

Bu script:
1. Secret'ları kontrol eder
2. Version'ları kontrol eder
3. Eksik version'ları ekler
4. Cloud Run'ı günceller
5. Test eder

---

***REMOVED******REMOVED*** ⚠️ ÖNEMLİ NOTLAR

***REMOVED******REMOVED******REMOVED*** JWT_SECRET Rotation

Eğer yeni bir JWT_SECRET oluşturursan:
- Mevcut JWT token'lar geçersiz olur
- Kullanıcılar tekrar login olmak zorunda kalır
- Bu production'da downtime'a sebep olabilir

**Öneri:** Mevcut JWT_SECRET değerini kullan (yukarıdaki değer).

***REMOVED******REMOVED******REMOVED*** Quote Secret

Quote secret yeni oluşturulduğu için, mevcut quote token'lar geçersiz olur. Bu normaldir çünkü:
- Quote token'lar zaten 15 dakika expire oluyor
- Yeni query'ler yeni token alacak
- Etkisi minimal

---

***REMOVED******REMOVED*** ✅ Sonrasında

Bu fix'ten sonra istersen:

1. **Secret rotation** → `backend/SECRET_ROTATION_SETUP.md`
2. **Version management** → `gcloud secrets versions list`
3. **Audit logging** → Cloud Logging'de aktif
4. **Zero-downtime secret rollout** → Version management

---

**Status:** ✅ Version fix hazır
**Next:** Adım 3 → 5'i aynen yap, sonucu gönder
