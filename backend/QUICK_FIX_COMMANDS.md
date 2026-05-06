***REMOVED*** Quick Fix Commands - OAuth 503 Error

***REMOVED******REMOVED*** One-Line Setup (After code is deployed)

```bash
***REMOVED*** Setup secrets and deploy
cd backend && \
./scripts/setup_secrets.sh && \
gcloud run deploy soarb2b --source backend --region us-central1 --allow-unauthenticated --env-vars-file backend/env-vars-cloudrun.yaml --service-account finderos-entegrasyon-480708@appspot.gserviceaccount.com --project finderos-entegrasyon-480708
```

***REMOVED******REMOVED*** Step-by-Step

***REMOVED******REMOVED******REMOVED*** 1. Setup Secrets (First Time Only)
```bash
cd backend
chmod +x scripts/setup_secrets.sh
./scripts/setup_secrets.sh
```

***REMOVED******REMOVED******REMOVED*** 2. Deploy
```bash
gcloud run deploy soarb2b \
  --source backend \
  --region us-central1 \
  --allow-unauthenticated \
  --env-vars-file backend/env-vars-cloudrun.yaml \
  --service-account finderos-entegrasyon-480708@appspot.gserviceaccount.com \
  --project finderos-entegrasyon-480708
```

***REMOVED******REMOVED******REMOVED*** 3. Verify
```bash
SERVICE_URL=$(gcloud run services describe soarb2b --region=us-central1 --project=finderos-entegrasyon-480708 --format="value(status.url)")
curl "$SERVICE_URL/v1/auth/config" | jq
```

**Expected:** `"oauth_enabled": true` (not 503 error)

***REMOVED******REMOVED*** What Changed

- ✅ Added Secret Manager integration
- ✅ Automatic fallback to env vars (backward compatible)
- ✅ Production: Secrets from Secret Manager
- ✅ Development: Secrets from .env file

***REMOVED******REMOVED*** Files Modified

- `backend/src/core/secret_manager.py` (NEW)
- `backend/src/services/auth_service.py` (MODIFIED)
- `backend/requirements.txt` (ADDED: google-cloud-secret-manager)
