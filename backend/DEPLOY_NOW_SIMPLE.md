***REMOVED*** 🚀 Cloud Run Deploy - Hızlı Komut

***REMOVED******REMOVED*** Tek Komut ile Deploy

**PowerShell:**
```powershell
gcloud run deploy soarb2b `
  --source backend `
  --region us-central1 `
  --project finderos-entegrasyon-480708 `
  --service-account soarb2b@finderos-entegrasyon-480708.iam.gserviceaccount.com `
  --set-secrets="GOOGLE_CLIENT_ID=google-client-id:latest,JWT_SECRET=jwt-secret:latest,QUOTE_SECRET=quote-secret:latest" `
  --allow-unauthenticated
```

**Bash/Cloud Shell:**
```bash
gcloud run deploy soarb2b \
  --source backend \
  --region us-central1 \
  --project finderos-entegrasyon-480708 \
  --service-account soarb2b@finderos-entegrasyon-480708.iam.gserviceaccount.com \
  --set-secrets="GOOGLE_CLIENT_ID=google-client-id:latest,JWT_SECRET=jwt-secret:latest,QUOTE_SECRET=quote-secret:latest" \
  --allow-unauthenticated
```

***REMOVED******REMOVED*** ✅ Beklenen Çıktı

```
Deploying...
  Building Container...
  Uploading sources...
  Deploying container...
  Creating Revision...done
  Routing traffic...done
Done.
Service [soarb2b] revision [soarb2b-000XX-xxx] has been deployed and is serving 100 percent of traffic.
Service URL: https://soarb2b-274308964876.us-central1.run.app
```

***REMOVED******REMOVED*** 🧪 Test

```bash
curl https://soarb2b-274308964876.us-central1.run.app/v1/auth/config | jq
```

**Beklenen:**
```json
{
  "enabled": true,
  "provider": "google",
  "google_client_id": "...apps.googleusercontent.com",
  "oauth_enabled": true
}
```

***REMOVED******REMOVED*** 📋 Deploy Edilen Özellikler

- ✅ Usage-based pricing model
- ✅ Quote token enforcement (HMAC-signed)
- ✅ Secret Manager integration
- ✅ Max 100 results enforcement
- ✅ Cost preview before query execution
- ✅ Single source of truth for pricing

---

**Status:** ✅ Ready to deploy
**Note:** Git push yapmadan da deploy edebilirsin, Cloud Run direkt backend klasöründen build ediyor.
