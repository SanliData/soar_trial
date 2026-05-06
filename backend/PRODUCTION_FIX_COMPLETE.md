***REMOVED*** Production Fix: OAuth 503 Error - Complete Solution

***REMOVED******REMOVED*** Root Cause Analysis

**Current Error:**
```json
{
  "error": "Authentication service is not configured",
  "detail": "Please set GOOGLE_CLIENT_ID and JWT_SECRET in backend .env file",
  "google_client_id": null,
  "oauth_enabled": false
}
```

**Root Causes Identified:**

1. **Secret Manager secrets not created** - Code tries Secret Manager first, fails silently, falls back to env vars
2. **Service account lacks permissions** - Cloud Run service account doesn't have `secretmanager.secretAccessor` role
3. **Env vars file path mismatch** - You mentioned `/home/isanli058/env-vars.yaml` but code uses `backend/env-vars-cloudrun.yaml`
4. **Code not deployed** - Latest Secret Manager integration may not be in deployed image

***REMOVED******REMOVED*** Immediate Fix (Choose One)

***REMOVED******REMOVED******REMOVED*** Option A: Quick Fix - Use Env Vars (Temporary)

**Deploy with env vars directly:**

```bash
gcloud run deploy soarb2b \
  --source backend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "ENV=production,GOOGLE_CLOUD_PROJECT_ID=finderos-entegrasyon-480708,GOOGLE_CLIENT_ID=274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com,JWT_SECRET=ex7eB25gFLQ1AP9_WlRL6381EXdHlQLYFVhGuFyuS6o" \
  --service-account finderos-entegrasyon-480708@appspot.gserviceaccount.com \
  --project finderos-entegrasyon-480708
```

**Verify:**
```bash
SERVICE_URL=$(gcloud run services describe soarb2b --region=us-central1 --project=finderos-entegrasyon-480708 --format="value(status.url)")
curl "$SERVICE_URL/v1/auth/config" | jq
```

***REMOVED******REMOVED******REMOVED*** Option B: Production Fix - Secret Manager (Recommended)

**Step 1: Create Secrets in Secret Manager**

```bash
PROJECT_ID="finderos-entegrasyon-480708"

***REMOVED*** Generate secure JWT_SECRET (64 bytes = 86 chars)
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

***REMOVED*** Grant Cloud Run service account access
SERVICE_ACCOUNT="finderos-entegrasyon-480708@appspot.gserviceaccount.com"

gcloud secrets add-iam-policy-binding GOOGLE_CLIENT_ID \
  --project="$PROJECT_ID" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding JWT_SECRET \
  --project="$PROJECT_ID" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

**Step 2: Verify Secrets Exist**

```bash
***REMOVED*** List secrets
gcloud secrets list --project="finderos-entegrasyon-480708"

***REMOVED*** Verify access (should show values)
gcloud secrets versions access latest --secret=GOOGLE_CLIENT_ID --project="finderos-entegrasyon-480708"
gcloud secrets versions access latest --secret=JWT_SECRET --project="finderos-entegrasyon-480708"
```

**Step 3: Deploy with Correct Env Vars File**

```bash
***REMOVED*** If env-vars.yaml is at /home/isanli058/env-vars.yaml
gcloud run deploy soarb2b \
  --source backend \
  --region us-central1 \
  --allow-unauthenticated \
  --env-vars-file /home/isanli058/env-vars.yaml \
  --service-account finderos-entegrasyon-480708@appspot.gserviceaccount.com \
  --project finderos-entegrasyon-480708

***REMOVED*** OR if using backend/env-vars-cloudrun.yaml
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

**Step 4: Verify Deployment**

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

***REMOVED******REMOVED*** Complete Deployment Command (Copy/Paste Ready)

```bash
***REMOVED***!/bin/bash
***REMOVED*** Complete production deployment with Secret Manager

PROJECT_ID="finderos-entegrasyon-480708"
REGION="us-central1"
SERVICE_NAME="soarb2b"
SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"

***REMOVED*** Step 1: Create secrets (if not exists)
echo "Creating secrets in Secret Manager..."
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

***REMOVED*** Create GOOGLE_CLIENT_ID
echo -n "274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com" | \
  gcloud secrets create GOOGLE_CLIENT_ID \
    --project="$PROJECT_ID" \
    --replication-policy="automatic" \
    --data-file=- 2>/dev/null || echo "GOOGLE_CLIENT_ID already exists"

***REMOVED*** Create JWT_SECRET
echo -n "$JWT_SECRET" | \
  gcloud secrets create JWT_SECRET \
    --project="$PROJECT_ID" \
    --replication-policy="automatic" \
    --data-file=- 2>/dev/null || echo "JWT_SECRET already exists"

***REMOVED*** Step 2: Grant permissions
echo "Granting service account access..."
gcloud secrets add-iam-policy-binding GOOGLE_CLIENT_ID \
  --project="$PROJECT_ID" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor" 2>/dev/null || true

gcloud secrets add-iam-policy-binding JWT_SECRET \
  --project="$PROJECT_ID" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor" 2>/dev/null || true

***REMOVED*** Step 3: Deploy
echo "Deploying service..."
gcloud run deploy "$SERVICE_NAME" \
  --source backend \
  --region "$REGION" \
  --allow-unauthenticated \
  --env-vars-file backend/env-vars-cloudrun.yaml \
  --service-account "$SERVICE_ACCOUNT" \
  --project "$PROJECT_ID"

***REMOVED*** Step 4: Verify
echo "Verifying deployment..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format="value(status.url)")

echo "Service URL: $SERVICE_URL"
echo ""
echo "Testing /v1/auth/config:"
curl -s "$SERVICE_URL/v1/auth/config" | jq
```

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Issue: Still Getting 503

