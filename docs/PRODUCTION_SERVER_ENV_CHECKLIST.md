***REMOVED*** Production server env checklist (FinderOS / SoarB2B)

Used with PM2 on DigitalOcean Ubuntu. All required env vars must be set before `pm2 start` or passed via `pm2 restart soarb2b --update-env` after `export`.

---

***REMOVED******REMOVED*** 1. PostgreSQL (if not already installed)

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

Create database and user:

```bash
sudo -u postgres psql -c "CREATE USER soarb2b WITH PASSWORD 'YOUR_DB_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE finderos OWNER soarb2b;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE finderos TO soarb2b;"
```

**DATABASE_URL** (use your real password and host if different):

```
postgresql://soarb2b:YOUR_DB_PASSWORD@localhost:5432/finderos
```

If the app runs on the same host as Postgres, `localhost` is correct. Otherwise use the DB server hostname or IP.

---

***REMOVED******REMOVED*** 2. Required environment variables (set on server)

Set these in the same shell before starting PM2, or add to `~/.bashrc` / a small `~/finder_os_env.sh` and `source` it before `pm2 restart`.

| Variable | Description | Example / how to generate |
|----------|-------------|---------------------------|
| **DATABASE_URL** | PostgreSQL URL (no SQLite in prod) | `postgresql://soarb2b:SECRET@localhost:5432/finderos` |
| **JWT_SECRET** | Cryptographically strong secret (min 32 chars) | `openssl rand -hex 32` |
| **SOARB2B_API_KEYS** | Comma-separated API keys for API access | e.g. `key1,key2` (generate strong keys) |
| **GOOGLE_CLIENT_ID** | Google OAuth client ID | `xxxxx.apps.googleusercontent.com` |
| **GOOGLE_CLIENT_SECRET** | Google OAuth client secret | From Google Cloud Console |
| **OPENAI_API_KEY** | OpenAI API key (for `/api/chat`) | `sk-...` from platform.openai.com |

One-time setup example (run in shell, then start/restart PM2):

```bash
***REMOVED*** Generate and export secrets (run once, then use pm2 restart soarb2b --update-env)
export DATABASE_URL="postgresql://soarb2b:YOUR_DB_PASSWORD@localhost:5432/finderos"
export JWT_SECRET="$(openssl rand -hex 32)"
export SOARB2B_API_KEYS="your-api-key-1,your-api-key-2"
export GOOGLE_CLIENT_ID="xxxxx.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="xxxxx"
export OPENAI_API_KEY="sk-..."

cd /var/www/finder_os
git pull origin main
cd backend
pm2 restart soarb2b --update-env
```

---

***REMOVED******REMOVED*** 3. Already set in ecosystem.config.cjs (no action needed)

- `ENV=production`
- `BASE_URL=https://soarb2b.com`
- `FINDEROS_VERSION=1.0.0`
- `FINDEROS_CORS_ORIGINS=https://soarb2b.com,https://www.soarb2b.com`

These are fixed in the PM2 config; only the variables in the table above must be set on the server.

---

***REMOVED******REMOVED*** 4. Checklist before first production start

- [ ] PostgreSQL installed and running
- [ ] Database and user created; `DATABASE_URL` set
- [ ] `JWT_SECRET` set (e.g. `openssl rand -hex 32`)
- [ ] `SOARB2B_API_KEYS` set (comma-separated)
- [ ] `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` set
- [ ] `OPENAI_API_KEY` set (for `/api/chat`; yoksa 503)
- [ ] All of the above exported in the same shell as `pm2 restart soarb2b --update-env`, or sourced from a script before PM2

After setting and exporting all required variables, run:

```bash
cd /var/www/finder_os/backend
pm2 restart soarb2b --update-env
pm2 logs soarb2b
```

If validation still fails, ensure no typo in variable names and that exports are in the same shell (or in a script you `source` before `pm2 restart`).

---

***REMOVED******REMOVED*** 5. Teşhis: PM2’nin gördüğü env

