***REMOVED*** Google OAuth Consent Screen – Yeterlilikler (OAuth onay ekranı alanları)

Google Cloud Console > **APIs & Services** > **OAuth consent screen** bölümünde aşağıdaki değerler kullanılmalıdır. Bu sayfa projede mevcuttur; yoksa ekleyin.

---

***REMOVED******REMOVED*** 1. Başvuru ana sayfası bağlantısı (Application homepage link)

```
https://soarb2b-274308964876.us-central1.run.app
```

Alternatif (custom domain kullanılıyorsa):

```
https://soarb2b.com
```

---

***REMOVED******REMOVED*** 2. Uygulama gizlilik politikası bağlantısı (Application privacy policy link)

```
https://soarb2b-274308964876.us-central1.run.app/ui/tr/soarb2b_privacy.html
```

Projede dosya: `backend/src/ui/tr/soarb2b_privacy.html` (ve `en/soarb2b_privacy.html`).

---

***REMOVED******REMOVED*** 3. Başvuru şartları bağlantısı (Application terms and conditions link)

```
https://soarb2b-274308964876.us-central1.run.app/ui/tr/soarb2b_terms.html
```

Projede dosya: `backend/src/ui/tr/soarb2b_terms.html` (ve `en/soarb2b_terms.html`).

---

***REMOVED******REMOVED*** 4. Yetkilendirilmiş alanlar (Authorized domains)

OAuth consent screen’de **Yetkilendirilmiş alanlar** listesinde şunlar olmalı (alan adı olarak, protokol yok):

| Alan adı |
|----------|
| `soarb2b.com` |
| `soarb2b-274308964876.us-central1.run.app` |
| `soarb2b-e4azd3qbdq-uc.a.run.app` |

Not: `www.soarb2b.com` kullanıyorsanız ayrıca ekleyin.

---

***REMOVED******REMOVED*** 5. İletişim e-posta adresleri (Contact email addresses)

Geliştirici / iletişim e-postası (Google Console’da gösterilir):

```
isanli058@gmail.com
```

---

***REMOVED******REMOVED*** Özet tablo

| Alan | Değer |
|------|--------|
| Ana sayfa | `https://soarb2b-274308964876.us-central1.run.app` |
| Gizlilik politikası | `https://soarb2b-274308964876.us-central1.run.app/ui/tr/soarb2b_privacy.html` |
| Hizmet şartları | `https://soarb2b-274308964876.us-central1.run.app/ui/tr/soarb2b_terms.html` |
| Yetkilendirilmiş alanlar | `soarb2b.com`, `soarb2b-274308964876.us-central1.run.app`, `soarb2b-e4azd3qbdq-uc.a.run.app` |
| İletişim e-posta | `isanli058@gmail.com` |

---

***REMOVED******REMOVED*** Projede varlık kontrolü

- **Gizlilik politikası sayfası:** Var → `backend/src/ui/tr/soarb2b_privacy.html`, `backend/src/ui/en/soarb2b_privacy.html`
- **Hizmet şartları sayfası:** Var → `backend/src/ui/tr/soarb2b_terms.html`, `backend/src/ui/en/soarb2b_terms.html`
- **CORS / domain kullanımı:** `app.py` ve `FINDEROS_CORS_ORIGINS` / dokümanlarda `soarb2b.com` ve ilgili Cloud Run URL’leri geçiyor.

Bu yeterlilikler projede mevcuttur; Google Console’da yalnızca yukarıdaki değerlerin girilmesi yeterlidir.

---

***REMOVED******REMOVED*** Testing modunda giriş

OAuth consent screen **"Testing"** modundayken sadece **Test users** listesindeki hesaplar giriş yapabilir. "Access blocked" veya giriş yapamıyorum diyorsanız: Google Cloud Console > OAuth consent screen > **Test users** > **+ ADD USERS** ile giriş yapacak Gmail adresini ekleyin. Test user'a geçince sorun çözülür.
