***REMOVED*** SOAR B2B — Bot Savunması + Akıllı Upload

***REMOVED******REMOVED*** Özet

- **Bot savunması:** Davranış bazlı risk skoru, sessiz throttle, şüpheli trafikte CAPTCHA isteği (ilk etkileşimde yok).
- **Upload ***REMOVED***1 — LinkedIn:** URL, PDF veya düz metin; kullanıcı verisi, scrape yok.
- **Upload ***REMOVED***2 — Firma hedefi:** Firma adı, domain, Google Maps, CSV; önizleme üretilir, kullanıcı onayı ile devam.
- **Admin:** Kim ne yükledi, ne üretildi, abuse şüphesi — `GET /api/v1/admin/uploads` (X-Admin-Key gerekli).

---

***REMOVED******REMOVED*** 1. Bot savunması

***REMOVED******REMOVED******REMOVED*** Modül

- **`src/security/bot_defense.py`**
  - Sinyaller: çok hızlı form submit, aynı IP’den burst, aynı fingerprint ile seri deneme, headless/automation User-Agent.
  - Savunma: sessiz gecikme (throttle), risk skoru [0,1], `require_captcha` eşiği (varsayılan 0.7).
- **`src/security/captcha.py`**
  - reCAPTCHA v3 (RECAPTCHA_SECRET_KEY / GOOGLE_RECAPTCHA_SECRET) veya self-hosted challenge token (CAPTCHA_CHALLENGE_SECRET).
- **`src/middleware/bot_defense_middleware.py`**
  - Sadece `/api/v1/public` için çalışır; `request.state.bot_risk_score` ve `request.state.require_captcha` set eder.
  - Body okumaz; fingerprint header’lardan.

***REMOVED******REMOVED******REMOVED*** Ortam değişkenleri

- `BOT_DEFENSE_ENABLED` (varsayılan: true)
- `BOT_FORM_SUBMIT_MAX` (varsayılan: 10), `BOT_FORM_SUBMIT_WINDOW_SEC` (60)
- `BOT_SAME_IP_BURST_MAX` (30), `BOT_SAME_IP_BURST_WINDOW_SEC` (60)
- `BOT_RISK_CAPTCHA_THRESHOLD` (0.7), `BOT_SILENT_DELAY_MS` (500)
- CAPTCHA: `RECAPTCHA_SECRET_KEY` veya `GOOGLE_RECAPTCHA_SECRET`; alternatif `CAPTCHA_CHALLENGE_SECRET`

***REMOVED******REMOVED******REMOVED*** Akış

1. Public istek → middleware risk hesaplar, gerekirse sessiz gecikme uygular.
2. Endpoint: `require_captcha` ise ve `X-Captcha-Token` yok/geçersizse → **403** + `{ "require_captcha": true, "message": "...", "message_tr": "..." }`.
3. Frontend: 403 ve `detail.require_captcha` ise `captcha_container` gösterilir; metin: *"Alışılmadık aktivite tespit ettik. Devam etmek için doğrulama yapın."*

---

***REMOVED******REMOVED*** 2. Upload — LinkedIn profil

- **Endpoint:** `POST /api/v1/public/upload/linkedin-profile`
- **Body:** `linkedin_url`, `pdf_base64`, `plain_text` (en az biri zorunlu).
- **Kural:** Sadece kullanıcı tarafından sağlanan veri; SOAR scrape veya özel erişim yapmaz.
- **Çıktı:** `upload_id`, `role`, `seniority`, `department`, `company_match`, `raw_preview`; persona enrichment seed olarak kullanılabilir.

Frontend (onboarding): “Hedef Kişi Yükle” alanı — LinkedIn URL, PDF dosyası, metin yapıştır; açıklama: *"Erişiminiz olan bir LinkedIn profili yükleyebilirsiniz. SOAR özel verilere erişmez veya scrape yapmaz."*

---

***REMOVED******REMOVED*** 3. Upload — Firma hedefi

- **Endpoint:** `POST /api/v1/public/upload/company-target`
- **Body:** `company_name`, `domain`, `google_maps_url`, `csv_text` (en az biri zorunlu).
- **Akış:** Firma doğrulama / normalize → önizleme; kullanıcı “bu verilerle devam et” derse sorgu başlatılır (ayrı akış).

---

***REMOVED******REMOVED*** 4. Upload → orkestrasyon

- Yüklenen veriler doğrudan sorgu başlatmaz; önce **preview** döner.
- Kullanıcı onayı ile devam eden akış (opsiyonel) ileride bağlanabilir.

---

***REMOVED******REMOVED*** 5. Admin görünürlüğü

- **`GET /api/v1/admin/uploads?limit=100&upload_type=linkedin_profile|company_target&abuse_only=true`**
- Header: `X-Admin-Key` (SOARB2B_ADMIN_KEYS ile tanımlı).
- Yanıt: kim (IP), ne (type, payload), preview, `abuse_suspicion`.

Kayıtlar `data/uploads.jsonl` içinde tutulur.

---

***REMOVED******REMOVED*** 6. UX metinleri

- **LinkedIn upload:**  
  *"You can upload a LinkedIn profile you already have access to. SOAR does not scrape or access private data."*  
  TR: *"Erişiminiz olan bir LinkedIn profili yükleyebilirsiniz. SOAR özel verilere erişmez veya scrape yapmaz."*
- **Bot doğrulama:**  
  *"We detected unusual activity. Please verify to continue."*  
  TR: *"Alışılmadık aktivite tespit ettik. Devam etmek için doğrulama yapın."*

---

***REMOVED******REMOVED*** 7. Güvenlik ve uyumluluk

- CAPTCHA: abuse önleme; ilk etkileşimde gösterilmez.
- Upload: kullanıcı kaynaklı veri; scrape yok, credential toplama yok.
- GDPR’a uyumlu pozisyonlama için yukarıdaki metinler kullanılır.
