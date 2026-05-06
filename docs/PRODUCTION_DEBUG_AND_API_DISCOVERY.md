***REMOVED*** SoarB2B (Finder_OS) — Production Debug & API Discovery Raporu

**Tarih:** 2025-02-21  
**Amaç:** Production erişim sorununu katmanlı debug, API endpoint keşfi, env/konfigürasyon tespiti.

---

***REMOVED******REMOVED*** 1) API Endpoint Haritası

***REMOVED******REMOVED******REMOVED*** 1.1 Uygulama Girişi ve Static

| Method | Path | Dosya | Auth | Dependency |
|--------|------|--------|------|------------|
| GET | `/` | `backend/src/app.py` | Hayır | - |
| GET | `/healthz` | `backend/src/app.py` | Hayır | - |
| GET | `/readyz` | `backend/src/app.py` | Hayır | - |
| GET | `/ui/soarb2b_home.html` | redirect → `/ui/tr/...` | Hayır | - |
| GET | `/ui/soarb2b_onboarding_5q.html` | redirect | Hayır | - |
| GET | `/ui/demo_showcase.html` | redirect | Hayır | - |
| * | `/ui/*` | Static mount | Hayır | `NoCacheStaticFiles(ui_dir)` |

- **Static mount:** `app.mount("/ui", NoCacheStaticFiles(directory=src/ui), name="ui")` — `backend/src/ui` kullanılıyor.
- **Templates:** Repo içinde Jinja/template kullanımı yok.

***REMOVED******REMOVED******REMOVED*** 1.2 v1 Router (prefix: `/v1`)

`router_registry` ile tek `v1_router` (prefix `/v1`) include ediliyor. Aşağıdaki tabloda **tam path** = `/v1` + router prefix + route.