Uygulama ayağa kalkıyor ama DB/API key hatası alıyorsan, PM2’ye env’in gidip gitmediğini kontrol et:

```bash
pm2 show soarb2b | sed -n '/env:/,/^$/p'
```

`DATABASE_URL`, `OPENAI_API_KEY`, `SOARB2B_API_KEYS` burada yoksa PM2 bu değişkenleri almıyor demektir. Aşağıdaki env dosyası yöntemini kullan.

---

***REMOVED******REMOVED*** 6. Önerilen: Sunucuda env dosyası + PM2

Env’i tek yerde tutup PM2’yi o shell’den başlat.

**6.1 Env dosyası oluştur (gerçek secret’ları kendin yaz):**

```bash
sudo nano /etc/soarb2b.env
```

Örnek içerik (placeholder’ları kendi değerlerinle değiştir):

```bash
DATABASE_URL=postgresql://soarb2b:YOUR_PASSWORD@localhost:5432/finderos
JWT_SECRET=YOUR_JWT_SECRET
SOARB2B_API_KEYS=key1,key2,key3
OPENAI_API_KEY=sk-...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

**6.2 İzinleri sıkılaştır:**

```bash
sudo chmod 600 /etc/soarb2b.env
```

**6.3 Bu env ile PM2 restart:**

```bash
set -a
source /etc/soarb2b.env
set +a

cd /var/www/finder_os/backend
pm2 restart ecosystem.config.cjs --update-env
pm2 logs soarb2b --lines 80
```

Beklenen: DB hatası, OPENAI 503 ve “API KEY VALIDATION FAILED … not in allowed keys” (doğru key’ler env’deyse) kaybolur.

---

***REMOVED******REMOVED*** 7. Postgres şifre hatası devam ediyorsa

**7.1 Bağlantıyı test et (şifre sorar):**

```bash
psql "postgresql://soarb2b@localhost:5432/finderos"
```

**7.2 Şifreyi sıfırlamak istersen:**

```bash
sudo -u postgres psql
```

psql içinde:

```sql
ALTER USER soarb2b WITH PASSWORD 'NEW_STRONG_PASSWORD';
\q
```

Sonra `/etc/soarb2b.env` içindeki `DATABASE_URL`’i bu yeni şifreyle güncelle ve **6.3** adımını tekrarla.

---

***REMOVED******REMOVED*** 8. Google giriş yapmıyor (Login sorun giderme)

- **Backend yapılandırması:** `GOOGLE_CLIENT_ID` ve `JWT_SECRET` mutlaka set olmalı. Kontrol:
  - `GET /v1/auth/health` → `"configured": true`, `"google_client_id_set": true` olmalı.
  - `GET /v1/auth/config` → `"google_client_id": "....apps.googleusercontent.com"` dönmeli (503 veya `null` ise env eksik).
- **Google Cloud Console:** OAuth 2.0 client’ta **Authorized JavaScript origins** kısmına sitenin origin’i eklenmeli:
  - Production: `https://soarb2b.com`, `https://www.soarb2b.com`
  - Yerel test: `http://localhost:8000`, `http://127.0.0.1:8000`
- **Hata mesajları:** “Token audience does not match” → Frontend ile backend aynı `GOOGLE_CLIENT_ID` kullanmalı (backend env veya Secret Manager). “Authentication service is not configured” → Backend’de `GOOGLE_CLIENT_ID` veya `JWT_SECRET` eksik.

---

***REMOVED******REMOVED*** 9. fpdf uyarısı (kritik değil)

Log: `You have both PyFPDF & fpdf2 installed...` → Projede hangisi kullanılıyorsa diğerini kaldır:

```bash
source /var/www/finder_os/venv/bin/activate
pip uninstall -y fpdf pypdf fpdf2
***REMOVED*** Sadece kullandığın paketi kur (genelde fpdf2):
pip install fpdf2
pm2 restart soarb2b --update-env
```
