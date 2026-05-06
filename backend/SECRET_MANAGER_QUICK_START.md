***REMOVED*** Secret Manager Quick Start - Türkçe

***REMOVED******REMOVED*** 🚀 Hızlı Başlangıç

Production hardening için Secret Manager'a geçiş yapmak çok basit:

***REMOVED******REMOVED******REMOVED*** Tek Komut ile Migration

```bash
cd backend
bash SECRET_MANAGER_MIGRATION.sh
```

Bu script otomatik olarak:
1. ✅ Secret Manager API'yi enable eder
2. ✅ Mevcut env var'ları okur
3. ✅ Secret Manager'da secret'ları oluşturur
4. ✅ Service account'a izin verir
5. ✅ Cloud Run'ı günceller
6. ✅ Plain env var'ları kaldırır
7. ✅ Deployment'ı verify eder

***REMOVED******REMOVED******REMOVED*** Manuel Adımlar (Eğer script kullanmak istemiyorsanız)

***REMOVED******REMOVED******REMOVED******REMOVED*** 1. Secret'ları Oluştur

```bash
PROJECT_ID="finderos-entegrasyon-480708"

***REMOVED*** Mevcut değerleri oku
GOOGLE_CLIENT_ID="274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com"
JWT_SECRET=$(gcloud run services describe soarb2b --region=us-central1 --format="value(spec.template.spec.containers[0].env[?(@.name=='JWT_SECRET')].value)")

***REMOVED*** Secret'ları oluştur
echo -n "${GOOGLE_CLIENT_ID}" | gcloud secrets create google-client-id --replication-policy="automatic" --data-file=-
echo -n "${JWT_SECRET}" | gcloud secrets create jwt-secret --replication-policy="automatic" --data-file=-
echo -n "$(openssl rand -hex 64)" | gcloud secrets create quote-secret --replication-policy="automatic" --data-file=-
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 2. Service Account Oluştur ve İzin Ver

```bash
***REMOVED*** Service account oluştur
gcloud iam service-accounts create soarb2b \
  --display-name="SOAR B2B Service Account"

***REMOVED*** Secret'lara erişim izni ver
gcloud secrets add-iam-policy-binding google-client-id \
  --member="serviceAccount:soarb2b@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding jwt-secret \
  --member="serviceAccount:soarb2b@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding quote-secret \
  --member="serviceAccount:soarb2b@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 3. Cloud Run'ı Güncelle

```bash
gcloud run services update soarb2b \
  --region=us-central1 \
  --project=${PROJECT_ID} \
  --service-account=soarb2b@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-secrets="GOOGLE_CLIENT_ID=google-client-id:latest,JWT_SECRET=jwt-secret:latest,QUOTE_SECRET=quote-secret:latest" \
  --remove-env-vars="GOOGLE_CLIENT_ID,JWT_SECRET"
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 4. Verify Et

```bash
SERVICE_URL=$(gcloud run services describe soarb2b --region=us-central1 --format="value(status.url)")
curl "${SERVICE_URL}/v1/auth/config"
```

**Beklenen cevap:**
```json
{
  "enabled": true,
  "provider": "google",
  "google_client_id": "...apps.googleusercontent.com",
  "oauth_enabled": true
}
```

---

***REMOVED******REMOVED*** ✅ Avantajlar

***REMOVED******REMOVED******REMOVED*** Güvenlik
- ✅ Secret'lar artık plain text değil
- ✅ Otomatik encryption at rest
- ✅ Audit logging aktif
- ✅ Version history (rollback mümkün)

***REMOVED******REMOVED******REMOVED*** Yönetim
- ✅ Centralized secret management
- ✅ Otomatik replication (tüm region'lara)
- ✅ Rotation policy eklenebilir
- ✅ Access control (IAM)

***REMOVED******REMOVED******REMOVED*** Compliance
- ✅ Audit trail
- ✅ Secret access logging
- ✅ Version tracking
- ✅ Access monitoring

---

***REMOVED******REMOVED*** 🔄 Rotation (Opsiyonel)

Eğer otomatik rotation istiyorsanız:

```bash
***REMOVED*** Detaylı dokümantasyon için:
cat backend/SECRET_ROTATION_SETUP.md
```

**Basit manuel rotation:**
```bash
***REMOVED*** Yeni secret oluştur
NEW_SECRET=$(openssl rand -hex 64)

***REMOVED*** Yeni versiyon ekle
echo -n "${NEW_SECRET}" | gcloud secrets versions add jwt-secret --data-file=-

***REMOVED*** Cloud Run zaten :latest kullanıyor, otomatik güncellenir
***REMOVED*** Veya force update için:
gcloud run services update soarb2b \
  --region=us-central1 \
  --update-secrets="JWT_SECRET=jwt-secret:latest"
```

---

***REMOVED******REMOVED*** 📊 Monitoring

***REMOVED******REMOVED******REMOVED*** Secret Access Logs

```bash
gcloud logging read 'resource.type=secret' --limit=50
```

***REMOVED******REMOVED******REMOVED*** Secret Versions

```bash
gcloud secrets versions list jwt-secret
```

---

***REMOVED******REMOVED*** 🎯 Sonuç

**Önceki Durum:**
- ❌ Secret'lar plain env var'larda
- ❌ Rotation yok
- ❌ Audit logging yok

**Yeni Durum:**
- ✅ Secret'lar Secret Manager'da
- ✅ Encryption at rest
- ✅ Audit logging aktif
- ✅ Version history
- ✅ Rotation ready

**Security Level:** 🔒 Enterprise-grade

---

**Status:** ✅ Production-ready
**Next:** İstersen rotation policy de kurabiliriz