| Method | Path (router prefix + route) | Dosya | Auth | Dependency |
|--------|-----------------------------|--------|------|------------|
| POST | `/v1/sales-page-audit/audit` | sales_page_audit_router | Optional User | get_current_user_from_header, get_db |
| GET | `/v1/sales-page-audit/health` | sales_page_audit_router | Hayır | - |
| GET/POST/DELETE | `/v1/discovery/records`, `.../records/{id}` | discovery_router | User | get_current_user_from_header, get_db |
| GET | `/v1/discovery/health` | discovery_router | Hayır | - |
| POST/GET | `/v1/campaigns/create`, `list`, `{id}/start|stop|stats`, bulk-create | campaign_router | Optional User | get_current_user_from_header, get_db |
| GET/POST | `/v1/subscriptions/*` (plans, current, create, cancel, pricing/*) | subscription_router | Optional User / DB | get_current_user_from_header, get_db |
| POST | `/v1/export/companies`, personnel, combined | export_router | User | get_current_user_from_header, get_db |
| GET | `/v1/export/health` | export_router | Hayır | - |
| POST | `/v1/auth/google`, verify, `/v1/auth/me`, health, config, linkedin, linkedin/callback | auth_router | Bazıları User | get_db, verify_token, get_current_user |
| GET/POST | `/v1/appointments/*` (list, available-slots, cancel, reschedule, {id}) | appointment_router | Optional User | get_current_user_from_header, get_db |
| POST/GET | `/v1/industrial-chain-hunter/*` | industrial_chain_hunter_router | User | get_current_user_dependency, get_db |
| POST/GET | `/v1/webhooks/google-ads/lead-form`, stripe, health | webhooks_router | Webhook secret / DB | get_db |
| GET/POST | `/v1/error-logs/*` | error_log_router | - | get_db |
| GET/POST | `/v1/notifications/*` | notification_router | - | get_db |
| GET | `/v1/invoices/*` | invoice_router | - | get_db |
| GET | `/v1/usage/*` | usage_router | - | get_db |
| POST/GET | `/v1/sniper-b2b/*` | sniper_b2b_router | - | - |
| POST | `/v1/records/preview` | records_router | - | - |
| POST/GET | `/v1/products/*` (read-barcode, create, search-by-image, analyze-vision*) | product_router | - | - |
| GET | `/v1/matching/health`, sample | matching_router | - | - |
| GET/POST | `/v1/growth-activation/*`, `/v1/growth/evaluate` | growth_activation_router / endpoints | - | - |
| GET/POST | `/v1/analytics/health`, events | analytics_router | - | - |
| POST/GET | `/v1/analytics/export-to-bigquery`, sheets, queue-bigquery-export | analytics_export_router | - | - |
| POST/GET | `/v1/research/company-intelligence`, batch-research | company_research_router | - | - |
| GET/POST | `/v1/gpt-companion/guide`, explain, strategy | gpt_companion_router | User | get_current_user_dependency, get_db |
| GET/POST/DELETE | `/v1/users/me/enrichment/*` | enrichment_router | User | get_current_user_dependency, get_db |
| GET/POST | `/v1/marketplace-sellers/*` | marketplace_seller_router | User | get_current_user_dependency, get_db |
| GET/POST | `/v1/targets/{id}/why`, traces (explainer) | explainer_router | User | get_current_user_dependency, get_db |
| GET/POST/DELETE | `/v1/personas/*` (location-affinity, signal-weights, signal-exclusions) | location_affinity_router, persona_signal_router | User | get_current_user_dependency, get_db |
| GET | `/v1/explorer/markets`, companies, persona-archetypes | explorer_router (v1’de de var) | - | - |
| GET/POST | `/v1/usage-billing/*` (pricing, events, usage, trial, ad-spend-comparison) | usage_billing_router | Optional User | get_current_user_from_header, get_db, services |
| POST | `/v1/api/v1/acquisition/jobs`, jobs/{id}, export | acquisition_router (prefix /api/v1/b2b/acquisition) | API Key | validate_api_key, get_db |
| GET/POST | `/v1/api/v1/pricing/*` | pricing_router | - | get_db |

Not: `router_registry` içinde bazı router’ların prefix’i zaten `/v1/...` olduğu için gerçek path’ler **/v1/v1/...** olabilir (örn. `/v1/v1/discovery/records`). Bu tutarsızlık production’da 404 sebebi olabilir; aşağıda “Path tutarlılığı” olarak işaretlendi.

***REMOVED******REMOVED******REMOVED*** 1.3 API v1 (prefix: `/api/v1`, `/api/v1/b2b`, `/api/v1/public`, `/api/chat`, `/api`)

| Method | Tam Path | Dosya | Auth | Dependency |
|--------|----------|--------|------|------------|
| POST | `/api/v1/support/contact` | support_router | - | - |
| POST/GET | `/api/v1/b2b/onboarding/create-plan`, assistant/create-plan, start-run, archive, case-library/*, demo/hotels | b2b_api_router | API Key | validate_api_key, get_db |
| POST/GET | `/api/v1/b2b/plan/objectives`, plan/{id}/timeline, activate | plan_router | API Key | validate_api_key, get_db |
| POST/GET | `/api/v1/admin/*` (plan intervene, admin-action, query-cap-override, plans, uploads, users, support-messages, contact-intakes, approve, replay, suggest) | admin_router | Admin Key | validate_admin_key, get_db |
| GET/POST | `/api/v1/b2b/plan/{id}/preview`, plans/{id}/results, export, exports/{id}/status|download | result_router | API Key | validate_api_key, get_db |
| POST/GET | `/api/v1/b2b/route`, route/{id}/generate-stops, plans/{id}/routes | visit_route_router | API Key | validate_api_key, get_db |
| GET | `/api/v1/explorer/markets`, companies, persona-archetypes | explorer_router | - | - |
| GET/POST | `/api/v1/public/ad-config`, validate-address, onboarding-intake, upload/*, corporate-signup, corporate-login-request | public_router | Hayır (public) | get_db (bazıları) |
| POST/GET | `/api/chat`, `/api/chat/health` | chat_router | - | - |
| POST/GET | `/api/v1/b2b/feasibility/generate`, report/{id}, unlock | feasibility_router | - | get_db |
| POST/GET | `/api/v1/b2b/exposure/create`, track-conversion, conversions/{id} | exposure_router | - | get_db |
| POST/GET | `/api/v1/b2b/reachability/escalation`, enable, status | reachability_router | - | get_db |
| POST | `/api/export/results` | export_results_router | - | get_db |

***REMOVED******REMOVED******REMOVED*** 1.4 WebSocket

- **WebSocket endpoint yok.** Repo içinde `WebSocket` / `websocket` kullanımı bulunmuyor.

***REMOVED******REMOVED******REMOVED*** 1.5 Kullanılmayan / Ayrık Router’lar

- `backend/api/v1/` altındaki router’lar (**b2b_products_router**, **b2b_personas_router**, **b2b_companies_router**, **b2b_mobile_targeting_router**, **b2b_campaigns_router**, **b2b_appointments_router**) **app.py içinde include edilmiyor**. Bu endpoint’ler şu an çalışmıyor (dead code).

---

***REMOVED******REMOVED*** BÖLÜM 3 — Deployment Doğrulama

| Kontrol | Durum | Not |
|--------|--------|-----|
| PM2 ecosystem config | Var | `backend/ecosystem.config.cjs` |
| Uvicorn portu | 8000 | `args: "-m uvicorn src.app:app --host 0.0.0.0 --port 8000"` |
| src import path | Doğru | `src.app:app` — çalışma dizini `backend` olduğu için `src` modülü bulunur |
| cwd | Doğru | `cwd: "/var/www/finder_os/backend"` |
| venv path | Sabit | `script: "/var/www/finder_os/venv/bin/python3"` — sunucu yolu sabit; taşıma durumunda güncellenmeli |
| .env konumu | Repo dışında | `.env` ve `env-vars.yaml` .gitignore’da; production’da `/var/www/finder_os/backend/.env` bekleniyor, app.py `load_dotenv(_backend_dir / ".env")` ile yüklüyor |

**Özet:** PM2 ve port doğru; .env’in sunucuda olması ve cwd’nin `backend` olması kritik. Nginx konfigürasyonu repoda yok (sunucuda ayrı tutuluyor).

---

***REMOVED******REMOVED*** 2) External Dependency Haritası

***REMOVED******REMOVED******REMOVED*** 2.1 Environment Variable Kullanımı (kod tabanı)

| Değişken | Kullanıldığı yer | Varsayılan | Production zorunlu? |
|----------|-------------------|------------|----------------------|
| FINDEROS_VERSION | app.py | "0.1.0" | Hayır |
| BOT_DEFENSE_* | bot_defense.py | çeşitli | Opsiyonel |
| GOOGLE_CLOUD_PROJECT_ID | gemini, secret_manager, bigquery, sheets | - | Gemini/BQ/Sheets için evet |
| GOOGLE_CLOUD_LOCATION | gemini | "us-central1" | Opsiyonel |
| GOOGLE_GEMINI_API_KEY | gemini_analysis_service | - | Gemini kullanımı için evet |
| GOOGLE_PLACES_API_KEY / GOOGLE_MAPS_API_KEY | b2b_api_router, company_discovery, address_validation | - | İlgili özellik için evet |
| STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY | payment_service | - | Ödeme için zorunlu |
| IYZICO_* | payment_service | - | Iyzico kullanımı için zorunlu |
| LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET | auth_router | - | LinkedIn OAuth için zorunlu |
| ENV | auth, security_headers, rate_limit, main, safe_run | "development" | Production’da "production" olmalı |
| RECAPTCHA_SECRET_KEY / GOOGLE_RECAPTCHA_SECRET | captcha | - | Captcha için |
| CAPTCHA_CHALLENGE_SECRET, JWT_SECRET | captcha | JWT fallback | Evet (token üretimi) |
| SOARB2B_API_KEYS | b2b_api_router, admin_router | "" | B2B API + Admin için zorunlu |
| SOARB2B_ADMIN_EMAILS, SOARB2B_ADMIN_KEYS | admin_router | "" | Admin paneli için zorunlu |
| ACONTEXT_* | acontext_client | - | Acontext kullanımı için |
| ADS_*, ADSENSE_* | public_router | - | Reklam için opsiyonel |
| GOOGLE_ADS_WEBHOOK_SECRET, DEFAULT_WEBHOOK_USER_ID | webhooks_router | - | Google Ads webhook için |
| SOAR_ENABLE_STAGEHAND, BROWSERBASE_* | stagehand_adapter | - | Stagehand için opsiyonel |
| GOOGLE_CLIENT_ID, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS | auth_service | - | Auth için zorunlu |
| REDIS_* | rate_limit_redis, cache | redis://localhost:6379/0 | Rate limit/cache için production’da önerilir |
| DATABASE_URL | db_config, db/base | sqlite:///./finderos.db | Production’da PostgreSQL zorunlu |
| DB_POOL_* | db_config | sayısal varsayılanlar | PostgreSQL için önerilir |
| QUOTE_SECRET / JWT_SECRET | quote_token, pricing | - | Quote token için (JWT fallback) |
| OPENAI_API_KEY | chat_router, gpt_companion_service, b2b product/persona | - | Chat/GPT özellikleri için zorunlu |
| GOOGLE_ADS_* (developer token, client, refresh, manager/login id) | google_ads_service | - | Google Ads için |
| GOOGLE_CUSTOM_SEARCH_* | web_research_service | - | Web arama için |
| GOOGLE_SHEETS_* | sheets_service | - | Sheets için |
| SMTP_* | notification_service, appointment_service | - | E-posta için |
| GOOGLE_GEOCODING_API_KEY | geocoding_service | - | Adres/geocoding için |
| GOOGLE_CLIENT_ID/SECRET, GOOGLE_CALENDAR_* | calendar_service | - | Takvim için |
| BIGQUERY_* | bigquery_service | - | BigQuery export için |
| FINDEROS_LIVEBOOK_ENABLED | livebook_endpoints | "false" | Opsiyonel |
| DISABLE_RATE_LIMIT | rate_limiting_middleware | "false" | Opsiyonel |
| FINDEROS_HOST, FINDEROS_PORT, PORT | main, safe_run | 0.0.0.0, 8080/8000 | PM2 port ile uyum (8000) |
| K_SERVICE, SKIP_PORT_CHECK | main | - | Cloud Run / container için |
| FINDEROS_RELOAD, FINDEROS_USE_HTTPS, FINDEROS_SSL_*, FINDEROS_FORCE_HTTPS | main, middleware | false | Opsiyonel |

***REMOVED******REMOVED******REMOVED*** 2.2 Harici API Çağrıları

- **requests:** auth_router (LinkedIn token/user), b2b_api_router (Places), web_research_service (Google Custom Search), sales_page_audit_service, industrial_chain_hunter_service, geocoding_service, company_discovery_service, address_validation_service, scripts.
- **httpx:** Test ve script’lerde (api_key_tier_test, rate_limit_test, observability_audit, load_test).
- **Google:** Maps/Places, Geocoding, Gemini, Ads, Custom Search, Sheets, BigQuery, ReCAPTCHA, OAuth (Client ID/Secret).
- **OpenAI:** Chat, GPT Companion, B2B product/persona/enrichment/industry.
- **Stripe:** Ödeme, webhook.
- **LinkedIn:** OAuth, API (persona_service, persona_enrichment).
- **Acontext:** Observability (API key, URL, encryption).
- **Browserbase/Stagehand:** Web acquisition (opsiyonel).
- **Iyzico:** Ödeme (opsiyonel).

---

***REMOVED******REMOVED*** 3) Eksik Env Var Listesi

***REMOVED******REMOVED******REMOVED*** 3.1 Production’da mutlaka olması gerekenler

- `ENV=production`
- `DATABASE_URL` (PostgreSQL connection string)
- `JWT_SECRET` (ve/veya `QUOTE_SECRET`; yoksa JWT_SECRET kullanılıyor)
- `GOOGLE_CLIENT_ID` (Google OAuth)
- `SOARB2B_API_KEYS` (B2B API erişimi)
- `SOARB2B_ADMIN_EMAILS` ve `SOARB2B_ADMIN_KEYS` (admin işlemleri)
- Stripe kullanılıyorsa: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`

***REMOVED******REMOVED******REMOVED*** 3.2 Özellik bazlı zorunlular

- Chat / GPT: `OPENAI_API_KEY`
- LinkedIn login: `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`
- Google Ads webhook: `GOOGLE_ADS_WEBHOOK_SECRET` (ve gerekirse `DEFAULT_WEBHOOK_USER_ID`)
- Reklam / reCAPTCHA: `RECAPTCHA_SECRET_KEY` veya `GOOGLE_RECAPTCHA_SECRET`
- Rate limit / cache (production): `REDIS_URL` veya `REDIS_HOST` + `REDIS_PORT` + `REDIS_DB`

***REMOVED******REMOVED******REMOVED*** 3.3 env-vars.yaml vs .env

- **env-vars.yaml** repoda `.gitignore`’da; sunucuda ayrı tutuluyor. PM2 **env** bloğu sadece `NODE_ENV` içeriyor; tüm değişkenler **.env** veya sistem env’den gelmeli.
- **app.py** `.env`’i `backend/.env` yolundan yüklüyor (`load_dotenv(_backend_dir / ".env")`). Production’da **/var/www/finder_os/backend/.env** dosyasının var ve okunabilir olması gerekir.

***REMOVED******REMOVED******REMOVED*** 3.4 Eksik / belirsiz olabilecekler

- **QUOTE_SECRET:** `.env.example`’da yok; kod JWT_SECRET’a fallback ediyor. Ayrı quote imzası istiyorsanız ekleyin.
- **FINDEROS_CORS_ORIGINS:** env-vars.yaml’da var; CORS’u sıkılaştırmak için production’da set edilmeli.
- **REDIS_*:** Production’da rate limit ve cache için önerilir; yoksa in-memory/tek process sınırlı kalır.

---

***REMOVED******REMOVED*** 4) En Olası Production Sorunları (öncelik sırası)

