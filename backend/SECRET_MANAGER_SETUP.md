***REMOVED*** Google Cloud Secret Manager Setup for SOAR B2B

***REMOVED******REMOVED*** Problem
The `/v1/auth/config` endpoint returns 503 because `GOOGLE_CLIENT_ID` and `JWT_SECRET` are not available in the Cloud Run container environment.

***REMOVED******REMOVED*** Solution
Use Google Cloud Secret Manager to securely store and retrieve secrets at runtime, with fallback to environment variables for local development.

***REMOVED******REMOVED*** Implementation

***REMOVED******REMOVED******REMOVED*** 1. Code Changes

**Files Modified:**
- `backend/src/core/secret_manager.py` (NEW) - Secret Manager utility
- `backend/src/services/auth_service.py` - Updated to use Secret Manager
- `backend/requirements.txt` - Added `google-cloud-secret-manager==2.20.0`

**How it works:**
- Production (Cloud Run): Reads secrets from Secret Manager
- Development (local): Falls back to environment variables (`.env` file)
- Automatic detection: Uses `K_SERVICE` env var to detect Cloud Run environment

***REMOVED******REMOVED******REMOVED*** 2. Secret Manager Setup

***REMOVED******REMOVED******REMOVED******REMOVED*** Option A: Using Setup Script (Recommended)

**Linux/Mac:**
```bash
cd backend
chmod +x scripts/setup_secrets.sh
./scripts/setup_secrets.sh
```

**Windows (PowerShell):**
```powershell
cd backend
.\scripts\setup_secrets.ps1
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Option B: Manual Setup

**Step 1: Generate Secure JWT_SECRET**

```bash
***REMOVED*** Generate 64-byte (86 character) secure random secret
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

**Step 2: Create Secrets in Secret Manager**

```bash
PROJECT_ID="finderos-entegrasyon-480708"
GOOGLE_CLIENT_ID="274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com"
JWT_SECRET="<generated-secret-from-step-1>"

***REMOVED*** Create GOOGLE_CLIENT_ID secret
echo -n "$GOOGLE_CLIENT_ID" | gcloud secrets create GOOGLE_CLIENT_ID \
    --project="$PROJECT_ID" \
    --replication-policy="automatic" \
    --data-file=-

***REMOVED*** Create JWT_SECRET secret
echo -n "$JWT_SECRET" | gcloud secrets create JWT_SECRET \
    --project="$PROJECT_ID" \
    --replication-policy="automatic" \
    --data-file=-
```

**Step 3: Grant Cloud Run Service Account Access**

```bash
PROJECT_ID="finderos-entegrasyon-480708"
SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"

***REMOVED*** Grant access to secrets
gcloud secrets add-iam-policy-binding GOOGLE_CLIENT_ID \
    --project="$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding JWT_SECRET \
    --project="$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"
```

***REMOVED******REMOVED******REMOVED*** 3. Update Cloud Run Deployment

**Update `env-vars-cloudrun.yaml`:**

```yaml
ENV: "production"
GOOGLE_CLOUD_PROJECT_ID: "finderos-entegrasyon-480708"
***REMOVED*** Remove GOOGLE_CLIENT_ID and JWT_SECRET from here - they're now in Secret Manager
```

**Deploy Command:**

```bash
gcloud run deploy soarb2b \
  --source backend \
  --region us-central1 \
  --allow-unauthenticated \
  --env-vars-file backend/env-vars-cloudrun.yaml \
  --service-account "${PROJECT_ID}@appspot.gserviceaccount.com"
```

***REMOVED******REMOVED******REMOVED*** 4. Verify Setup

**Test Secret Access:**
```bash
***REMOVED*** Verify secrets are accessible
gcloud secrets versions access latest --secret=GOOGLE_CLIENT_ID --project="finderos-entegrasyon-480708"
gcloud secrets versions access latest --secret=JWT_SECRET --project="finderos-entegrasyon-480708"
```

**Test API Endpoint:**
```bash
***REMOVED*** Should return 200 with oauth_enabled: true
curl https://your-cloud-run-url/v1/auth/config
```

