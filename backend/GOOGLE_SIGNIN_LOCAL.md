***REMOVED*** Yerelde Gmail ile giris (Google Client ID)

"Google Client ID not configured in backend response" hatasini gidermek icin backend'de iki ortam degiskeni tanimlanmali.

***REMOVED******REMOVED*** 1. backend/.env dosyasi

`backend` klasorunde `.env` dosyasi olusturun (yoksa):

```powershell
cd "C:\Users\issan\OneDrive\ISMAIL_SANLI\FINDER_OS\backend"
copy .env.example .env
```

Sonra `.env` icinde su satirlari ekleyin veya guncelleyin:

```env
GOOGLE_CLIENT_ID=...client-id....apps.googleusercontent.com
JWT_SECRET=...en-az-32-karakter-rastgele-bir-string...
```

***REMOVED******REMOVED*** 2. Google Client ID alma

1. [Google Cloud Console](https://console.cloud.google.com/) > projenizi secin
2. **APIs & Services** > **Credentials**
3. **Create Credentials** > **OAuth client ID**
4. Application type: **Web application**
5. **Authorized JavaScript origins** icin yerel test:
   - `http://127.0.0.1:9000`
   - `http://127.0.0.1:9001`
   - `http://localhost:9000`
   - `http://localhost:9001`
6. Olusan **Client ID** degerini kopyalayip `.env` icindeki `GOOGLE_CLIENT_ID=` satirina yapistirin.  
   **Not:** Placeholder (ornegin `your-google-client-id`) kullanirsaniz tarayici konsolunda "The given client ID is not found" (GSI_LOGGER) hatasi alirsiniz; mutlaka Google Cloud Console'dan alinan gercek OAuth Client ID kullanin.  
   Sunucu farkli portta calisiyorsa (ornegin 8082), Authorized JavaScript origins'a `http://localhost:8082` ve `http://127.0.0.1:8082` ekleyin.

***REMOVED******REMOVED*** 3. JWT_SECRET (yerel test)

Yerel test icin uzun rastgele bir string yeterli (en az 32 karakter). Ornek uretmek icin PowerShell:

```powershell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }) -as [byte[]])
```

Cikan degeri `.env` icinde `JWT_SECRET=` olarak kullanin.

***REMOVED******REMOVED*** 4. Client ID degistirdiyseniz (eski silinip yeni olusturulduysa)

GCP'de kullandiginiz OAuth client silinip yeni bir tane olusturulduysa:

1. Google Cloud Console > Credentials > yeni **Client ID** degerini kopyalayin (örn. `274308964876-xxxx.apps.googleusercontent.com`).
2. `backend/.env` icinde **GOOGLE_CLIENT_ID** satirini bu yeni degerle degistirin.
3. Backend'i durdurup yeniden baslatin (asagiya bakin).
4. Yerelde farkli port kullaniyorsaniz (8082, 9000 vb.), GCP'de bu client icin **Authorized JavaScript origins** ve **Authorized redirect URIs** listesine `http://127.0.0.1:PORT` ve `http://localhost:PORT` ekleyin.

**"The OAuth client was not found" / Hata 401: invalid_client** goruyorsaniz asagidaki adimlari kontrol edin:

1. **Backend'in dondurdugu Client ID:** Tarayicida `http://127.0.0.1:8082/v1/auth/config` (veya kullandiginiz port) acin. `google_client_id` degerini kopyalayin; **Google Cloud Console > Credentials > OAuth 2.0 Client IDs** icindeki Client ID ile karakter karakter ayni olmali.
2. **.env ve restart:** `backend/.env` icinde `GOOGLE_CLIENT_ID=` bu degerle guncel olmali. Degisiklik yaptiysaniz backend'i mutlaka yeniden baslatin (Ctrl+C sonra `python -m src.main`).
3. **GCP'de client tipi:** OAuth client tipi **"Web application"** olmali (Desktop veya baska tip invalid_client verebilir).
4. **Authorized JavaScript origins:** Kullandiginiz adres orada olmali, ornek: `http://127.0.0.1:8082`, `http://localhost:8082`. Protokol (http/https) ve port ayni olmali.
5. **OAuth consent screen:** "Testing" modundaysa, **Test users** listesine giriş yapacak Gmail adresini ekleyin; yoksa "Access blocked" veya giriş reddedilir. Test user'a geçince sorun çözülür.

***REMOVED******REMOVED*** 5. "Login yapamiyorum" – Kontrol listesi

1. **Sayfayi sunucu uzerinden acin**  
   `http://127.0.0.1:8082/ui/tr/soarb2b_home.html` veya `http://localhost:8082/...`  
   Dosyayi dogrudan (file://) acmayin; API cagrilari calismaz.

2. **Backend ayakta mi?**  
   Tarayicida `http://127.0.0.1:8082/healthz` acin; `{"status":"ok", ...}` donmeli.

3. **Client ID backend’den geliyor mu?**  
   `http://127.0.0.1:8082/v1/auth/config` acin. `google_client_id` gercek bir `...apps.googleusercontent.com` degeri olmali; `your-google-client-id` veya bos ise `backend/.env` icinde `GOOGLE_CLIENT_ID` duzeltip sunucuyu yeniden baslatin.

4. **GCP Authorized JavaScript origins**  
   Kullandiginiz adres (ornegin `http://127.0.0.1:8082` ve `http://localhost:8082`) GCP OAuth client’ta "Yetkilendirilmiş JavaScript kaynaklari" listesinde olmali.

5. **Hata mesajini okuyun**  
   Google ile giris tiklayinca cikan uyari (alert) veya tarayici konsolundaki (F12 > Console) hata mesajini not alin:
   - "Token audience does not match GOOGLE_CLIENT_ID" → Frontend ile backend farkli Client ID kullaniyor; backend’in dondurdugu Client ID ile .env ayni olmali.
   - "Token verification failed" / "Token has expired" → Tekrar "Google ile giris" deneyin; bazen token suresi cok kisadir.
   - "Authentication service is not configured" → .env’de GOOGLE_CLIENT_ID ve JWT_SECRET dolu olmali, sunucu yeniden baslatilmali.
   - Ag hatasi / CORS → Sayfayi sunucu URL’i ile actiginizdan emin olun (file:// degil).

***REMOVED******REMOVED*** 6. Sunucuyu yeniden baslatin

`.env` degistikten sonra uvicorn’u durdurup (Ctrl+C) tekrar baslatin:

```powershell
python -m uvicorn src.app:app --host 127.0.0.1 --port 9000
```

Tarayicida **Sign In** > Gmail butonu artik Client ID ile yuklenecektir.