1. **Path tutarlılığı (/v1 vs /v1/v1)**  
   `router_registry`’deki birçok router prefix’i zaten `/v1/...`. Bunlar `include_router(v1_router)` ile `/v1` altına alındığı için gerçek path’ler **/v1/v1/discovery/...** gibi olabilir. Frontend veya dokümantasyon `/v1/discovery/...` bekliyorsa 404 alınır.

2. **.env yüklenmemesi**  
   PM2 `ecosystem.config.cjs` ile `python3 -m uvicorn` çalıştırıyor; PM2 kendi başına `.env` okumaz. app.py içinde `load_dotenv(backend/.env)` var; ancak **cwd** veya **çalışma dizini** yanlışsa `.env` bulunamaz. Root’un `/var/www/finder_os` ve cwd’nin `backend` olduğu doğrulanmalı.

3. **DATABASE_URL / Redis**  
   Production’da `DATABASE_URL` PostgreSQL olmalı. Eksik veya yanlışsa DB hataları veya bağlantı zaman aşımı olur. Redis yoksa rate limit paylaşılmaz (çok instance’da tutarsız davranış).

4. **Nginx proxy ve port**  
   Nginx, uygulamayı `127.0.0.1:8000` veya `0.0.0.0:8000`’e yönlendirmeli. ecosystem.config.cjs `--port 8000` kullanıyor; Nginx’te `proxy_pass http://127.0.0.1:8000` (veya uygun upstream) olmalı.

