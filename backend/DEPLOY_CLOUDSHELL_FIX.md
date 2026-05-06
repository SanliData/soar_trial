***REMOVED*** Cloud Shell Deploy Fix

***REMOVED******REMOVED*** 🔴 Problem

**Error:**
```
ERROR: (gcloud.run.deploy) could not find source [backend]
```

**Root Cause:** Cloud Shell'de `backend` klasörü mevcut dizinde değil.

---

***REMOVED******REMOVED*** ✅ Solution

**1. Find backend directory:**
```bash
***REMOVED*** Check current directory
pwd

***REMOVED*** Find backend folder
find ~ -name "backend" -type d 2>/dev/null | grep -i finder
```

**2. Navigate to correct directory:**
```bash
***REMOVED*** If backend is in Finder_os/backend
cd ~/Finder_os
***REMOVED*** OR
cd ~/FINDER_OS

***REMOVED*** Verify backend exists
ls -la backend/
```

**3. Deploy from correct location:**

**Option A: Deploy from project root (if backend/ exists):**
```bash
cd ~/Finder_os  ***REMOVED*** or ~/FINDER_OS
gcloud run deploy soarb2b \
  --source backend \
  --region us-central1 \
  --project finderos-entegrasyon-480708 \
  --service-account soarb2b@finderos-entegrasyon-480708.iam.gserviceaccount.com \
  --set-secrets="GOOGLE_CLIENT_ID=google-client-id:latest,JWT_SECRET=jwt-secret:latest,QUOTE_SECRET=quote-secret:latest" \
  --allow-unauthenticated
```

**Option B: Deploy with absolute path:**
```bash
gcloud run deploy soarb2b \
  --source ~/Finder_os/backend \
  --region us-central1 \
  --project finderos-entegrasyon-480708 \
  --service-account soarb2b@finderos-entegrasyon-480708.iam.gserviceaccount.com \
  --set-secrets="GOOGLE_CLIENT_ID=google-client-id:latest,JWT_SECRET=jwt-secret:latest,QUOTE_SECRET=quote-secret:latest" \
  --allow-unauthenticated
```

---

***REMOVED******REMOVED*** 🔍 Quick Check Commands

```bash
***REMOVED*** 1. Find backend
find ~ -name "backend" -type d 2>/dev/null

***REMOVED*** 2. Check if Dockerfile exists
find ~ -name "Dockerfile" -path "*/backend/*" 2>/dev/null

***REMOVED*** 3. Check current directory structure
pwd
ls -la
```

---

**Status:** ⚠️ **PATH ISSUE**  
**Next:** Find backend directory + Deploy from correct location
