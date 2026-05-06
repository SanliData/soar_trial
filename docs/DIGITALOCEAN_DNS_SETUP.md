***REMOVED*** DigitalOcean DNS Kayıtları — soarb2b.com

Domain **soarb2b.com** için gerekli DNS kayıtları. NS kayıtları zaten var; site açılsın diye aşağıdakileri ekle.

---

***REMOVED******REMOVED*** 1. Droplet IP’yi bul

- DigitalOcean → **Droplets**
- Backend’in çalıştığı Droplet’e tıkla
- **Public IPv4** adresini kopyala (örn. `164.92.xxx.xxx`)

Bu adresi aşağıda **DROPLET_IP** yerine yazacaksın.

---

***REMOVED******REMOVED*** 2. Eklenecek kayıtlar

DigitalOcean → **Networking** → **Domains** → **soarb2b.com** → **Create a record**

Aşağıdaki kayıtları **sırayla** ekle:

| ***REMOVED*** | Type | Hostname | Value | TTL | Açıklama |
|---|------|----------|--------|-----|----------|
| 1 | **A** | `@` | **DROPLET_IP** | 1800 | soarb2b.com → sunucu |
| 2 | **A** | `www` | **DROPLET_IP** | 1800 | www.soarb2b.com → sunucu |

**DROPLET_IP** = Droplet’inin Public IPv4 adresi.

---

***REMOVED******REMOVED*** 3. Adım adım (panelde)

***REMOVED******REMOVED******REMOVED*** Kayıt 1 — Root domain (soarb2b.com)

1. **Create a record** tıkla.
2. **Type:** `A`
3. **Hostname:** `@` (veya boş bırak; root = soarb2b.com)
4. **Will direct to:** `IPv4 address` seç, **Enter an IP address** alanına Droplet IP’yi yapıştır.
5. **TTL:** 1800 (veya 3600).
6. **Create Record**.

***REMOVED******REMOVED******REMOVED*** Kayıt 2 — www (www.soarb2b.com)

1. Tekrar **Create a record**.
2. **Type:** `A`
3. **Hostname:** `www`
4. **Will direct to:** `IPv4 address` → aynı Droplet IP.
5. **TTL:** 1800.
6. **Create Record**.

---

***REMOVED******REMOVED*** 4. Kontrol

- 5–10 dakika sonra: tarayıcıda `https://soarb2b.com` ve `https://www.soarb2b.com` açılsın.
- Terminal: `nslookup soarb2b.com` → Droplet IP’yi göstermeli.

---

***REMOVED******REMOVED*** 5. Özet

| Mevcut | Eklenecek |
|--------|-----------|
| NS → ns1/ns2/ns3.digitalocean.com (zaten var) | A @ → DROPLET_IP |
| | A www → DROPLET_IP |

Bu iki A kaydı eklendikten sonra DNS yeterli olur; Nginx/PM2 doğru yapılandığında site canlıya alınmış olur.