5. **Cloudflare**  
   SSL/TLS modu (Full/Strict), firewall kuralları veya “Under Attack” modu backend’e erişimi engelleyebilir. Gerekirse backend için bypass veya whitelist düşünülmeli.

6. **Admin / API key**  
   `SOARB2B_ADMIN_KEYS` veya `SOARB2B_API_KEYS` boş/yanlışsa admin ve B2B endpoint’leri 401/403 döner.

7. **CORS**  
   `allow_origins=["*"]` şu an geniş; production’da `FINDEROS_CORS_ORIGINS` ile sınırlanması güvenlik ve öngörülebilirlik için iyi olur.

---

***REMOVED******REMOVED*** 5) Hızlı Fix

1. **Health kontrolü (sunucuda)**  
   ```bash
   curl -s http://127.0.0.1:8000/healthz
   curl -s http://127.0.0.1:8000/readyz
   ```  
   Yanıt yoksa uygulama çalışmıyor veya port yanlış.

2. **.env ve cwd**  
   PM2 cwd: `/var/www/finder_os/backend`. Bu dizinde `.env` var mı ve app bu path’ten okuyor mu kontrol et (app.py’deki `_backend_dir` = `Path(__file__).resolve().parent.parent` = backend).  
   Gerekirse PM2’de `env_file` benzeri bir mekanizma kullanılamıyorsa, env’i sistem veya PM2 `env: { ... }` ile vermek (güvenli bir şekilde) düşünülebilir.

