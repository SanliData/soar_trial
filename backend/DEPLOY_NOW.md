***REMOVED*** SOAR B2B - Hemen Deployment Adımları

***REMOVED******REMOVED*** Ön Hazırlık (5 Dakika)

***REMOVED******REMOVED******REMOVED*** 1. Production API Keys Oluştur

```powershell
cd backend
python -c "import secrets; keys = [secrets.token_urlsafe(32) for _ in range(3)]; print('Keys:'); [print(f'  {k}') for k in keys]"
```

Bu key'leri kopyalayın ve `.env` dosyasına ekleyin.

***REMOVED******REMOVED******REMOVED*** 2. .env Dosyası Oluştur

```powershell
cd backend

***REMOVED*** .env dosyası oluştur
@"
ENV=production
PORT=8000
SOARB2B_API_KEYS=KEY1,KEY2,KEY3
FINDEROS_CORS_ORIGINS=https://soarb2b.com,https://www.soarb2b.com
FINDEROS_CORS_ALLOW_ALL=false
FINDEROS_HOST=0.0.0.0
FINDEROS_PORT=8000
"@ | Out-File -FilePath .env -Encoding utf8
```

**ÖNEMLİ:** `KEY1,KEY2,KEY3` yerine yukarıda oluşturduğunuz gerçek key'leri yazın!

***REMOVED******REMOVED*** Deployment Seçenekleri

***REMOVED******REMOVED******REMOVED*** Seçenek 1: Local Test (Şimdi - 2 Dakika)

```powershell
cd backend

***REMOVED*** Environment variables set et
$env:ENV="production"
$env:SOARB2B_API_KEYS="dev-key-12345"  ***REMOVED*** Test için
$env:FINDEROS_CORS_ORIGINS="http://localhost:8000"

***REMOVED*** Server başlat
.\scripts\run_local.ps1
```

Test: http://127.0.0.1:8000/ui/soarb2b_home.html

***REMOVED******REMOVED******REMOVED*** Seçenek 2: Docker Local Test (5 Dakika)

```powershell
cd backend

***REMOVED*** Docker build
docker build -t soarb2b:latest .

***REMOVED*** Docker run (test)
docker run -d `
  -p 8000:8000 `
  -e ENV=production `
  -e SOARB2B_API_KEYS=dev-key-12345 `
  -e FINDEROS_CORS_ORIGINS=http://localhost:8000 `
  -v "$(pwd)/data:/app/data" `
  --name soarb2b-test `
  soarb2b:latest

***REMOVED*** Logs kontrol
docker logs -f soarb2b-test
```

Test: http://localhost:8000/healthz

***REMOVED******REMOVED******REMOVED*** Seçenek 3: Docker Compose (Production - 10 Dakika)

```powershell
cd backend

***REMOVED*** .env dosyası hazır olmalı (yukarıda oluşturuldu)

***REMOVED*** Deploy
docker-compose up -d --build

***REMOVED*** Status kontrol
docker-compose ps

***REMOVED*** Logs
docker-compose logs -f

***REMOVED*** Stop (gerekirse)
docker-compose down
```

***REMOVED******REMOVED******REMOVED*** Seçenek 4: Cloud Deployment (Heroku - 15 Dakika)

```powershell
***REMOVED*** Heroku CLI yüklü olmalı
***REMOVED*** https://devcenter.heroku.com/articles/heroku-cli

heroku login

***REMOVED*** App oluştur
cd backend
heroku create soarb2b-production

***REMOVED*** Environment variables
heroku config:set ENV=production
heroku config:set SOARB2B_API_KEYS="KEY1,KEY2,KEY3"  ***REMOVED*** Gerçek key'ler
heroku config:set FINDEROS_CORS_ORIGINS="https://soarb2b.com,https://www.soarb2b.com"
heroku config:set FINDEROS_CORS_ALLOW_ALL=false

***REMOVED*** Procfile oluştur (yoksa)
@"
web: python -m uvicorn src.app:app --host 0.0.0.0 --port $PORT
"@ | Out-File -FilePath Procfile -Encoding utf8

***REMOVED*** Deploy
git add .
git commit -m "Deploy SOAR B2B"
git push heroku main

***REMOVED*** Logs
heroku logs --tail

***REMOVED*** Custom domain ekle (sonra)
heroku domains:add www.soarb2b.com
```

***REMOVED******REMOVED*** Post-Deployment Verification

```powershell
***REMOVED*** Health check
Invoke-WebRequest http://localhost:8000/healthz -UseBasicParsing

***REMOVED*** Homepage
Invoke-WebRequest http://localhost:8000/ui/soarb2b_home.html -UseBasicParsing

***REMOVED*** API test
$headers = @{"X-API-Key" = "dev-key-12345"}
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/b2b/demo/hotels" -Headers $headers -UseBasicParsing

***REMOVED*** OpenAPI schema
Invoke-WebRequest http://localhost:8000/openapi.json -UseBasicParsing | Select-Object -ExpandProperty Content | Select-String "case-library"
```

***REMOVED******REMOVED*** Hangi Seçeneği Seçmeliyim?

1. **Hızlı test:** Seçenek 1 (Local)
2. **Docker test:** Seçenek 2
3. **Production hazır:** Seçenek 3 (Docker Compose) veya Seçenek 4 (Heroku)
4. **Domain bağlı production:** Seçenek 4 (Heroku) + DNS ayarları

***REMOVED******REMOVED*** Sorun Giderme

***REMOVED******REMOVED******REMOVED*** Port Already in Use
```powershell
***REMOVED*** Port 8000'i kullanan process'i bul
Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess

***REMOVED*** Process'i durdur
Stop-Process -Id <PID> -Force
```

***REMOVED******REMOVED******REMOVED*** Docker Build Fails
```powershell
***REMOVED*** Cache temizle
docker system prune -a

***REMOVED*** Tekrar build
docker build --no-cache -t soarb2b:latest .
```

***REMOVED******REMOVED******REMOVED*** Environment Variables Not Working
```powershell
***REMOVED*** Docker container içinde kontrol
docker exec -it soarb2b-test env | Select-String "SOARB2B"

***REMOVED*** docker-compose ile kontrol
docker-compose config
```

---

**Hazır mısınız?** Yukarıdaki seçeneklerden birini seçin ve adımları takip edin!
