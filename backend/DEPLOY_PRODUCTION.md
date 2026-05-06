***REMOVED*** SOAR B2B - Production Deployment Guide

***REMOVED******REMOVED*** 🎯 Hızlı Başlangıç

***REMOVED******REMOVED******REMOVED*** 1. Environment Variables Ayarla

```bash
cd backend
cp .env.example .env
***REMOVED*** .env dosyasını düzenle
```

**Minimum Gerekli:**
```env
ENV=production
SOARB2B_API_KEYS=your-secure-api-key-1,your-secure-api-key-2
FINDEROS_CORS_ORIGINS=https://yourdomain.com
```

***REMOVED******REMOVED******REMOVED*** 2. Docker ile Deploy

```bash
docker-compose up -d --build
```

***REMOVED******REMOVED******REMOVED*** 3. Doğrulama

```bash
***REMOVED*** Health check
curl http://localhost:8000/healthz

***REMOVED*** Homepage
curl http://localhost:8000/ui/soarb2b_home.html
```

***REMOVED******REMOVED*** 📦 Deployment Seçenekleri

***REMOVED******REMOVED******REMOVED*** Seçenek 1: Docker Compose (Önerilen)

```bash
cd backend
docker-compose up -d --build
```

***REMOVED******REMOVED******REMOVED*** Seçenek 2: Docker Run

```bash
docker build -t soarb2b:latest .
docker run -d \
  -p 8000:8000 \
  -e ENV=production \
  -e SOARB2B_API_KEYS=your-key \
  -e FINDEROS_CORS_ORIGINS=https://yourdomain.com \
  -v $(pwd)/data:/app/data \
  --name soarb2b \
  soarb2b:latest
```

***REMOVED******REMOVED******REMOVED*** Seçenek 3: Cloud Platform (AWS/GCP/Azure)

**AWS ECS / Fargate:**
- Dockerfile'ı kullanarak container image oluştur
- ECS Task Definition oluştur
- Environment variables'ı ECS'te set et

**Google Cloud Run:**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/soarb2b
gcloud run deploy soarb2b \
  --image gcr.io/PROJECT_ID/soarb2b \
  --platform managed \
  --set-env-vars ENV=production,SOARB2B_API_KEYS=key1,key2
```

**Heroku:**
```bash
heroku create your-app-name
heroku config:set ENV=production
heroku config:set SOARB2B_API_KEYS=key1,key2
git push heroku main
```

***REMOVED******REMOVED*** 🔧 Production Configuration

***REMOVED******REMOVED******REMOVED*** Nginx Reverse Proxy (Önerilen)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

***REMOVED******REMOVED******REMOVED*** Systemd Service (Linux)

```ini
[Unit]
Description=SOAR B2B API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/soarb2b/backend
Environment="ENV=production"
Environment="SOARB2B_API_KEYS=key1,key2"
Environment="FINDEROS_CORS_ORIGINS=https://yourdomain.com"
ExecStart=/usr/bin/python3 -m uvicorn src.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

***REMOVED******REMOVED*** 🔐 Security Best Practices

1. **API Keys:** Güvenli, rastgele key'ler kullanın
2. **CORS:** Sadece production domain'lerini allow edin
3. **SSL/TLS:** Mutlaka HTTPS kullanın
4. **Rate Limiting:** Aktif (varsayılan: 100 req/min/IP)
5. **Secrets:** Environment variables kullanın, kodda hardcode etmeyin

***REMOVED******REMOVED*** 📊 Monitoring

***REMOVED******REMOVED******REMOVED*** Health Checks

- `/healthz` - Basic health
- `/readyz` - Readiness
- `/metrics` - Prometheus metrics

***REMOVED******REMOVED******REMOVED*** Logs

```bash
***REMOVED*** Docker logs
docker-compose logs -f

***REMOVED*** Systemd logs
journalctl -u soarb2b -f
```

***REMOVED******REMOVED*** 🚨 Troubleshooting

Bkz. `DEPLOYMENT_CHECKLIST.md` ve `DEPLOYMENT_RUNBOOK.md`

---

**Ready to Deploy?** `DEPLOYMENT_CHECKLIST.md` dosyasını takip edin!