3. **Nginx**  
   `proxy_pass http://127.0.0.1:8000;` ve `proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr;` ile test edin. 502/504 ise backend cevap vermiyor veya timeout.

4. **Path 404**  
   İstemci hangi path’e istek atıyor? Örn. `/v1/discovery/records` mı `/v1/v1/discovery/records` mı? OpenAPI: `http://sunucu:8000/docs` veya `http://sunucu:8000/openapi.json` ile gerçek path’leri doğrulayın; gerekirse router prefix’lerini tek `/v1` altında tutarlı hale getirin.

5. **Eksik env**  
   Yukarıdaki “Production’da mutlaka olması gerekenler” listesini sunucudaki `.env` ile karşılaştırın; eksikleri ekleyin ve uygulamayı yeniden başlatın.

---

***REMOVED******REMOVED*** 6) Kalıcı Mimari Önerisi

1. **Tek kaynak path**  
   Tüm API path’lerini tek bir yerde (örn. constants veya OpenAPI’den üretilen client) tanımlayın; router prefix’lerini `/v1` ile çakışmayacak şekilde düzenleyin (ya hep parent’ta `/v1`, ya da child’larda prefix’te `/v1` tekrarlanmasın).

2. **Env schema ve startup check**  
   Pydantic Settings veya benzeri ile env şeması tanımlayın; uygulama ayağa kalkarken zorunlu env’leri kontrol edip eksikte **fail-fast** (başlamadan hata) yapın. Opsiyonel özellikler için “feature flag” env’leri net olsun.

