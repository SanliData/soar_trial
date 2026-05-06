***REMOVED*** SOAR B2B - www.soarb2b.com Production Deployment Plan

***REMOVED******REMOVED*** 📅 Deployment Timeline

***REMOVED******REMOVED******REMOVED*** Hemen Yapılacaklar (Bugün - 2 Saat)

1. **Domain Kontrolü** (15 dk)
   - [ ] soarb2b.com domain'i satın alındı mı?
   - [ ] DNS yönetim paneline erişim var mı?
   - [ ] www subdomain'i hazır mı?

2. **Hosting Platform Seçimi** (30 dk)
   - **Öneri 1: DigitalOcean Droplet** ($6-12/ay)
   - **Öneri 2: AWS EC2/Lightsail** ($5-10/ay)
   - **Öneri 3: Google Cloud Run** (Pay-as-you-go)
   - **Öneri 4: Heroku** ($7-25/ay)

3. **Environment Variables Hazırlığı** (15 dk)
   ```bash
   ***REMOVED*** Production API keys oluştur
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

***REMOVED******REMOVED******REMOVED*** Deployment (1-2 Saat)

4. **Server Setup** (30-60 dk)
   - SSH erişimi kurulumu
   - Docker kurulumu
   - Nginx kurulumu

5. **SSL Sertifikası** (15 dk)
   - Let's Encrypt ile ücretsiz SSL

6. **Application Deploy** (15 dk)
   - Docker container deploy
   - Health check

***REMOVED******REMOVED******REMOVED*** DNS & Testing (30 dk)

7. **DNS Yapılandırması** (15 dk)
8. **Production Test** (15 dk)

***REMOVED******REMOVED*** 🚀 Hızlı Deployment (DigitalOcean Örneği)

***REMOVED******REMOVED******REMOVED*** Adım 1: DigitalOcean Droplet Oluştur

```bash
***REMOVED*** 1. DigitalOcean Console'da:
***REMOVED*** - Create Droplet
***REMOVED*** - Ubuntu 22.04 LTS
***REMOVED*** - $6/ay (1GB RAM, 1 CPU)
***REMOVED*** - SSH key ekle
```

***REMOVED******REMOVED******REMOVED*** Adım 2: Server'a Bağlan ve Kurulum

```bash
***REMOVED*** SSH ile bağlan
ssh root@YOUR_SERVER_IP

***REMOVED*** Docker kurulumu
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

***REMOVED*** Docker Compose kurulumu
apt-get update
apt-get install docker-compose-plugin -y

***REMOVED*** Nginx kurulumu
apt-get install nginx certbot python3-certbot-nginx -y
```

***REMOVED******REMOVED******REMOVED*** Adım 3: Uygulamayı Deploy Et

```bash
***REMOVED*** Git clone (veya scp ile dosya kopyala)
git clone https://github.com/SanliData/Finder_os.git
cd Finder_os/backend

***REMOVED*** .env dosyası oluştur
cat > .env << EOF
ENV=production
PORT=8000
SOARB2B_API_KEYS=your-secure-key-1,your-secure-key-2
FINDEROS_CORS_ORIGINS=https://soarb2b.com,https://www.soarb2b.com
FINDEROS_CORS_ALLOW_ALL=false
EOF

***REMOVED*** Docker Compose ile deploy
docker compose up -d --build

