***REMOVED*** Fix OAuth 503 Error - Immediate Action Required

***REMOVED******REMOVED*** Current Problem

**Endpoint:** `GET /v1/auth/config`  
**Status:** 503 Service Unavailable  
**Response:**
```json
{
  "error": "Authentication service is not configured",
  "detail": "Please set GOOGLE_CLIENT_ID and JWT_SECRET in backend .env file",
  "google_client_id": null,
  "oauth_enabled": false
}
```

***REMOVED******REMOVED*** Root Cause

1. **Secret Manager secrets don't exist** - Code tries Secret Manager, fails, falls back to env vars
2. **Env vars not loaded** - Either file path wrong or vars not injected into container
3. **Service account lacks permissions** - Can't read from Secret Manager

***REMOVED******REMOVED*** Immediate Fix (Choose One)

***REMOVED******REMOVED******REMOVED*** Option 1: Quick Fix - Use Script (Recommended)

```bash
cd backend
chmod +x DEPLOY_FIX_NOW.sh
./DEPLOY_FIX_NOW.sh
```

This script:
- Creates secrets in Secret Manager
- Grants service account access
- Deploys with correct configuration
- Verifies the fix

***REMOVED******REMOVED******REMOVED*** Option 2: Manual Fix - Step by Step

***REMOVED******REMOVED******REMOVED******REMOVED*** Step 1: Create Secrets

```bash
PROJECT_ID="finderos-entegrasyon-480708"
SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"

***REMOVED*** Generate secure JWT_SECRET
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

***REMOVED*** Create GOOGLE_CLIENT_ID secret
echo -n "274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com" | \
  gcloud secrets create GOOGLE_CLIENT_ID \
    --project="$PROJECT_ID" \
    --replication-policy="automatic" \
    --data-file=-

***REMOVED*** Create JWT_SECRET secret
echo -n "$JWT_SECRET" | \
  gcloud secrets create JWT_SECRET \
    --project="$PROJECT_ID" \
    --replication-policy="automatic" \
    --data-file=-

***REMOVED*** Grant access
gcloud secrets add-iam-policy-binding GOOGLE_CLIENT_ID \
  --project="$PROJECT_ID" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding JWT_SECRET \
  --project="$PROJECT_ID" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Step 2: Deploy

**If env file is at `/home/isanli058/env-vars.yaml`:**
```bash
gcloud run deploy soarb2b \
  --source backend \
  --region us-central1 \
  --allow-unauthenticated \
  --env-vars-file /home/isanli058/env-vars.yaml \
  --service-account finderos-entegrasyon-480708@appspot.gserviceaccount.com \
  --project finderos-entegrasyon-480708
```

**If env file is at `backend/env-vars-cloudrun.yaml`:**
```bash
gcloud run deploy soarb2b \
  --source backend \
  --region us-central1 \
  --allow-unauthenticated \
  --env-vars-file backend/env-vars-cloudrun.yaml \
  --service-account finderos-entegrasyon-480708@appspot.gserviceaccount.com \
  --project finderos-entegrasyon-480708
```

**Critical:** Ensure `GOOGLE_CLOUD_PROJECT_ID` is in your env-vars file:
```yaml
GOOGLE_CLOUD_PROJECT_ID: "finderos-entegrasyon-480708"
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Step 3: Verify

```bash
***REMOVED*** Get service URL
SERVICE_URL=$(gcloud run services describe soarb2b \
  --region=us-central1 \
  --project=finderos-entegrasyon-480708 \
  --format="value(status.url)")

***REMOVED*** Test endpoint
curl "$SERVICE_URL/v1/auth/config" | jq
```

**Expected Response (200 OK):**
```json
{
  "enabled": true,
  "provider": "google",
  "google_client_id": "274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com",
  "oauth_enabled": true
}
```

***REMOVED******REMOVED******REMOVED*** Option 3: Emergency Fallback - Inline Env Vars

