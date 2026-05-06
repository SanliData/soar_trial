***REMOVED*** SOAR B2B — Üst Düzey Reklam Planı (Tüm Servis Maliyetini Karşılama)

**Amaç:** Tüm uygulama ve servis maliyetini reklam geliriyle karşılamak; mümkün olan üst düzeyde reklam envanteri ve gelir hedefi.

---

***REMOVED******REMOVED*** 1. Karşılanacak Toplam Servis Maliyeti

Tüm maliyet kalemleri tek çatıda; reklam hedefi bu toplamı aşacak şekilde planlanır.

| Kalem | Aylık tahmini | Yıllık (≈) |
|-------|----------------|------------|
| Sunucu / hosting (Cloud Run, VPS, vb.) | $40–120 | $480–1.440 |
| Veritabanı (yönetilen DB, yedekleme) | $20–80 | $240–960 |
| E-posta / SMTP / transactional | $10–40 | $120–480 |
| CDN / statik dosya | $15–50 | $180–600 |
| Harici API’ler (harita, doğrulama, AI/LLM kullanımı) | $30–150 | $360–1.800 |
| Domain, SSL, monitoring, log | $10–30 | $120–360 |
| Destek / ticket araçları, 3. parti abonelikler | $20–80 | $240–960 |
| **TOPLAM (aylık)** | **$145–550** | **$1.740–6.600** |

**Hedef:** Aylık reklam gelirinin **en az $150–600 bandını** karşılaması; mümkünse **$200–700/ay** ile tampon bırakılması.

---

***REMOVED******REMOVED*** 2. Gelir Kabülü ve Gerekli Trafik

- **RPM (Revenue Per 1000 impression):** B2B/tech trafiği için display genelde **$1–6 RPM** (bölge ve formatla değişir).
- **Sayfa başı ortalama slot:** Plan dahilinde sayfa başı **2–3 slot** (yüksek envanter senaryosu).
- **Kabül formülü:**
  - Aylık gelir ≈ (Sayfa görüntülemesi × sayfa başı slot sayısı / 1000) × RPM
  - Örnek: 150.000 sayfa × 2.5 slot = 375.000 impression; RPM $2 → **$750/ay**
- **Hedef trafik (tüm maliyeti karşılamak için):**
  - **Minimum:** Ayda ~80.000–120.000 sayfa görüntülemesi, sayfa başı 2 slot → **$160–720** (RPM $1–3).
  - **Hedef:** Ayda **150.000–250.000** sayfa görüntülemesi, sayfa başı 2–3 slot → **$300–1.500** (RPM $1–4).
  - **Üst senaryo:** 300.000+ sayfa, 3 slot ortalama → **$900–2.700+** (RPM $1–3).

Reklam ihtiyacı bu hedefe ulaşacak şekilde **mümkün olan üst düzeyde** tutulacak: çok sayıda sayfa + sayfa başı birden fazla, viewability’si yüksek slot.

---

***REMOVED******REMOVED*** 3. Reklam Verilecek Sayfalar (Maksimum Envanter)

Reklam **mutlaka** açık olan sayfalar (öncelik ve slot sayısı ile):

| Sayfa | Açıklama | Slot sayısı | Öncelik |
|-------|----------|-------------|--------|
| **Ana sayfa** (soarb2b_home) | En yüksek trafik | 3 | 1 |
| **Onboarding 5 soru** (soarb2b_onboarding_5q) | Uzun akış, her adım sonrası alan | 2–3 | 1 |
| **Sonuç merkezi** (soarb2b_results_hub) | Uzun süre kalış | 2 | 1 |
| **Arşiv** (soarb2b_archive) | Liste, üst + alt | 2 | 1 |
| **Fiyatlandırma** (soarb2b_pricing) | Karar anı, yüksek değer | 2 | 1 |
| **Hakkında** (soarb2b_about) | İçerik sayfası | 2 | 2 |
| **Kurumlar / Agencies** (soarb2b_agencies) | İçerik | 2 | 2 |
| **Hedef seçimi** (soarb2b_objective_selection) | Kısa sayfa | 1–2 | 2 |
| **Süreç zaman çizelgesi** (soarb2b_process_timeline) | İçerik | 2 | 2 |
| **Demo / vaka** (soarb2b_case_*, demo) | İçerik | 2 | 2 |
| **Destek** (support) | Footer üstü + içerik altı | 2 | 2 |
| **Gizlilik / Şartlar** (soarb2b_privacy, soarb2b_terms) | Uzun metin sayfaları | 1–2 | 2 |
| **Readme / Kullanım** (soarb2b_readme) | Dokümantasyon | 1–2 | 2 |

**Reklam gösterilmeyecek:** Admin, login/modal içi, ödeme adımları, kritik form alanları (adres/kişi girişi vb.). Ücretli/premium kullanıcılar için ileride reklam kapatma seçeneği eklenebilir.

**Toplam hedef envanter:** 12+ sayfa türü, ortalama ~2–2,5 slot → **~25–35 reklam slotu** (tüm diller/ varyantlar dahil sayfa sayısına göre artar).

---

***REMOVED******REMOVED*** 4. Slot Yerleşimleri (Sayfa Bazlı, Üst Düzey İhtiyaç)

***REMOVED******REMOVED******REMOVED*** 4.1 Ana sayfa (soarb2b_home) — 3 slot

| Slot | Konum | Format | Gerekçe |
|------|--------|--------|--------|
| **home-below-hero** | Hero hemen altı | 728×90 / 320×50 responsive | İlk scroll, yüksek viewability |
| **home-mid** | Trust/özellik bandı ortası veya CTA öncesi | 300×250 veya native | Orta sayfa, ek gelir |
| **home-above-footer** | Footer hemen üstü | Horizontal banner / native | Sayfa sonu, düşük rahatsız edicilik |

