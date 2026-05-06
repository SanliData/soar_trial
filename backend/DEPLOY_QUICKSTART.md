***REMOVED*** SOAR B2B - Hızlı Deployment Başlangıç

***REMOVED******REMOVED*** 1. Production API Keys (Hazır!)

Aşağıdaki key'leri kullanabilirsiniz:

```
qO1-m6mDLNOPPMZXhZlDrE_noP8PLYcvjzVKUrZoG_k
quNu1D4bpCVhgZndJ7CfNE8rGhVq1b2Kyz3Ujd6qUPU
wbprNQ5WXsTDB7PbyPK0tUye3bHrGryWjMqlVFDU4nk
```

***REMOVED******REMOVED*** 2. .env Dosyası Oluştur

`backend` klasöründe `.env` dosyası oluşturun (veya mevcut dosyaya ekleyin):

```env
ENV=production
PORT=8000
SOARB2B_API_KEYS=qO1-m6mDLNOPPMZXhZlDrE_noP8PLYcvjzVKUrZoG_k,quNu1D4bpCVhgZndJ7CfNE8rGhVq1b2Kyz3Ujd6qUPU,wbprNQ5WXsTDB7PbyPK0tUye3bHrGryWjMqlVFDU4nk
FINDEROS_CORS_ORIGINS=https://soarb2b.com,https://www.soarb2b.com
FINDEROS_CORS_ALLOW_ALL=false
FINDEROS_HOST=0.0.0.0
FINDEROS_PORT=8000
```

***REMOVED******REMOVED*** 3. Deployment Komutu (Tek Komut)

***REMOVED******REMOVED******REMOVED*** Windows PowerShell:

```powershell
cd backend
.\DEPLOY_SIMPLE.ps1
```

Veya manuel:

```powershell
cd backend
docker-compose up -d --build
```

***REMOVED******REMOVED*** 4. Verification

```powershell
***REMOVED*** Health check
Invoke-WebRequest http://127.0.0.1:8000/healthz -UseBasicParsing

***REMOVED*** Homepage
Start-Process "http://127.0.0.1:8000/ui/soarb2b_home.html"

***REMOVED*** Logs
docker-compose logs -f
```

***REMOVED******REMOVED*** 5. Production Domain Bağlama (Sonra)

Domain hazır olduğunda:
1. DNS A record: soarb2b.com → YOUR_SERVER_IP
2. DNS A record: www.soarb2b.com → YOUR_SERVER_IP
3. Nginx reverse proxy kurulumu (DEPLOY_TO_SOARB2B_COM.md'ye bakın)
4. SSL sertifikası (Let's Encrypt)

---

**ŞİMDİ NE YAPMALI?**

1. `backend/.env` dosyasını oluştur (yukarıdaki içerik ile)
2. `cd backend`
3. `.\DEPLOY_SIMPLE.ps1` çalıştır
4. Test: http://127.0.0.1:8000/ui/soarb2b_home.html

Hepsi bu kadar!
