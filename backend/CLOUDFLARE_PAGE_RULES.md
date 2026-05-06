***REMOVED*** Cloudflare Page Rules - Manual Configuration

***REMOVED******REMOVED*** 🎯 Required Page Rules

***REMOVED******REMOVED******REMOVED*** Rule 1: Bypass Cache for HTML Files

**URL Pattern:**
```
*soarb2b.com/ui/*.html
```

**Settings:**
- **Cache Level:** Bypass
- **Browser Cache TTL:** Respect Existing Headers
- **Edge Cache TTL:** Bypass
- **Cache Deception Armor:** On

---

***REMOVED******REMOVED******REMOVED*** Rule 2: Bypass Cache for UI Directory

**URL Pattern:**
```
*soarb2b.com/ui/*
```

**Settings:**
- **Cache Level:** Bypass
- **Browser Cache TTL:** Bypass
- **Edge Cache TTL:** Bypass

---

***REMOVED******REMOVED*** 📋 Step-by-Step Configuration

***REMOVED******REMOVED******REMOVED*** 1. Access Cloudflare Dashboard

1. Go to: https://dash.cloudflare.com
2. Select domain: `soarb2b.com`
3. Go to: **Rules** → **Page Rules**

***REMOVED******REMOVED******REMOVED*** 2. Create Rule 1

1. Click **Create Page Rule**
2. **URL Pattern:** `*soarb2b.com/ui/*.html`
3. **Settings:**
   - Add setting: **Cache Level** → **Bypass**
   - Add setting: **Browser Cache TTL** → **Respect Existing Headers**
   - Add setting: **Edge Cache TTL** → **Bypass**
4. Click **Save and Deploy**

***REMOVED******REMOVED******REMOVED*** 3. Create Rule 2

1. Click **Create Page Rule**
2. **URL Pattern:** `*soarb2b.com/ui/*`
3. **Settings:**
   - Add setting: **Cache Level** → **Bypass**
   - Add setting: **Browser Cache TTL** → **Bypass**
   - Add setting: **Edge Cache TTL** → **Bypass**
4. Click **Save and Deploy**

---

***REMOVED******REMOVED*** ⚙️ Additional Cloudflare Settings

***REMOVED******REMOVED******REMOVED*** Disable Rocket Loader

1. Go to: **Speed** → **Optimization** → **Rocket Loader**
2. Set: **Off**
3. Click **Save**

***REMOVED******REMOVED******REMOVED*** Disable HTML Minification

1. Go to: **Speed** → **Optimization** → **Auto Minify**
2. **HTML:** **Off**
3. Click **Save**

***REMOVED******REMOVED******REMOVED*** Disable APO (if enabled)

1. Go to: **Speed** → **Optimization** → **APO**
2. Set: **Off** (or exclude `/ui/*.html`)
3. Click **Save**

---

***REMOVED******REMOVED*** 🔍 Verification

After configuration, verify:

```bash
***REMOVED*** Check cache status
curl -I https://soarb2b.com/ui/tr/soarb2b_onboarding_5q.html | grep -i "cf-cache-status"

***REMOVED*** Expected: cf-cache-status: BYPASS
```

---

**Status:** ⚠️ **MANUAL CONFIGURATION REQUIRED**  
**Location:** Cloudflare Dashboard
