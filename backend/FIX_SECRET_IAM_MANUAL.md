***REMOVED*** Secret Manager IAM Fix - Manuel Adımlar

***REMOVED******REMOVED*** 🔴 Problem Analizi

Cloud Run hataları:
- ❌ `Permission denied on secret: google-client-id` → IAM yok
- ❌ `Permission denied on secret: quote-secret` → IAM yok  
- ❌ `Secret jwt-secret was not found` → Secret yok veya isim uyuşmazlığı

***REMOVED******REMOVED*** ✅ KESİN ve TEMİZ FIX

Aşağıdaki adımları **sırayla** uygula:

---

***REMOVED******REMOVED******REMOVED*** 🧹 0️⃣ Önce mevcut başarısız deploy state'i temizle

```bash
gcloud run services update soarb2b \
  --region us-central1 \
  --project finderos-entegrasyon-480708 \
  --clear-secrets
```

**Not:** Bu sadece secret bağlarını temizler, servisi silmez.

---

***REMOVED******REMOVED******REMOVED*** 🔍 1️⃣ Secret'ların GERÇEKTEN var olduğunu doğrula

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

**Eğer biri yoksa:**

***REMOVED******REMOVED******REMOVED******REMOVED*** google-client-id yoksa:
```bash
echo -n "274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com" | \
  gcloud secrets create google-client-id \
    --project finderos-entegrasyon-480708 \
    --replication-policy="automatic" \
    --data-file=-
```

***REMOVED******REMOVED******REMOVED******REMOVED*** jwt-secret yoksa:
```bash
echo -n "$(openssl rand -hex 64)" | \
  gcloud secrets create jwt-secret \
    --project finderos-entegrasyon-480708 \
    --replication-policy="automatic" \
    --data-file=-
```

***REMOVED******REMOVED******REMOVED******REMOVED*** quote-secret yoksa:
```bash
echo -n "$(openssl rand -hex 64)" | \
  gcloud secrets create quote-secret \
    --project finderos-entegrasyon-480708 \
    --replication-policy="automatic" \
    --data-file=-
```

---

***REMOVED******REMOVED******REMOVED*** 🔐 2️⃣ IAM yetkisini ÜÇÜNE DE ver

**⚠️ ÖNEMLİ:** Sadece birine değil, **hepsine** ayrı ayrı vermek şart!

```bash
SA="serviceAccount:soarb2b@finderos-entegrasyon-480708.iam.gserviceaccount.com"

***REMOVED*** google-client-id için
gcloud secrets add-iam-policy-binding google-client-id \
  --project finderos-entegrasyon-480708 \
  --member="$SA" \
  --role="roles/secretmanager.secretAccessor"

***REMOVED*** jwt-secret için
gcloud secrets add-iam-policy-binding jwt-secret \
  --project finderos-entegrasyon-480708 \
  --member="$SA" \
  --role="roles/secretmanager.secretAccessor"

***REMOVED*** quote-secret için
gcloud secrets add-iam-policy-binding quote-secret \
  --project finderos-entegrasyon-480708 \
  --member="$SA" \
  --role="roles/secretmanager.secretAccessor"
```

**Beklenen çıktı (her biri için):**
```
Updated IAM policy for secret [google-client-id].
bindings:
- members:
  - serviceAccount:soarb2b@finderos-entegrasyon-480708.iam.gserviceaccount.com
  role: roles/secretmanager.secretAccessor
```

---

***REMOVED******REMOVED******REMOVED*** 🔎 3️⃣ IAM doğrulaması (opsiyonel ama önerilir)

```bash
***REMOVED*** google-client-id
gcloud secrets get-iam-policy google-client-id \
  --project finderos-entegrasyon-480708

***REMOVED*** jwt-secret
gcloud secrets get-iam-policy jwt-secret \
  --project finderos-entegrasyon-480708

***REMOVED*** quote-secret
gcloud secrets get-iam-policy quote-secret \
  --project finderos-entegrasyon-480708
```

**Her birinde şunu görmelisin:**
```yaml
bindings:
- members:
  - serviceAccount:soarb2b@finderos-entegrasyon-480708.iam.gserviceaccount.com
  role: roles/secretmanager.secretAccessor
```

---

***REMOVED******REMOVED******REMOVED*** 🚀 4️⃣ Cloud Run'ı TEKRAR güncelle (BU SEFER GEÇECEK)

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
- `Permission denied` → Adım 2'yi tekrar kontrol et
- `Secret not found` → Adım 1'de secret'ı oluştur
- `Service account not found` → Service account'ı oluştur:
  ```bash
  gcloud iam service-accounts create soarb2b \
    --project finderos-entegrasyon-480708 \
    --display-name="SOAR B2B Service Account"
  ```

---

***REMOVED******REMOVED******REMOVED*** 🧪 5️⃣ Final doğrulama

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
- Adım 4'ü tekrar çalıştır

---

***REMOVED******REMOVED******REMOVED*** 🧪 6️⃣ Endpoint test

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
| Secret'lar | ✅ oluşturulmuş |
| IAM | ❌ eksikti → **Adım 2 ile düzeliyor** |
| Cloud Run binding | ❌ fail → **Adım 4 ile geçecek** |
| Yaklaşım | ✅ doğru |
| Hata | IAM binding eksikliği |

---

***REMOVED******REMOVED*** 🚀 Otomatik Fix (Script)

Eğer manuel adımları uygulamak istemiyorsan:

```bash
cd backend
bash FIX_SECRET_IAM.sh
```

Bu script tüm adımları otomatik yapar.

---

***REMOVED******REMOVED*** ✅ Sonrasında

Bu fix'ten sonra istersen:

1. **Secret rotation** → `backend/SECRET_ROTATION_SETUP.md`
2. **Staging/prod ayrımı** → Farklı secret'lar
3. **Audit logging** → Cloud Logging'de aktif
4. **Zero-downtime secret rollout** → Version management

---

**Status:** ✅ Adım adım fix hazır
**Next:** Adım 2 → 4'ü aynen yap, sonucu gönder