3. **Config dosyası**  
   Hassas olmayan default’lar `config/settings.py` (veya YAML), hassaslar env’de kalsın. `.env` sadece sunucuda; env-vars.yaml dokümantasyon/skeleton olarak kalabilir, gerçek değerler repoya girmesin.

4. **Nginx ve PM2**  
   Nginx konfigürasyonunu repoda (ör. `deploy/nginx.conf.example`) versiyonlayın; tek bir “deploy” dokümanı ile Nginx + PM2 + .env konumu tarif edin. PM2’de `cwd`, `interpreter`, `args` ve gerekirse `env_file` (destekleniyorsa) net yazılsın.

5. **Sağlık ve observability**  
   `/healthz` ve `/readyz`’i DB/Redis bağlantı kontrolü ile genişletin (opsiyonel ama önerilir). Request ID ve log correlation zaten var; log formatını (JSON) ve seviyeyi production’da standartlaştırın.

6. **Dead code**  
   `backend/api/v1/*` router’ları ya app’e include edilip kullanılmalı ya da kaldırılmalı; aksi halde karışıklık ve yanlış “API listesi” algısı oluşur.

---

***REMOVED******REMOVED*** BÖLÜM 4 — Production Debug Stratejisi (Katmanlı)

***REMOVED******REMOVED******REMOVED*** KATMAN 1 — Application (Uvicorn / FastAPI)

