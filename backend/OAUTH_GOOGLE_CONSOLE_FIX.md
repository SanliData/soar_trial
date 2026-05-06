***REMOVED*** OAuth 403 Fix - Google Cloud Console Configuration

***REMOVED******REMOVED*** 🔴 Problem

**Error:** `[GSI_LOGGER]: origin not allowed for client ID`  
**HTTP Status:** 403  
**Trigger:** Google Sign-in button click

***REMOVED******REMOVED*** ✅ Root Cause

Google Cloud Console OAuth client configuration is missing the Cloud Run URL in "Authorized JavaScript origins" and "Authorized redirect URIs".

***REMOVED******REMOVED*** 🔧 Fix Steps

***REMOVED******REMOVED******REMOVED*** Step 1: Access Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/credentials?project=finderos-entegrasyon-480708
2. Or navigate: **APIs & Services** > **Credentials**

***REMOVED******REMOVED******REMOVED*** Step 2: Find OAuth Client

1. Look for OAuth 2.0 Client ID: `274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2`
2. Click the **pencil icon** (Edit) next to it

***REMOVED******REMOVED******REMOVED*** Step 3: Add Authorized JavaScript Origins

Under **"Authorized JavaScript origins"**, click **"+ ADD URI"** and add:

```
https://soarb2b-274308964876.us-central1.run.app
```

**Important:**
- ✅ Must be HTTPS
- ✅ No trailing slash
- ✅ Exact match with Cloud Run URL

***REMOVED******REMOVED******REMOVED*** Step 4: Add Authorized Redirect URIs

Under **"Authorized redirect URIs"**, click **"+ ADD URI"** and add:

```
https://soarb2b-274308964876.us-central1.run.app/v1/auth/google/callback
```

**Important:**
- ✅ Must be HTTPS
- ✅ Exact path: `/v1/auth/google/callback`
- ✅ Must match backend route

***REMOVED******REMOVED******REMOVED*** Step 5: Save

Click **"SAVE"** at the bottom of the page.

***REMOVED******REMOVED******REMOVED*** Step 6: Wait for Propagation

Google OAuth changes can take **1-5 minutes** to propagate.

***REMOVED******REMOVED******REMOVED*** Step 7: Test

1. Go to: https://soarb2b-274308964876.us-central1.run.app
2. Click "Sign In" button
3. Click Google Sign-in button
4. Should redirect to Google OAuth (no 403 error)

---

***REMOVED******REMOVED*** ✅ Expected Result

After fix:
- ✅ No 403 error on Google Sign-in button click
- ✅ Redirects to Google OAuth consent screen
- ✅ After consent, redirects back to app with token

---

***REMOVED******REMOVED*** 🔍 Verification

**Check Current Configuration:**
```bash
***REMOVED*** View OAuth client (requires gcloud)
gcloud alpha iap oauth-clients list \
  --project=finderos-entegrasyon-480708
```

**Or check in Console:**
- Go to Credentials page
- Click on OAuth client
- Verify URLs are listed

---

***REMOVED******REMOVED*** ⚠️ Common Mistakes

1. **HTTP vs HTTPS:** Must use `https://` not `http://`
2. **Trailing Slash:** Don't add trailing slash to origin
3. **Port Number:** Cloud Run URLs don't include port numbers
4. **Path in Origins:** Origins should NOT include paths (only domain)
5. **Path in Redirects:** Redirects MUST include full path

---

**Status:** ⚠️ **MANUAL ACTION REQUIRED**  
**No Code Changes Needed** - This is a Google Console configuration issue
