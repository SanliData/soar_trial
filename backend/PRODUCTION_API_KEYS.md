***REMOVED*** SOAR B2B - Production API Keys

***REMOVED******REMOVED*** ⚠️ GÜVENLİK UYARISI

**BU DOSYA ASLA GITHUB'A COMMIT EDİLMEMELİDİR!**

Production API key'leri sadece:
- Google Cloud Run Environment Variables'da saklanmalı
- Güvenli bir password manager'da saklanmalı
- .gitignore'a eklenmiş olmalı

---

***REMOVED******REMOVED*** Production API Key'leri Oluşturma

***REMOVED******REMOVED******REMOVED*** Yeni Key'ler Oluşturmak İçin:

```powershell
cd backend
python -c "import secrets; keys = [secrets.token_urlsafe(32) for _ in range(3)]; print('SOARB2B_API_KEYS=' + ','.join(keys))"
```

***REMOVED******REMOVED******REMOVED*** Key Format:

- **Format**: Comma-separated values
- **Her key**: 32-byte URL-safe random string (secrets.token_urlsafe)
- **Örnek**: `key1,key2,key3`

---

***REMOVED******REMOVED*** Google Cloud Run Deployment

***REMOVED******REMOVED******REMOVED*** Environment Variable Ayarlama:

```powershell
***REMOVED*** Google Cloud Run service'e environment variable ekle
gcloud run services update soarb2b \
  --region us-central1 \
  --set-env-vars "SOARB2B_API_KEYS=your-key-1,your-key-2,your-key-3"
```

Veya deployment sırasında:

```powershell
gcloud run deploy soarb2b \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "ENV=production,SOARB2B_API_KEYS=key1,key2,key3"
```

---

***REMOVED******REMOVED*** API Key Kullanımı

***REMOVED******REMOVED******REMOVED*** Test Etmek İçin:

```powershell
$headers = @{"X-API-Key" = "your-production-key"}
Invoke-WebRequest https://your-domain.com/api/v1/b2b/demo/hotels -Headers $headers -UseBasicParsing
```

---

***REMOVED******REMOVED*** Key Rotation (Key Değiştirme)

1. Yeni key'ler oluştur
2. Yeni key'leri Cloud Run'a ekle (eski key'lerle birlikte)
3. Client'ları yeni key'e geçir
4. Eski key'leri kaldır

```powershell
***REMOVED*** Yeni key'leri ekle (eski key'lerle birlikte)
gcloud run services update soarb2b \
  --region us-central1 \
  --set-env-vars "SOARB2B_API_KEYS=old-key-1,old-key-2,new-key-1,new-key-2"
  
***REMOVED*** Migration sonrası eski key'leri kaldır
gcloud run services update soarb2b \
  --region us-central1 \
  --set-env-vars "SOARB2B_API_KEYS=new-key-1,new-key-2"
```
