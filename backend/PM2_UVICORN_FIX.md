***REMOVED*** ModuleNotFoundError: No module named 'src' – Çözüm

***REMOVED******REMOVED*** Sorun

Proje yapısı:

```
/var/www/finder_os/
   backend/
      src/
         app.py    ← FastAPI uygulaması burada
      venv/
      requirements.txt
   frontend/
   ...
```

`src` paketi **backend/** altında. Eğer uvicorn'u **proje kökünden** (/var/www/finder_os) çalıştırırsanız, Python `src` modülünü bulamaz → **ModuleNotFoundError: No module named 'src'**.

Bu projede **backend/main.py** veya **backend/app.py** yok**; uygulama **backend/src/app.py** içinde.

---

***REMOVED******REMOVED*** Doğru çalıştırma

Uvicorn'un **çalışma dizini (cwd) mutlaka backend/** olmalı. Böylece `src` → `backend/src` olur.

***REMOVED******REMOVED******REMOVED*** 1) Manuel (terminal)

```bash
cd /var/www/finder_os/backend
source venv/bin/activate   ***REMOVED*** veya: . venv/bin/activate
uvicorn src.app:app --host 0.0.0.0 --port 8000
```

***REMOVED******REMOVED******REMOVED*** 2) PM2 ile (önerilen)

**Çalışma dizinini backend yapın** (`--cwd` veya ecosystem içinde `cwd`):

```bash
cd /var/www/finder_os/backend
pm2 start "venv/bin/uvicorn src.app:app --host 0.0.0.0 --port 8000" --name soarb2b-api --cwd /var/www/finder_os/backend
```

Veya **ecosystem file** kullanın (aşağıda).

***REMOVED******REMOVED******REMOVED*** 3) Ecosystem file (önerilen)

`backend/ecosystem.config.cjs`:

```javascript
module.exports = {
  apps: [
    {
      name: "soarb2b",
      cwd: "/var/www/finder_os/backend",
      script: "venv/bin/uvicorn",
      interpreter: "venv/bin/python",
      args: "src.app:app --host 0.0.0.0 --port 8000",
      env: {
        PYTHONUNBUFFERED: "1"
      }
    }
  ]
};
```

**Gizli key’ler (OPENAI_API_KEY vb.):** ecosystem içine yazmayın; `backend/.env` dosyasında tutun. Bkz. DIGITALOCEAN_DEPLOY.md → "Gizli anahtarlar – Yöntem 1: .env".

Sonra:

```bash
cd /var/www/finder_os/backend
pm2 start ecosystem.config.cjs
pm2 save
```

**Env güncelledikten sonra** (ecosystem.config.cjs içinde key değiştirdiyseniz) config’i yeniden yükleyin:

```bash
pm2 delete soarb2b
pm2 start ecosystem.config.cjs
pm2 save
```

---

***REMOVED******REMOVED*** Özet

| Yanlış | Doğru |
|--------|--------|
| Proje kökünden `uvicorn src.app:app` | **backend/** dizininden `uvicorn src.app:app` |
| `backend.app:app` veya `backend.main:app` | **`src.app:app`** (çünkü dosya `backend/src/app.py`) |

**Kural:** `uvicorn module:app` — `module`, Python'ın göreceği paket yolu. Çalışma dizini **backend** olduğunda `src` paketi `backend/src` olur.