| Olası hata | Nasıl test edilir | Nasıl düzeltilir |
|------------|-------------------|-------------------|
| Uygulama başlamıyor | `pm2 logs soarb2b`, `pm2 status` | Import hatası: venv ve `PYTHONPATH`; `cwd` = backend. |
| .env okunmuyor | Log’da env’e bağlı hata (JWT, DB) | `backend/.env` varlığı ve app.py’deki `load_dotenv(_backend_dir / ".env")` path’ini doğrula. |
| Port dinlenmiyor | `ss -tlnp \| grep 8000` (Linux) | ecosystem’de `--port 8000`; başka process 8000’i kullanıyorsa değiştir veya serbest bırak. |
| 404 on known path | `/docs` veya `openapi.json` ile path listesi | Router prefix’leri ve include sırası; /v1/v1 vs /v1 tutarlılığı. |

***REMOVED******REMOVED******REMOVED*** KATMAN 2 — Nginx

| Olası hata | Nasıl test edilir | Nasıl düzeltilir |
|------------|-------------------|-------------------|
| 502 Bad Gateway | Nginx error_log; backend’e doğrudan curl | `proxy_pass` doğru porta (8000); backend ayakta mı kontrol et. |
| 504 Gateway Timeout | Uzun süren istekler | `proxy_read_timeout`, `proxy_connect_timeout` artır; backend’de yavaş endpoint’leri iyileştir. |
| Yanlış Host / path | İstek header’ları ve Nginx location | `proxy_set_header Host $host;`; location’ların `/api`, `/ui`, `/v1` vs. doğru yönlendiğinden emin ol. |
| Static / UI 404 | `/ui/...` isteği | Static’i Nginx’ten sunuyorsanız root/alias; değilse FastAPI mount’un çalıştığını doğrula. |

***REMOVED******REMOVED******REMOVED*** KATMAN 3 — Cloudflare

| Olası hata | Nasıl test edilir | Nasıl düzeltilir |
|------------|-------------------|-------------------|
| Block / challenge | Tarayıcıda 403/1020; curl’de farklı cevap | Firewall kuralları, Security Level, Bot Fight Mode; gerekirse API/health IP whitelist. |
| SSL hatası | Tarayıcı veya `curl -v https://domain` | Cloudflare SSL modu (Full/Strict); origin certificate veya geçerli cert. |
| Cache yanlış davranış | API cevaplarında cache header’ları | Page rules / Cache Rules; API path’lerinde cache bypass. |

***REMOVED******REMOVED******REMOVED*** KATMAN 4 — Firewall

| Olası hata | Nasıl test edilir | Nasıl düzeltilir |
|------------|-------------------|-------------------|
| Dışarıdan porta erişilemiyor | Sunucuda `curl localhost:8000` çalışıyor, dışarıdan çalışmıyor | UFW/iptables: 80/443 açık, 8000 sadece localhost’a açık (Nginx proxy için). |
| DigitalOcean firewall | DO Control Panel → Networking → Firewall | Inbound: 80, 443; gerekirse SSH (22). 8000 inbound’da olmasın. |

---

**Özet:** Production erişim sorununu önce Application (port, .env, path), sonra Nginx (proxy, timeout), sonra Cloudflare (block/SSL), en sonda firewall ile katman katman test etmek; API path’lerini OpenAPI ile sabitlemek ve env’i startup’ta doğrulamak kalıcı çözüm için kritik.
