***REMOVED*** Cloudflare Quick Links

***REMOVED******REMOVED*** 🔗 Direct Links

***REMOVED******REMOVED******REMOVED*** 1. Purge Cache
**Link:** https://dash.cloudflare.com/[YOUR_ACCOUNT_ID]/[ZONE_ID]/caching/configuration/purge-cache

**Steps:**
1. Go to: https://dash.cloudflare.com
2. Select domain: `soarb2b.com`
3. Go to: **Caching** → **Configuration** → **Purge Cache**
4. Select: **Purge Everything**
5. Click **Purge Everything**

***REMOVED******REMOVED******REMOVED*** 2. Cache Rules
**Link:** https://dash.cloudflare.com/[YOUR_ACCOUNT_ID]/[ZONE_ID]/caching/configuration/cache-rules

**Steps:**
1. Go to: https://dash.cloudflare.com
2. Select domain: `soarb2b.com`
3. Go to: **Caching** → **Configuration** → **Cache Rules**
4. Click **Create rule**

**Rule 1:**
- **Rule name:** `Bypass HTML Files`
- **IF:** URI Path ends with `.html` AND URI Path contains `/ui/`
- **THEN:** Cache status = Bypass

**Rule 2:**
- **Rule name:** `Bypass UI Directory`
- **IF:** URI Path starts with `/ui/`
- **THEN:** Cache status = Bypass

***REMOVED******REMOVED******REMOVED*** 3. Speed Optimizations
**Link:** https://dash.cloudflare.com/[YOUR_ACCOUNT_ID]/[ZONE_ID]/speed/optimization

**Steps:**
1. Go to: https://dash.cloudflare.com
2. Select domain: `soarb2b.com`
3. Go to: **Speed** → **Optimization**
4. Disable:
   - **Rocket Loader:** Off
   - **Auto Minify** → **HTML:** Off
   - **APO:** Off (if enabled)

---

***REMOVED******REMOVED*** 📋 Quick Access

**Main Dashboard:**
- https://dash.cloudflare.com

**After selecting domain `soarb2b.com`:**
- **Caching:** https://dash.cloudflare.com → Select domain → Caching
- **Speed:** https://dash.cloudflare.com → Select domain → Speed

---

***REMOVED******REMOVED*** 🔍 Verification

After configuration, verify:
```bash
curl -I https://soarb2b.com/ui/tr/soarb2b_home.html | grep -i "cf-cache-status\|cache-control"
```

**Expected:**
- `cf-cache-status: BYPASS`
- `cache-control: no-store, no-cache, must-revalidate, max-age=0`

---

**Note:** Replace `[YOUR_ACCOUNT_ID]` and `[ZONE_ID]` with your actual Cloudflare account and zone IDs, or navigate through the dashboard.