**Check 1: Secrets exist?**
```bash
gcloud secrets list --project="finderos-entegrasyon-480708"
```

**Check 2: Service account has access?**
```bash
gcloud secrets get-iam-policy GOOGLE_CLIENT_ID --project="finderos-entegrasyon-480708"
```

**Check 3: GOOGLE_CLOUD_PROJECT_ID set?**
```bash
gcloud run services describe soarb2b \
  --region=us-central1 \
  --project=finderos-entegrasyon-480708 \
  --format="value(spec.template.spec.containers[0].env)" | grep GOOGLE_CLOUD_PROJECT_ID
```

**Check 4: Cloud Run logs**
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=soarb2b" \
  --limit=50 \
  --project=finderos-entegrasyon-480708 \
  --format=json | jq '.[] | select(.textPayload | contains("Secret Manager") or contains("GOOGLE_CLIENT_ID") or contains("JWT_SECRET"))'
```

***REMOVED******REMOVED******REMOVED*** Issue: Permission Denied

```bash
PROJECT_ID="finderos-entegrasyon-480708"
SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"

***REMOVED*** Grant at project level
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

***REMOVED******REMOVED******REMOVED*** Issue: ImportError for secretmanager

**Solution:** Rebuild Docker image (requirements.txt has google-cloud-secret-manager)
```bash
gcloud run deploy soarb2b \
  --source backend \
  --region us-central1 \
  --project finderos-entegrasyon-480708
```

***REMOVED******REMOVED*** Validation Checklist

- [ ] Secrets created in Secret Manager
  ```bash
  gcloud secrets list --project=finderos-entegrasyon-480708 | grep -E "GOOGLE_CLIENT_ID|JWT_SECRET"
  ```

- [ ] Service account has access
  ```bash
  gcloud secrets get-iam-policy GOOGLE_CLIENT_ID --project=finderos-entegrasyon-480708 | grep secretAccessor
  ```

- [ ] GOOGLE_CLOUD_PROJECT_ID in env vars
  ```bash
  gcloud run services describe soarb2b --region=us-central1 --project=finderos-entegrasyon-480708 --format="value(spec.template.spec.containers[0].env)" | grep GOOGLE_CLOUD_PROJECT_ID
  ```

- [ ] Code deployed with latest changes
  ```bash
  gcloud run services describe soarb2b --region=us-central1 --project=finderos-entegrasyon-480708 --format="value(status.latestReadyRevisionName)"
  ```

- [ ] Endpoint returns 200 (not 503)
  ```bash
  SERVICE_URL=$(gcloud run services describe soarb2b --region=us-central1 --project=finderos-entegrasyon-480708 --format="value(status.url)")
  curl -s "$SERVICE_URL/v1/auth/config" | jq '.oauth_enabled'
  ***REMOVED*** Should output: true
  ```

- [ ] OAuth flow works end-to-end
  - Test Google Sign-In button
  - Verify JWT token generation
  - Check user creation/retrieval

***REMOVED******REMOVED*** File Paths Reference

- **Backend source:** `backend/` (relative to repo root)
- **Env vars file (repo):** `backend/env-vars-cloudrun.yaml`
- **Env vars file (server):** `/home/isanli058/env-vars.yaml` (if different)
- **Entrypoint:** `backend/entrypoint.sh`
- **Dockerfile:** `backend/dockerfile`
- **Secret Manager code:** `backend/src/core/secret_manager.py`
- **Auth service:** `backend/src/services/auth_service.py`

***REMOVED******REMOVED*** Expected Final State

**Before Fix:**
- ❌ 503 Service Unavailable
- ❌ `oauth_enabled: false`
- ❌ `google_client_id: null`

**After Fix:**
- ✅ 200 OK
- ✅ `oauth_enabled: true`
- ✅ `google_client_id: "274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2.apps.googleusercontent.com"`
- ✅ OAuth flow functional

***REMOVED******REMOVED*** Security Notes

- **JWT_SECRET:** Must be >= 64 bytes (86 chars in base64)
- **Storage:** Secrets in Secret Manager (encrypted at rest)
- **Access:** Only Cloud Run service account
- **Rotation:** Update secret version, code uses `latest` automatically
