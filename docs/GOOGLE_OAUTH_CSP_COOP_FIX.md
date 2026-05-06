***REMOVED*** Google OAuth – CSP ve COOP Düzeltmeleri (Teknik Rapor Özeti)

***REMOVED******REMOVED*** Konsol Hataları

1. **CSP:** `Framing 'https://accounts.google.com/' violates... frame-ancestors 'self'`  
   → Google kendi sayfasının iframe içinde açılmasına izin vermiyor; login iframe ile açılmamalı.

2. **COOP:** `Cross-Origin-Opener-Policy policy would block the window.postMessage call`  
   → Popup ile ana sayfa arasında postMessage için COOP/COEP uyumlu olmalı.

***REMOVED******REMOVED*** Yapılan Backend Düzeltmeleri

**Dosya:** `backend/src/middleware/security_headers_middleware.py` (production only)

| Ayar | Değer | Açıklama |
|------|--------|----------|
| **CSP** | `frame-ancestors 'self'` eklendi | Sadece kendi origin’imiz sayfalarımızı frame’leyebilir. |
| **CSP** | `frame-src https://accounts.google.com` | Gerekirse Google’ı açmak için (popup akışında iframe kullanılmıyor). |
| **COOP** | `same-origin-allow-popups` | Popup ile ana pencere arasında postMessage çalışır. |
| **COEP** | `unsafe-none` | Embedder policy postMessage’ı engellemez. |

Google login **iframe içinde açılmamalı**; GSI `ux_mode: "popup"` ile zaten popup pencerede açılıyor (tüm ilgili UI dosyalarında ayarlı).

***REMOVED******REMOVED*** Google Console Kontrol Listesi

- **Authorized JavaScript origins:** `https://soarb2b.com`, `https://www.soarb2b.com`
- **Authorized redirect URIs:** Backend callback URL’iniz (ör. `https://soarb2b.com/v1/auth/callback` veya kullandığınız path)

***REMOVED******REMOVED*** Test

1. Google ile giriş butonuna tıkla → popup açılmalı (iframe değil).
2. Popup’ta Google giriş ekranı görünmeli.
3. Giriş sonrası token ana sayfaya postMessage ile gelmeli, COOP/COEP hatası olmamalı.
4. Kullanıcı oturum açmış şekilde ana sayfada kalmalı.

***REMOVED******REMOVED*** Referans

Rapor: *SOAR B2B Teknik Rapor — Google OAuth Entegrasyon Hatası Analizi*  
Uygulama: CSP + COOP + COEP middleware; GSI `ux_mode: "popup"` (önceden yapıldı).