***REMOVED******REMOVED******REMOVED*** 4.2 Onboarding (soarb2b_onboarding_5q) — 2–3 slot

| Slot | Konum | Format | Gerekçe |
|------|--------|--------|--------|
| **onboarding-after-step-2** | 2. adım sonrası | 300×250 | Uzun akışta ilk mola |
| **onboarding-after-step-4** | 4. adım sonrası | 300×250 veya 320×50 | İkinci mola |
| **onboarding-above-footer** | Sayfa altı | Leaderboard / native | Son adımlara yakın |

***REMOVED******REMOVED******REMOVED*** 4.3 Sonuç merkezi (soarb2b_results_hub) — 2 slot

| Slot | Konum | Format | Gerekçe |
|------|--------|--------|--------|
| **results-below-summary** | Özet kartların altı | 300×250 | İçerikle uyumlu |
| **results-above-footer** | Footer üstü | 728×90 / native | Sayfa sonu |

***REMOVED******REMOVED******REMOVED*** 4.4 Diğer yüksek öncelikli sayfalar (Fiyatlandırma, Arşiv, Hakkında, Agencies)

- **Fiyatlandırma:** Planların üstü (veya yanı) 1 slot; tablo/CTA altı 1 slot.
- **Arşiv:** Liste üstü 1 banner; liste altı 1 slot.
- **Hakkında / Agencies:** İçerik ortası 1 slot; footer üstü 1 slot.

***REMOVED******REMOVED******REMOVED*** 4.5 Destek, Gizlilik, Şartlar, Readme

- Her sayfada **en az 1**, mümkünse **2 slot:** içerik bloğunun altı + footer üstü (300×250 veya responsive).

---

***REMOVED******REMOVED*** 5. Format ve Sağlayıcı Stratejisi

| Öncelik | Sağlayıcı / tip | Kullanım |
|---------|------------------|----------|
| 1 | **Google AdSense** | Tüm slotlar; display + responsive + mümkünse native |
| 2 | **Media.net / Taboola / Outbrain** | Backup veya ek slot (özellikle içerik sayfaları) |
| 3 | **Direct / sponsorluk** | Trafik ve niş B2B kitlesi büyüdükçe yüksek CPM’li direkt satış |

**Format önceliği:** Responsive display (728×90, 300×250, 320×50) + mümkünse native; video/outstream sadece viewability ve politika uygun ise (B2B imajı korunacak şekilde).

---

***REMOVED******REMOVED*** 6. Teknik ve Operasyonel Özet

- **Merkezi aç/kapa:** `ADS_ENABLED` (veya backend `ad-config` API) ile tüm sayfalarda reklamlar tek yerden açılır/kapatılır.
- **Slot ID yönetimi:** Her slot için `data-slot` ile isim; AdSense (veya diğer sağlayıcı) client/slot ID’leri env veya config’den okunur.
- **Performans:** Reklam script’i lazy-load veya ilk etkileşim sonrası; LCP’yi bozmayacak şekilde hero altı slot hafif gecikmeli yüklenebilir.
- **Viewability:** Slotlar görünür alanda (above-the-fold veya ilk 1–2 scroll) olacak şekilde yerleştirilir; gereksiz sayfa sonu slotları yerine orta sayfa slotları tercih edilir.

---

***REMOVED******REMOVED*** 7. Hedef Özet (Tüm Servis Maliyetini Karşılama)

| Metrik | Minimum | Hedef | Üst senaryo |
|--------|---------|--------|-------------|
| Aylık sayfa görüntülemesi | 80.000 | 150.000 | 300.000+ |
| Sayfa başı ortalama slot | 2 | 2,5 | 3 |
| Aylık toplam impression (≈) | 160.000 | 375.000 | 900.000+ |
| RPM kabülü | $1–2 | $2–3 | $1,5–3 |
| **Aylık reklam geliri (≈)** | **$160–320** | **$750–1.125** | **$1.350–2.700+** |
| Aylık servis maliyeti (≈) | $145–550 | $145–550 | $145–550 |
| **Gelir / maliyet** | Karşılama–tampon | Net karşılar + tampon | Güçlü tampon |

***REMOVED******REMOVED******REMOVED*** Reklam gelirinin maliyete oranı (kaç kat?)

- **Sadece sunucu maliyeti** (aylık $40–120) baz alınırsa:
  - Minimum gelir: **≈ 1,3x – 8x** ($160–320 / $40–120)
  - Hedef gelir: **≈ 6x – 28x** ($750–1.125 / $40–120)
  - Üst senaryo: **≈ 11x – 68x** ($1.350–2.700 / $40–120)
- **Tüm servis maliyeti** (aylık $145–550) baz alınırsa:
  - Minimum: **≈ 0,3x – 2,2x** (karşılama sınırında)
  - Hedef: **≈ 1,4x – 7,8x** (net karşılar + tampon)
  - Üst senaryo: **≈ 2,5x – 19x** (güçlü tampon)

Yani bu planla reklam geliri, **sadece sunucu maliyetinin** hedeflenen trafikte **yaklaşık 6–28 katı**, üst senaryoda **11–68 katı** olacak şekilde kurgulanmıştır; tüm maliyeti karşılamak için ise hedef **1,4x–7,8x**, üst senaryo **2,5x–19x** bandındadır.

Bu plan, **tüm servis maliyetini karşılayacak** ve mümkün olan **üst düzey reklam ihtiyacını** (sayfa ve slot sayısı) tanımlar. Uygulama: mevcut `REKLAM_MONETIZASYON_PLANI.md` ile uyumlu slot isimleri ve `ADS_ENABLED` / slot ID yapılandırması kullanılarak adım adım açılabilir.
