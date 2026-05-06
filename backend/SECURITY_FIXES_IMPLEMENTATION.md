***REMOVED*** Security Fixes - Implementation Plan

***REMOVED******REMOVED*** 🔴 CRITICAL FIXES REQUIRED

***REMOVED******REMOVED******REMOVED*** Fix 1: Remove Localhost API Calls

**Files to Fix:**
1. `backend/src/ui/soarb2b_onboarding_5q.html` - 6 instances (lines 989, 997, 1031, 1037, 1045, 1053)
2. `backend/src/ui/en/soarb2b_home.html` - 6 instances (lines 2854, 3072, 3080, 3095, 3108, 3119)
3. `backend/src/ui/soarb2b_home.html` - Check for similar instances
4. All language variants: `ar/`, `de/`, `es/`, `fr/`, `it/`, `tr/`

**Pattern to Remove:**
```javascript
// ***REMOVED***region agent log
fetch('http://127.0.0.1:7243/ingest/be4f401c-3c97-493b-8d38-8ef6be20a376',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...})}).catch(()=>{});
// ***REMOVED***endregion
```

**Action:** Remove entire blocks (including comments)

---

***REMOVED******REMOVED******REMOVED*** Fix 2: OAuth 403 - Google Console Configuration

**Action Required (Manual - Google Cloud Console):**

1. Go to: https://console.cloud.google.com/apis/credentials?project=finderos-entegrasyon-480708
2. Find OAuth 2.0 Client ID: `274308964876-sspd7hojmr70jplqh2hb9vk9gpt5d9a2`
3. Click "Edit"
4. Under "Authorized JavaScript origins", add:
   - `https://soarb2b-274308964876.us-central1.run.app`
5. Under "Authorized redirect URIs", add:
   - `https://soarb2b-274308964876.us-central1.run.app/v1/auth/google/callback`
6. Save

**No Code Changes Needed**

---

***REMOVED******REMOVED******REMOVED*** Fix 3: Complete UI Cleanup

**Actions:**
1. Remove old subscription loading code from `soarb2b_home.html`
2. Verify all language variants have usage-based pricing
3. Ensure no "unlimited" language remains

---

***REMOVED******REMOVED*** Implementation Order

1. **Fix 1** - Remove localhost calls (all files)
2. **Fix 2** - Update Google Console (manual)
3. **Fix 3** - UI cleanup (if needed)

---

**Status:** Ready to implement  
**Architecture Gate:** ✅ Approved (no security downgrade)
