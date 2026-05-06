***REMOVED*** SOAR B2B — Reklam Monetizasyon Planı

**Amaç:** Uygulama sayfalarına reklam alımını en etkin şekilde planlamak; mümkünse tüm sunucu masraflarını reklam geliriyle karşılamak.

---

***REMOVED******REMOVED*** 1. Sunucu Maliyeti Tahmini (Karşılanacak Hedef)

| Ortam | Aylık tahmini maliyet |
|-------|------------------------|
| Cloud Run / küçük VPS | ~$30–80 |
| Orta trafik + DB + e-posta | ~$80–150 |
| Yüksek trafik + CDN | ~$150–300 |

**Hedef:** Aylık reklam gelirinin bu bandı karşılaması (ör. $50–150/ay).

---

***REMOVED******REMOVED*** 2. Reklam Geliri Kabül (Kabaca)

- **RPM (Revenue Per 1000 impressions):** B2B/tech trafiği için display reklamlar genelde $1–5 RPM (bölgeye göre değişir).
- **Örnek:** Ayda 100.000 sayfa görüntülenmesi × 2 reklam slotu = 200.000 impression → $200–1.000 (RPM $1–5).
- **Sonuç:** Ayda 50.000–100.000 sayfa görüntülemesi ve 2–3 iyi yerleştirilmiş slot ile sunucu maliyeti karşılanabilir.

---

***REMOVED******REMOVED*** 3. Reklam Verilecek Sayfalar (Envanter)

Reklam **gösterilecek** sayfalar (yüksek görünürlük, kullanıcı deneyimi dengesi):

| Sayfa | Açıklama | Öncelik |
|-------|----------|--------|
| **Ana sayfa** (tr/en soarb2b_home) | En yüksek trafik, hero altı + footer üstü | 1 |
| **Onboarding 5 soru** (soarb2b_onboarding_5q) | Uzun sayfa, adım arası / sayfa altı | 1 |
| **Sonuç merkezi** (soarb2b_results_hub) | Kullanıcı sonuç sayfası, sidebar veya alt alan | 1 |
| **Arşiv** (soarb2b_archive) | Liste sayfası, üst veya alt banner | 2 |
| **Hedef seçimi** (soarb2b_objective_selection) | Kısa sayfa, tek slot | 2 |
| **Süreç zaman çizelgesi** (soarb2b_process_timeline) | İçerik sayfası, tek slot | 2 |
| **Demo / vaka** (demo_showcase, soarb2b_case_*) | İçerik sayfası, tek slot | 2 |
| **Destek** (support) | Tek slot, footer üstü | 2 |

Reklam **gösterilmeyecek** sayfalar:

- **Admin** (admin.html): Güvenlik ve dikkat dağılmaması.
- **Login/Modal içi:** Kullanıcı işlemi sırasında reklam yok.
- **Ücretli/Premium kullanıcı:** İsteğe bağlı olarak cookie/flag ile kapatılabilir (ileride).

---

***REMOVED******REMOVED*** 4. Yerleşim Stratejisi (En Etkin Konumlar)

***REMOVED******REMOVED******REMOVED*** 4.1 Ana sayfa (soarb2b_home)

| Slot | Konum | Format önerisi | Gerekçe |
|------|--------|----------------|--------|
| **home-below-hero** | Hero bölümünün hemen altı, trust-band üstü | Responsive leaderboard (728×90 / 320×50) | İlk scroll’da görünür, yüksek viewability |
| **home-above-footer** | Footer’dan hemen önce | Horizontal banner veya native | Sayfa sonu okuma, düşük rahatsız edicilik |

***REMOVED******REMOVED******REMOVED*** 4.2 Onboarding (soarb2b_onboarding_5q)

| Slot | Konum | Format | Gerekçe |
|------|--------|--------|--------|
| **onboarding-mid** | Adımlar arasında (örn. 3. adım sonrası) veya sayfa altı | Rectangle (300×250) veya responsive | Uzun sayfada tek, görünür slot |

***REMOVED******REMOVED******REMOVED*** 4.3 Sonuç merkezi (soarb2b_results_hub)

