***REMOVED*** Google OAuth (Sign in with Google) — Production Stabilization

***REMOVED******REMOVED*** 1) Otomatik düzeltilenler

| Madde | Yapılan |
|-------|--------|
| **Redirect URI tutarlılığı** | Hard-coded localhost kaldırıldı. Backend base URL artık `BASE_URL` env’den (production’da) veya `request.base_url` (development). LinkedIn redirect_uri = `_base_url(request) + "/v1/auth/linkedin/callback"`. |
| **BASE_URL validasyonu** | `ENV=production` iken `BASE_URL` zorunlu ve **https** ile başlamalı; değilse startup’ta `ValueError`. |
| **Google env fail-fast** | Production’da `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `JWT_SECRET` zorunlu; eksikse startup’ta hata. |
| **OAuth state & CSRF** | LinkedIn için state HMAC ile imzalanıyor (`_make_signed_state`); callback’te `_verify_signed_state` ile doğrulanıyor (TTL 10 dk). State yok/geçersizse `linkedin_error=6` ile redirect. |
| **Callback hata davranışı** | Token exchange / userinfo hatalarında log’a yazılıyor; kullanıcıya stack trace verilmiyor, sadece generic error redirect. Production’da `authenticate_google` exception’larında `exc_info=False`. |
| **JWT süresi** | Production’da JWT expiration zaten en fazla 24 saat (`auth_service`). |
| **Structured OAuth log** | `_oauth_log(event, ...)` eklendi: `login_start`, `callback_received`, `token_exchanged`, `user_created`, `user_logged_in`, `failure_reason`. INFO seviyesi. |
| **Post-login redirect** | `_frontend_redirect_base(request)` ile redirect URL: önce `FRONTEND_ORIGIN`, yoksa `BASE_URL`, yoksa request’ten türetiliyor. |

---

***REMOVED******REMOVED*** 2) Manuel Google Console ayarları

Aşağıdakiler **Google Cloud Console** üzerinden yapılmalı (kod bunları değiştiremez).

***REMOVED******REMOVED******REMOVED*** 2.1 Credentials (OAuth 2.0 Client ID)

- **Credentials** → İlgili OAuth 2.0 Client ID’yi aç.

**Authorized JavaScript origins**

- Production: `https://soarb2b.com`
- Gerekirse: `https://www.soarb2b.com`
- Geliştirme: `http://localhost:3000` (veya frontend’in çalıştığı origin)

**Authorized redirect URIs**

- Backend callback kullanıyorsanız: `https://soarb2b.com/v1/auth/google/callback`
- Şu an akış **frontend’te id_token alıp POST /v1/auth/google** olduğu için, Google’ın redirect ettiği adres genelde **frontend** sayfasıdır. O zaman:
  - Örnek: `https://soarb2b.com` veya `https://soarb2b.com/` (frontend’in ana sayfası)
  - Geliştirme: `http://localhost:3000` vb.
- Hem backend callback hem frontend kullanacaksanız her iki URI’yi de ekleyin.

***REMOVED******REMOVED******REMOVED*** 2.2 OAuth consent screen

- **OAuth consent screen** → Uygulama “Published” olmalı (Testing’de kalsanız bile production domain’i test kullanıcılarına açık olmalı).
- **Publishing status**: Production’da “In production” yapın; “Testing” ise sadece “Test users” listesindeki hesaplar giriş yapabilir.

***REMOVED******REMOVED******REMOVED*** 2.3 Test users (Testing modundaysa)

- **Test users** listesine production’da giriş yapacak e-posta adreslerini ekleyin.
- Ya da consent screen’i “In production” yapıp test user zorunluluğunu kaldırın.

***REMOVED******REMOVED******REMOVED*** 2.4 Özet checklist

| Adım | Kontrol |
|------|--------|
| Authorized JavaScript origins | `https://soarb2b.com` (ve gerekiyorsa `https://www.soarb2b.com`) eklendi mi? |
| Authorized redirect URIs | Frontend veya backend callback URI’leri (yukarıya göre) eklendi mi? |
| OAuth consent screen | Yayında mı (In production) veya Test users listesi güncel mi? |
| GOOGLE_CLIENT_SECRET | Backend `.env` içinde production’da set mi? |

---

***REMOVED******REMOVED*** 3) Olası production hata senaryoları

| Senaryo | Sebep | Çözüm |
|--------|--------|--------|
| 503 / “Authentication service is not configured” | `GOOGLE_CLIENT_ID` veya `JWT_SECRET` (production’da ayrıca `GOOGLE_CLIENT_SECRET`) eksik. | `.env`’de bu değişkenleri set edin; uygulamayı yeniden başlatın. |
| redirect_uri_mismatch (Google) | Google Console’daki “Authorized redirect URIs” ile istekte giden redirect_uri farklı. | Console’da backend veya frontend redirect URI’yi tam ekleyin (trailing slash, http vs https uyumlu). |
| “invalid_state” / linkedin_error=6 | LinkedIn callback’te state süresi doldu veya imza geçersiz. | Kullanıcıyı tekrar “Sign in with LinkedIn” ile başlatın; sunucu saatinin doğru olduğundan emin olun. |
| CORS hatası (frontend’ten /v1/auth/google) | Frontend origin’i `FINDEROS_CORS_ORIGINS` içinde yok. | Production’da `FINDEROS_CORS_ORIGINS` içine frontend origin’i (örn. `https://soarb2b.com`) ekleyin. |
| Post-login redirect yanlış sayfaya gidiyor | `FRONTEND_ORIGIN` boş; `_frontend_redirect_base` request’ten yanlış türetiyor. | `.env`’de `FRONTEND_ORIGIN=https://soarb2b.com` (veya doğru frontend URL) set edin. |
| id_token verification failed | Client ID uyuşmazlığı veya token süresi dolmuş. | Frontend’in kullandığı Client ID ile backend’deki `GOOGLE_CLIENT_ID` aynı olmalı; kullanıcı tekrar giriş yapsın. |

---

***REMOVED******REMOVED*** CORS & Cookie notu

- Şu an backend **cookie ile oturum taşımıyor**; JWT response body’de (ve LinkedIn’de redirect query’de) dönüyor.
- `allow_credentials=False` (CORS) bu akışla uyumlu.
- İleride cookie kullanırsanız: production’da `Secure=True`, cross-site ise `SameSite=None`; CORS’ta `allow_credentials=True` ve `allow_origins` listesinin wildcard olmaması gerekir.

***REMOVED******REMOVED*** FRONTEND_ORIGIN eşleşmesi

- Post-login redirect `FRONTEND_ORIGIN` veya `BASE_URL` ile yapılıyor.
- `FINDEROS_CORS_ORIGINS` içinde frontend origin’in de olması, API istekleri için gerekli; ayrıca “eşleşme” için `FRONTEND_ORIGIN`’i mümkünse bu origin’lerden biriyle aynı tutun (örn. `https://soarb2b.com`).