***REMOVED*** Logs kontrol
docker compose logs -f
```

***REMOVED******REMOVED******REMOVED*** Adım 4: Nginx Yapılandırması

```bash
***REMOVED*** Nginx config oluştur
cat > /etc/nginx/sites-available/soarb2b.com << 'EOF'
server {
    listen 80;
    server_name soarb2b.com www.soarb2b.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

***REMOVED*** Symlink oluştur
ln -s /etc/nginx/sites-available/soarb2b.com /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

***REMOVED*** Nginx test ve restart
nginx -t
systemctl restart nginx
```

***REMOVED******REMOVED******REMOVED*** Adım 5: SSL Sertifikası (Let's Encrypt)

```bash
***REMOVED*** SSL sertifikası al
certbot --nginx -d soarb2b.com -d www.soarb2b.com

***REMOVED*** Otomatik yenileme test
certbot renew --dry-run
```

***REMOVED******REMOVED******REMOVED*** Adım 6: DNS Yapılandırması

Domain DNS ayarlarında:

```
Type: A
Name: @
Value: YOUR_SERVER_IP
TTL: 3600

Type: A
Name: www
Value: YOUR_SERVER_IP
TTL: 3600
```

DNS propagation: 5 dakika - 48 saat (genelde 5-30 dk)

***REMOVED******REMOVED******REMOVED*** Adım 7: Test

```bash
***REMOVED*** Health check
curl https://www.soarb2b.com/healthz

***REMOVED*** Homepage
curl https://www.soarb2b.com/ui/soarb2b_home.html

***REMOVED*** API test
curl -H "X-API-Key: your-secure-key-1" \
  https://www.soarb2b.com/api/v1/b2b/demo/hotels
```

***REMOVED******REMOVED*** 📋 Alternative: Google Cloud Run (Daha Hızlı, Serverless)

***REMOVED******REMOVED******REMOVED*** Adım 1: Google Cloud Setup

```bash
***REMOVED*** Google Cloud CLI kurulumu (Windows)
***REMOVED*** https://cloud.google.com/sdk/docs/install

***REMOVED*** Login
gcloud auth login

***REMOVED*** Project oluştur
gcloud projects create soarb2b-production

***REMOVED*** Project seç
gcloud config set project soarb2b-production

***REMOVED*** Billing account bağla (gerekirse)
gcloud billing projects link soarb2b-production --billing-account=BILLING_ACCOUNT_ID
```

***REMOVED******REMOVED******REMOVED*** Adım 2: Deploy to Cloud Run

```bash
cd backend

***REMOVED*** Build ve deploy
gcloud run deploy soarb2b \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars ENV=production \
  --set-env-vars SOARB2B_API_KEYS=key1,key2 \
  --set-env-vars FINDEROS_CORS_ORIGINS=https://soarb2b.com,https://www.soarb2b.com \
  --memory 512Mi \
  --timeout 300

***REMOVED*** Custom domain bağla
gcloud run domain-mappings create \
  --service soarb2b \
  --domain www.soarb2b.com \
  --region us-central1
```

Cloud Run otomatik SSL sağlar!

***REMOVED******REMOVED*** ⚡ En Hızlı Yol: Heroku (10 Dakika)

```bash
***REMOVED*** Heroku CLI kurulumu
***REMOVED*** https://devcenter.heroku.com/articles/heroku-cli

***REMOVED*** Login
heroku login

***REMOVED*** App oluştur
heroku create soarb2b-production

***REMOVED*** Environment variables set et
heroku config:set ENV=production
heroku config:set SOARB2B_API_KEYS=key1,key2
heroku config:set FINDEROS_CORS_ORIGINS=https://soarb2b.com,https://www.soarb2b.com

***REMOVED*** Deploy
git push heroku main

***REMOVED*** Custom domain ekle
heroku domains:add www.soarb2b.com
heroku domains:add soarb2b.com

***REMOVED*** SSL sertifikası (otomatik)
***REMOVED*** Heroku ücretsiz SSL sağlar
```

***REMOVED******REMOVED*** ✅ Deployment Sonrası Checklist

- [ ] https://www.soarb2b.com erişilebilir
- [ ] https://www.soarb2b.com/healthz 200 OK döndürüyor
- [ ] https://www.soarb2b.com/ui/soarb2b_home.html açılıyor
- [ ] API endpoints çalışıyor
- [ ] SSL sertifikası geçerli
- [ ] Mobile responsive test edildi
- [ ] Browser console'da hata yok

***REMOVED******REMOVED*** 🎯 Ne Zaman Erişilebilir?

***REMOVED******REMOVED******REMOVED*** Senaryo 1: DigitalOcean/VPS (1-2 Saat)
- Server setup: 30-60 dk
- SSL kurulumu: 15 dk
- DNS propagation: 5-30 dk
- **TOPLAM: 1-2 saat**

***REMOVED******REMOVED******REMOVED*** Senaryo 2: Google Cloud Run (30 Dakika)
- Cloud Run deploy: 15 dk
- Domain mapping: 10 dk
- DNS propagation: 5-30 dk
- **TOPLAM: 30-60 dakika**

***REMOVED******REMOVED******REMOVED*** Senaryo 3: Heroku (15 Dakika)
- Heroku deploy: 10 dk
- Domain ekleme: 5 dk
- **TOPLAM: 15-20 dakika**

***REMOVED******REMOVED*** 🔧 İhtiyaç Duyulan Bilgiler

1. **Domain Bilgileri:**
   - soarb2b.com DNS yönetim paneline erişim
   - Domain registrar bilgileri

2. **Hosting Seçimi:**
   - Hangi platform? (DigitalOcean, AWS, GCP, Heroku)
   - Bütçe? ($5-25/ay)

3. **Production API Keys:**
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   print(secrets.token_urlsafe(32))
   ```

***REMOVED******REMOVED*** 📞 Sonraki Adım

1. Hangi hosting platform'unu seçeceğinizi söyleyin
2. Production API key'leri oluşturun
3. DNS erişimi hazır olun

**Hazır olduğunuzda:** Bu planı adım adım takip edin!

---

**Tahmini Deployment Süresi: 15 dakika - 2 saat** (platform'a göre)