Expected response:
```json
{
  "enabled": true,
  "provider": "google",
  "google_client_id": "274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com",
  "oauth_enabled": true
}
```

***REMOVED******REMOVED*** Security Best Practices

***REMOVED******REMOVED******REMOVED*** JWT_SECRET Requirements
- **Minimum length:** 64 bytes (86 characters in base64)
- **Generation:** Use cryptographically secure random generator
- **Storage:** Never commit to git, always use Secret Manager in production
- **Rotation:** Rotate every 90 days or after security incidents

***REMOVED******REMOVED******REMOVED*** Secret Rotation Strategy

**1. Create New Secret Version:**
```bash
***REMOVED*** Generate new JWT_SECRET
NEW_JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

***REMOVED*** Add new version
echo -n "$NEW_JWT_SECRET" | gcloud secrets versions add JWT_SECRET \
    --project="$PROJECT_ID" \
    --data-file=-
```

**2. Update Application:**
- The code automatically uses `latest` version
- No code changes needed for rotation
- Old tokens will become invalid (by design)

**3. Verify:**
```bash
***REMOVED*** Test that new secret is being used
curl https://your-cloud-run-url/v1/auth/config
```

***REMOVED******REMOVED******REMOVED*** Access Control

**Principle of Least Privilege:**
- Only grant `roles/secretmanager.secretAccessor` to Cloud Run service account
- Never grant `roles/secretmanager.admin` to service accounts
- Use IAM conditions for time-based access if needed

***REMOVED******REMOVED*** Local Development

For local development, continue using `.env` file:

```env
GOOGLE_CLIENT_ID=274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com
JWT_SECRET=your-local-dev-secret
GOOGLE_CLOUD_PROJECT_ID=finderos-entegrasyon-480708
```

The code automatically falls back to environment variables when not running in Cloud Run.

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Issue: 503 Error Still Occurring

**Check:**
1. Secrets exist in Secret Manager:
   ```bash
   gcloud secrets list --project="finderos-entegrasyon-480708"
   ```

2. Service account has access:
   ```bash
   gcloud secrets get-iam-policy GOOGLE_CLIENT_ID --project="finderos-entegrasyon-480708"
   ```

3. GOOGLE_CLOUD_PROJECT_ID is set in Cloud Run:
   ```bash
   gcloud run services describe soarb2b --region=us-central1 --format="value(spec.template.spec.containers[0].env)"
   ```

4. Check Cloud Run logs:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=soarb2b" --limit=50
   ```

***REMOVED******REMOVED******REMOVED*** Issue: ImportError for secretmanager

**Solution:** Ensure `google-cloud-secret-manager==2.20.0` is in `requirements.txt` and rebuild Docker image.

***REMOVED******REMOVED******REMOVED*** Issue: Permission Denied

**Solution:** Grant Secret Manager access:
```bash
gcloud projects add-iam-policy-binding finderos-entegrasyon-480708 \
    --member="serviceAccount:finderos-entegrasyon-480708@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

***REMOVED******REMOVED*** Migration Checklist

- [x] Create Secret Manager utility (`secret_manager.py`)
- [x] Update `auth_service.py` to use Secret Manager
- [x] Add `google-cloud-secret-manager` to requirements.txt
- [ ] Create secrets in Secret Manager
- [ ] Grant service account access
- [ ] Update `env-vars-cloudrun.yaml` (remove secrets)
- [ ] Deploy to Cloud Run
- [ ] Verify `/v1/auth/config` returns 200
- [ ] Test OAuth flow end-to-end
- [ ] Document rotation procedure

***REMOVED******REMOVED*** Rollback Plan

If issues occur, you can temporarily rollback by:

1. Add secrets back to `env-vars-cloudrun.yaml`:
   ```yaml
   GOOGLE_CLIENT_ID: "274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com"
   JWT_SECRET: "ex7eB25gFLQ1AP9_WlRL6381EXdHlQLYFVhGuFyuS6o"
   ```

2. Redeploy:
   ```bash
   gcloud run deploy soarb2b --source backend --region us-central1 --env-vars-file backend/env-vars-cloudrun.yaml
   ```

The code will automatically use environment variables if Secret Manager fails.
