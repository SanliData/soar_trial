***REMOVED*** SOAR B2B - Production Deployment Checklist

***REMOVED******REMOVED*** ✅ Hazır Olanlar (P0 Complete)

- [x] Dockerfile hazır
- [x] docker-compose.yml hazır
- [x] Health checks (/healthz, /readyz)
- [x] Metrics endpoint (/metrics)
- [x] Static files serving (/ui/*)
- [x] API authentication (X-API-Key)
- [x] Rate limiting
- [x] Security headers
- [x] Structured logging
- [x] CORS configuration
- [x] Environment variables support

***REMOVED******REMOVED*** ⚠️ Production Deployment Öncesi Yapılacaklar

***REMOVED******REMOVED******REMOVED*** 1. Environment Variables (.env dosyası)

**CRITICAL:** `.env.example` dosyasını kopyalayıp `.env` olarak düzenleyin:

```bash
cp .env.example .env
```

**Minimum Production Ayarları:**
```env
ENV=production
PORT=8000
SOARB2B_API_KEYS=your-secure-key-1,your-secure-key-2
FINDEROS_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
FINDEROS_CORS_ALLOW_ALL=false
```

***REMOVED******REMOVED******REMOVED*** 2. API Keys Güvenliği

**ÖNEMLİ:** Production için güvenli API key'ler oluşturun:

```python
import secrets
***REMOVED*** Generate secure keys
for i in range(3):
    print(secrets.token_urlsafe(32))
```

Bu key'leri `.env` dosyasına ekleyin.

***REMOVED******REMOVED******REMOVED*** 3. Domain ve SSL

- [ ] Domain satın alındı ve DNS ayarları yapıldı
- [ ] SSL sertifikası (Let's Encrypt veya provider)
- [ ] Domain'in `FINDEROS_CORS_ORIGINS`'e eklendiği doğrulandı

***REMOVED******REMOVED******REMOVED*** 4. Docker Build ve Test

```bash
***REMOVED*** Build test
cd backend
docker build -t soarb2b:latest .

***REMOVED*** Run test
docker run -p 8000:8000 \
  -e ENV=production \
  -e SOARB2B_API_KEYS=test-key \
  -e FINDEROS_CORS_ORIGINS=https://yourdomain.com \
  soarb2b:latest

***REMOVED*** Test endpoints
curl http://localhost:8000/healthz
curl http://localhost:8000/ui/soarb2b_home.html
```

***REMOVED******REMOVED******REMOVED*** 5. Production Deployment (Docker Compose)

```bash
cd backend

***REMOVED*** Environment variables set et
export ENV=production
export PORT=8000
export SOARB2B_API_KEYS=your-key-1,your-key-2
export FINDEROS_CORS_ORIGINS=https://yourdomain.com

***REMOVED*** Deploy
docker-compose up -d --build

***REMOVED*** Logs kontrol
docker-compose logs -f
```

***REMOVED******REMOVED******REMOVED*** 6. Reverse Proxy (Nginx/Traefik) - Önerilen

Production'da reverse proxy kullanın:

**Nginx örneği:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    ***REMOVED*** Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

***REMOVED******REMOVED******REMOVED*** 7. Health Check Monitoring

Health check endpoint'lerini monitoring sisteminize ekleyin:

- `/healthz` - Basic health
- `/readyz` - Readiness check
- `/metrics` - Prometheus metrics

***REMOVED******REMOVED******REMOVED*** 8. Data Persistence

Docker volume mount'unun doğru çalıştığını doğrulayın:

```yaml
***REMOVED*** docker-compose.yml'de:
volumes:
  - ./data:/app/data  ***REMOVED*** Bu dizin kalıcı olmalı
```

**Not:** Production'da `./data` yerine absolute path veya named volume kullanın.

***REMOVED******REMOVED******REMOVED*** 9. Logging ve Monitoring

- [ ] Log aggregation (ELK, CloudWatch, etc.)
- [ ] Error tracking (Sentry optional)
- [ ] Performance monitoring
- [ ] Alert configuration

***REMOVED******REMOVED******REMOVED*** 10. Backup Strategy

- [ ] `data/` dizini yedekleniyor
- [ ] Database backup (eğer kullanılıyorsa)
- [ ] Yedekleme schedule'ı belirlendi

***REMOVED******REMOVED*** 🚀 Quick Deploy (Single Command)

**Hazır olduğunuzda:**

```bash
cd backend
docker-compose up -d --build
```

***REMOVED******REMOVED*** 📋 Post-Deployment Verification

Deployment sonrası kontrol edin:

```bash
***REMOVED*** Health check
curl https://yourdomain.com/healthz

***REMOVED*** Homepage
curl https://yourdomain.com/ui/soarb2b_home.html

***REMOVED*** API test (API key ile)
curl -H "X-API-Key: your-key" \
  https://yourdomain.com/api/v1/b2b/demo/hotels

***REMOVED*** Metrics
curl https://yourdomain.com/metrics
```

***REMOVED******REMOVED*** 🔧 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Port Already in Use
```bash
***REMOVED*** Find process
lsof -i :8000  ***REMOVED*** Linux/Mac
netstat -ano | findstr :8000  ***REMOVED*** Windows

***REMOVED*** Kill process
kill -9 <PID>  ***REMOVED*** Linux/Mac
taskkill /PID <PID> /F  ***REMOVED*** Windows
```

***REMOVED******REMOVED******REMOVED*** API Key Not Working
- `.env` dosyasında `SOARB2B_API_KEYS` doğru set edilmiş mi?
- Docker container'a environment variable geçirilmiş mi?
- Request header'ında `X-API-Key` doğru mu?

***REMOVED******REMOVED******REMOVED*** UI Files Not Loading
- `backend/src/ui/` dizini var mı?
- Docker container içinde `/app/src/ui/` var mı?
- Static files mount edilmiş mi? (`/ui` prefix ile)

***REMOVED******REMOVED******REMOVED*** CORS Errors
- `FINDEROS_CORS_ORIGINS` doğru domain'leri içeriyor mu?
- HTTPS kullanıyorsanız, origins de HTTPS olmalı
- Browser console'da CORS hatası kontrol edin

***REMOVED******REMOVED*** 📊 Monitoring Checklist

- [ ] Health check alerts configured
- [ ] Error rate monitoring
- [ ] Response time monitoring
- [ ] Disk space monitoring (for data directory)
- [ ] Memory/CPU usage monitoring

***REMOVED******REMOVED*** 🔐 Security Checklist

- [x] API key authentication
- [x] Rate limiting enabled
- [x] Security headers
- [x] CORS restricted to production domains
- [ ] SSL/TLS enabled
- [ ] Secrets not hardcoded (env vars used)
- [ ] Regular security updates

---

**Son Kontrol:** Tüm checklist'i tamamladıktan sonra deployment'a geçin.

**Destek:** Sorun olursa `DEPLOYMENT_RUNBOOK.md` dosyasına bakın.
