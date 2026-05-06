***REMOVED*** UPAP Upload 401 Error - Fix Guide

**Error:** `401 Unauthorized` on `/api/v1/upap/upload`  
**Message:** "User not found. Please sign in again."

---

***REMOVED******REMOVED*** 🔍 Error Analysis

***REMOVED******REMOVED******REMOVED*** Error Details
```
Failed to load resource: 401
Error: Upload failed: 401
{
  "status": "error",
  "error_type": "http_exception",
  "detail": "User not found. Please sign in again.",
  "path": "/api/v1/upap/upload"
}
```

***REMOVED******REMOVED******REMOVED*** Root Cause

**401 = Authentication Failed**

The error "User not found" with status 401 means:
1. ❌ **JWT token is missing** - No `Authorization: Bearer <token>` header sent
2. ❌ **JWT token is invalid** - Token expired, malformed, or signature invalid
3. ❌ **User doesn't exist** - Token is valid but `user_id` not found in database
4. ❌ **User is inactive** - User exists but `is_active=False`

---

***REMOVED******REMOVED*** 🔍 Finding the UPAP Endpoint

**UPAP endpoint NOT FOUND in codebase.** This means:
- Endpoint might be in a different service
- Endpoint might be dynamically registered
- Endpoint might be missing (needs to be created)

**Search commands:**
```bash
***REMOVED*** Find UPAP router
grep -r "upap\|UPAP" backend/src

***REMOVED*** Find upload endpoints
grep -r "/upload\|@router.*upload" backend/src/http

***REMOVED*** Check all router prefixes
grep -r "prefix.*=" backend/src/http/v1/*router*.py
```

---

***REMOVED******REMOVED*** 🔧 Authentication Flow

***REMOVED******REMOVED******REMOVED*** How It Works

1. **User signs in** → Gets JWT token from `/v1/auth/google`
2. **Frontend stores token** → `localStorage` or `sessionStorage`
3. **API requests include token** → `Authorization: Bearer <token>` header
4. **Backend validates** → `get_current_user_dependency` checks token

***REMOVED******REMOVED******REMOVED*** Current User Dependency

**File:** `backend/src/services/auth_service.py` (Line 357-461)

**Error occurs at:**
```python
***REMOVED*** Line 447-453
user = db.query(User).filter(User.id == user_id).first()

if not user:
    raise HTTPException(
        status_code=404,  ***REMOVED*** But returns 401 in practice
        detail="User not found"
    )
```

**Note:** Error says "User not found" but HTTP status is **401** (not 404). This suggests the error is caught and re-raised as 401.

---

***REMOVED******REMOVED*** 🚨 Possible Causes

***REMOVED******REMOVED******REMOVED*** 1. Token Missing (Most Likely)
- Frontend not sending `Authorization` header
- Token not stored in browser
- Token lost after page refresh

***REMOVED******REMOVED******REMOVED*** 2. Token Expired
- JWT token expired
- Need to refresh token or re-authenticate

***REMOVED******REMOVED******REMOVED*** 3. User Deleted
- User was deleted from database
- Token still valid but user_id doesn't exist

***REMOVED******REMOVED******REMOVED*** 4. Database Sync Issue
- User exists in OAuth but not in local database
- Token created but user record not saved

---

***REMOVED******REMOVED*** 🔧 Fix Steps

***REMOVED******REMOVED******REMOVED*** Step 1: Check Frontend Code (upload.html)

**Find the upload function (line 829):**
```javascript
// Check if Authorization header is included
async function uploadRecord(data) {
    const token = localStorage.getItem('auth_token') || 
                  sessionStorage.getItem('auth_token');
    
    if (!token) {
        // Redirect to login
        window.location.href = '/ui/en/soarb2b_home.html***REMOVED***login';
        return;
    }
    
    const response = await fetch('/api/v1/upap/upload', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,  // ← MUST BE PRESENT
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    
    // ...
}
```

***REMOVED******REMOVED******REMOVED*** Step 2: Verify Token Storage