If Secret Manager setup fails, use inline env vars temporarily:

```bash
gcloud run deploy soarb2b \
  --source backend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "ENV=production,GOOGLE_CLOUD_PROJECT_ID=finderos-entegrasyon-480708,GOOGLE_CLIENT_ID=274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com,JWT_SECRET=ex7eB25gFLQ1AP9_WlRL6381EXdHlQLYFVhGuFyuS6o" \
  --service-account finderos-entegrasyon-480708@appspot.gserviceaccount.com \
  --project finderos-entegrasyon-480708
```

**⚠️ WARNING:** This exposes secrets in deployment command. Use only for emergency.

***REMOVED******REMOVED*** Verification Checklist

Run these commands to verify the fix:

```bash
***REMOVED*** 1. Check secrets exist
gcloud secrets list --project=finderos-entegrasyon-480708 | grep -E "GOOGLE_CLIENT_ID|JWT_SECRET"

***REMOVED*** 2. Check service account access
gcloud secrets get-iam-policy GOOGLE_CLIENT_ID --project=finderos-entegrasyon-480708 | grep secretAccessor

***REMOVED*** 3. Check GOOGLE_CLOUD_PROJECT_ID is set
gcloud run services describe soarb2b \
  --region=us-central1 \
  --project=finderos-entegrasyon-480708 \
  --format="value(spec.template.spec.containers[0].env)" | grep GOOGLE_CLOUD_PROJECT_ID

***REMOVED*** 4. Test endpoint
SERVICE_URL=$(gcloud run services describe soarb2b --region=us-central1 --project=finderos-entegrasyon-480708 --format="value(status.url)")
curl -s "$SERVICE_URL/v1/auth/config" | jq '.oauth_enabled'
***REMOVED*** Should output: true
```

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Still Getting 503?

**Check Cloud Run logs:**
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=soarb2b" \
  --limit=50 \
  --project=finderos-entegrasyon-480708 \
  --format=json | jq '.[] | select(.textPayload | contains("Secret Manager") or contains("GOOGLE_CLIENT_ID") or contains("JWT_SECRET") or contains("error") or contains("Error"))'
```

**Common issues:**
1. **Secrets don't exist** → Run Step 1 above
2. **No permissions** → Run `gcloud secrets add-iam-policy-binding` commands
3. **GOOGLE_CLOUD_PROJECT_ID missing** → Add to env-vars file
4. **Code not deployed** → Run deploy command again

***REMOVED******REMOVED******REMOVED*** Permission Denied?

```bash
PROJECT_ID="finderos-entegrasyon-480708"
SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

***REMOVED******REMOVED*** File Locations

- **Backend source:** `backend/` (relative to repo root)
- **Env vars (repo):** `backend/env-vars-cloudrun.yaml`
- **Env vars (server):** `/home/isanli058/env-vars.yaml`
- **Fix script:** `backend/DEPLOY_FIX_NOW.sh`
- **Entrypoint:** `backend/entrypoint.sh`
- **Dockerfile:** `backend/dockerfile`

***REMOVED******REMOVED*** Expected Result

**Before:**
```json
{
  "error": "Authentication service is not configured",
  "detail": "Please set GOOGLE_CLIENT_ID and JWT_SECRET in backend .env file",
  "google_client_id": null,
  "oauth_enabled": false
}
```

**After:**
```json
{
  "enabled": true,
  "provider": "google",
  "google_client_id": "274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com",
  "oauth_enabled": true
}
```

***REMOVED******REMOVED*** Security Notes

- **JWT_SECRET:** Must be >= 64 bytes (86 chars). Script generates secure random.
- **Storage:** Secrets stored in Secret Manager (encrypted at rest).
- **Access:** Only Cloud Run service account can read.
- **Rotation:** Update secret version, code uses `latest` automatically.

---

**Status:** Ready to deploy  
**Time to fix:** ~5 minutes  
**Risk:** Low (backward compatible, graceful fallback)