| Slot | Konum | Format | Gerekçe |
|------|--------|--------|--------|
| **results-sidebar** veya **results-below-summary** | Özet kartların altı veya sağ sidebar | 300×250 veya native | İçerikle uyumlu, B2B kullanıcıda kabul edilebilir |

***REMOVED******REMOVED******REMOVED*** 4.4 Diğer sayfalar (arşiv, hedef seçimi, timeline, demo, destek)

- **Tek slot:** İçerik bloğunun altı veya footer üstü.
- **Format:** 300×250 veya responsive (320×50 mobil, 728×90 masaüstü).

---

***REMOVED******REMOVED*** 5. Teknik Uygulama Özeti

- **Merkezi aç/kapa:** `ADS_ENABLED` (veya backend `ad-config` API) ile tüm sayfalarda reklamlar tek yerden açılıp kapatılır.
- **Slot ID yönetimi:** Her slot için `data-slot` ile isim verilir; reklam sağlayıcı (ör. AdSense) client/slot ID’leri env veya config’den okunur.
- **Responsive:** Slotlar `min-height` ve `max-width: 100%` ile taşmayı önler; sağlayıcı responsive birim kullanılırsa mobil/desktop otomatik uyum sağlar.
- **Performans:** Reklam script’i mümkünse lazy-load veya sayfa etkileşiminden sonra yüklenir; LCP’yi bozmamak için hero altı slot hafif gecikmeli de yüklenebilir.

---

***REMOVED******REMOVED*** 6. Reklam Sağlayıcı Önerisi

| Sağlayıcı | Avantaj | Not |
|-----------|---------|-----|
| **Google AdSense** | Kolay entegrasyon, otomatik format, B2B/tech CPM’leri nispeten iyi | Onay süreci olabilir; politikaya uyum gerekli |
| **Media.net / Taboola** | B2B odaklı alternatif | Backup veya ek gelir |
| **Direct / Sponsor** | Yüksek CPM, tam kontrol | Trafik belirli seviyeye geldikten sonra düşünülebilir |

Öncelik: AdSense ile başlayıp, slotları bu plandaki konumlara göre açmak; gerekirse Media.net vb. eklemek.

---

***REMOVED******REMOVED*** 7. Ortam Değişkenleri (Backend .env)

Reklamları açmak ve AdSense slot ID'lerini vermek için:

```env
***REMOVED*** Reklam: aç/kapa
ADS_ENABLED=1

***REMOVED*** Google AdSense (client ID = ca-pub-XXXXXXXX)
ADSENSE_CLIENT_ID=ca-pub-xxxxxxxxxxxxxxxx

***REMOVED*** Slot ID'leri (AdSense panelinden her bir reklam birimi için alınır)
ADS_SLOT_HOME_BELOW_HERO=1234567890
ADS_SLOT_HOME_ABOVE_FOOTER=0987654321
ADS_SLOT_ONBOARDING_MID=
ADS_SLOT_RESULTS_BELOW_SUMMARY=
```

- `ADS_ENABLED=0` veya boş bırakılırsa reklam hiç yüklenmez; slot div'leri boş kalır.
- Slot ID boş olan sayfalarda o slot gösterilmez.

---

***REMOVED******REMOVED*** 8. Beklenen Sonuç (Özet)

- **Sayfa envanteri:** 8+ sayfa türü, sayfa başı 1–2 slot → toplam ~12–15 slot.
- **Viewability odaklı yerleşim:** Hero altı + footer üstü + uzun sayfalarda tek orta/alt slot.
- **Hedef:** Aylık 50k–100k+ sayfa görüntülemesi ile $50–150+ reklam geliri; sunucu maliyetini karşılamak.
- **UX:** Modal ve kritik form alanlarında reklam yok; B2B imajı korunur.

Bu plan, uygulamanın tüm sunucu masraflarını reklamla karşılama hedefine göre en etkin reklam alma seçeneğini yapılandırır. Slotlar ve sayfalar ortak bir config ile yönetildiği için ileride ek sayfa veya slot eklemek kolaydır.