**In browser console (on upload.html page):**
```javascript
// Check if token exists
const token = localStorage.getItem('auth_token') || 
              sessionStorage.getItem('auth_token');
console.log('Token exists:', !!token);
console.log('Token preview:', token ? token.substring(0, 20) + '...' : 'NOT FOUND');
```

***REMOVED******REMOVED******REMOVED*** Step 3: Test Token Manually

**Get token from browser, then test:**
```bash
***REMOVED*** Replace YOUR_TOKEN with actual token
curl -X POST https://soarb2b.com/api/v1/upap/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

**Expected:**
- ✅ `200 OK` = Token is valid
- ❌ `401 Unauthorized` = Token invalid or user not found
- ❌ `404 Not Found` = Endpoint doesn't exist

***REMOVED******REMOVED******REMOVED*** Step 4: Check User in Database

**If token is valid but user not found:**
- User might have been deleted
- Database migration issue
- User creation failed during OAuth

---

***REMOVED******REMOVED*** 🔧 Quick Fixes

***REMOVED******REMOVED******REMOVED*** Fix 1: Ensure Token is Sent

**If token exists but not sent in request:**
```javascript
// In upload.html, ensure token is included
async function uploadRecord(data) {
    // Get token
    const token = localStorage.getItem('auth_token') || 
                  sessionStorage.getItem('auth_token');
    
    if (!token) {
        alert('Please sign in first');
        window.location.href = '/ui/en/soarb2b_home.html***REMOVED***login';
        return;
    }
    
    // Include token in headers
    const response = await fetch('/api/v1/upap/upload', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,  // ← CRITICAL
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    
    if (response.status === 401) {
        // Token expired or invalid - re-authenticate
        localStorage.removeItem('auth_token');
        sessionStorage.removeItem('auth_token');
        window.location.href = '/ui/en/soarb2b_home.html***REMOVED***login';
        return;
    }
    
    // Handle response...
}
```

***REMOVED******REMOVED******REMOVED*** Fix 2: Handle 401 Gracefully

**Add error handling:**
```javascript
try {
    const response = await fetch('/api/v1/upap/upload', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    
    if (response.status === 401) {
        // Clear invalid token
        localStorage.removeItem('auth_token');
        sessionStorage.removeItem('auth_token');
        
        // Redirect to login
        alert('Session expired. Please sign in again.');
        window.location.href = '/ui/en/soarb2b_home.html***REMOVED***login';
        return;
    }
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
    }
    
    const result = await response.json();
    return result;
    
} catch (error) {
    console.error('Upload error:', error);
    alert('Upload failed: ' + error.message);
}
```

***REMOVED******REMOVED******REMOVED*** Fix 3: Check if Endpoint Exists

**If endpoint doesn't exist, create it:**
```python
***REMOVED*** In a new router file: backend/src/http/v1/upap_router.py
from fastapi import APIRouter, HTTPException, Depends
from src.models.user import User
from src.services.auth_service import get_current_user_dependency

router = APIRouter(prefix="/v1/upap", tags=["upap"])

@router.post("/upload")
async def upload_data(
    data: dict,
    user: User = Depends(get_current_user_dependency)
):
    """Upload data - requires authentication"""
    ***REMOVED*** Your upload logic here
    return {"status": "success", "user_id": user.id}
```

---

***REMOVED******REMOVED*** 📋 Debugging Checklist

- [ ] Check if token exists in browser storage
- [ ] Check if `Authorization` header is sent in request
- [ ] Check if token is valid (not expired)
- [ ] Check if user exists in database
- [ ] Check if endpoint `/api/v1/upap/upload` exists
- [ ] Check browser DevTools → Network tab for request headers
- [ ] Check server logs for authentication errors

---

***REMOVED******REMOVED*** 🎯 Next Steps

1. **Find upload.html file** - Check how request is made
2. **Check token storage** - Verify token exists
3. **Test endpoint** - Use curl to test manually
4. **Create endpoint** - If it doesn't exist, create it
5. **Fix frontend** - Ensure token is sent correctly

---

**Status:** 🔍 **ANALYSIS COMPLETE**  
**Action Required:** Find upload.html and check authentication flow
