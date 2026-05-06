***REMOVED*** Cloudflare Cache Rules – Doğru Yapılandırma

***REMOVED******REMOVED*** Önemli

Cloudflare’da önbellek ayarları artık **Page Rules** ile değil, **Cache Rules** ile yapılıyor. Aşağıdaki adımlar **Cache Rules** kullanımına göredir.

---

***REMOVED******REMOVED*** Adım adım yapılandırma

***REMOVED******REMOVED******REMOVED*** 1. Cloudflare paneline giriş

1. https://dash.cloudflare.com adresine gidin.
2. `soarb2b.com` alan adını seçin.
3. **Caching** → **Configuration** → **Cache Rules** bölümüne gidin.

***REMOVED******REMOVED******REMOVED*** 2. Kural 1: HTML dosyalarını önbelleğe alma (Bypass)

**Kural adı:** `Bypass HTML Files`

**IF (Eşleşme):**
- **Field:** URI Path  
- **Operator:** ends with  
- **Value:** `.html`  

**AND**

- **Field:** URI Path  
- **Operator:** contains  
- **Value:** `/ui/`  

**THEN:**
- **Cache status:** Bypass  

**Save and Deploy** ile kaydedin.

---

***REMOVED******REMOVED******REMOVED*** 3. Kural 2: /ui/ dizinini önbelleğe alma (Bypass)

**Kural adı:** `Bypass UI Directory`

**IF (Eşleşme):**
- **Field:** URI Path  
- **Operator:** starts with  
- **Value:** `/ui/`  

**THEN:**
- **Cache status:** Bypass  

**Save and Deploy** ile kaydedin.

---

***REMOVED******REMOVED*** Ek Cloudflare ayarları

***REMOVED******REMOVED******REMOVED*** Rocket Loader

1. **Speed** → **Optimization** → **Rocket Loader**
2. **Off** yapın → **Save**

***REMOVED******REMOVED******REMOVED*** HTML minification

1. **Speed** → **Optimization** → **Auto Minify**
2. **HTML:** **Off** → **Save**

***REMOVED******REMOVED******REMOVED*** APO (varsa)

1. **Speed** → **Optimization** → **APO**
2. **Off** yapın (veya `/ui/*.html` hariç tutun) → **Save**

---

***REMOVED******REMOVED*** Doğrulama

Yapılandırmadan sonra:

```bash
curl -I https://soarb2b.com/ui/tr/soarb2b_onboarding_5q.html | grep -i "cf-cache-status"
```

Beklenen: `cf-cache-status: BYPASS`  
Bu header Cloudflare edge tarafından set edilir; origin sunucu değil.

---

***REMOVED******REMOVED*** Önce önbelleği temizleyin

Kuralları eklemeden **önce** önbelleği tamamen temizleyin:

1. **Caching** → **Configuration** → **Purge Cache**
2. **Purge Everything** seçin → **Purge Everything**

Eski edge önbelleği, kurallar eklense bile eski içeriği sunmaya devam edebilir.

---

**Durum:** Manuel yapılandırma gerekli  
**Yer:** Cloudflare Dashboard → Caching → Cache Rules
