***REMOVED*** Google Sign-In "OAuth client was not found" (401 invalid_client) Düzeltmesi

Sayfa **http://127.0.0.1:8000** (veya farklı port) üzerinde açıldığında Google bu origin'e izin vermediği için hata verir. Aşağıdaki adımlar GCP tarafında gerekli.

***REMOVED******REMOVED*** 1. Google Cloud Console

1. [Google Cloud Console](https://console.cloud.google.com/) → projenizi seçin.
2. **APIs & Services** → **Credentials**.
3. **OAuth 2.0 Client IDs** bölümünde, uygulamanızda kullandığınız client'ı bulun (`.env` içindeki `GOOGLE_CLIENT_ID` ile aynı olan; örn. **Web client 3** – `274308964876-sspd...`).
4. Bu client'ın satırındaki **kalem (Edit)** ikonuna tıklayın.

***REMOVED******REMOVED*** 2. Authorized JavaScript origins

**Authorized JavaScript origins** alanına, uygulamanızın çalıştığı adresleri **tam olarak** ekleyin:

- `http://127.0.0.1:8000`
- `http://localhost:8000`

Port farklıysa (ör. 9000) onu da ekleyin:

- `http://127.0.0.1:9000`
- `http://localhost:9000`

- Sonunda **slash (/) olmamalı**: `http://127.0.0.1:8000` ✓, `http://127.0.0.1:8000/` ✓ (Google genelde ikisini de kabul eder ama origin olarak slashsız yazmak yeterli).
- **http** kullanıyorsanız `https` yazmayın; tam adres tarayıcı çubuğundaki ile aynı olmalı.

***REMOVED******REMOVED*** 3. Authorized redirect URIs (isteğe bağlı)

Bazı akışlar için redirect URI de istenir. Aynı client'ta **Authorized redirect URIs** bölümüne şunları ekleyebilirsiniz:

- `http://127.0.0.1:8000/`
- `http://localhost:8000/`

(Port 9000 kullanıyorsanız: `http://127.0.0.1:9000/`, `http://localhost:9000/`.)

***REMOVED******REMOVED*** 4. Kaydet ve tekrar dene

- **Save** ile kaydedin.
- Birkaç dakika bekleyin (bazen birkaç saniye yeterli).
- Tarayıcıda sayfayı **yenileyip** tekrar "Google ile oturum açın" deneyin.

***REMOVED******REMOVED*** Kontrol listesi

- [ ] GCP Credentials’da doğru OAuth 2.0 Client ID düzenlendi (GOOGLE_CLIENT_ID ile aynı).
- [ ] **Authorized JavaScript origins**’e `http://127.0.0.1:8000` ve kullandığınız diğer origin’ler eklendi.
- [ ] Port farklıysa (ör. 9000) o port için de origin eklendi.
- [ ] Kaydedildi ve birkaç dakika geçti.
- [ ] Sayfa yenilendi, tekrar giriş denendi.

Hata sürerse: Tarayıcıda tam açık olan adres (protocol + host + port) ile GCP’de yazdığınız origin’in **birebir aynı** olduğundan emin olun.
