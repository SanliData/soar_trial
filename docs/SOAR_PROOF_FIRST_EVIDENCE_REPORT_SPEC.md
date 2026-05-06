***REMOVED*** SOAR Yetkinliği — Proof-First Evidence Report (PFER)

**Bağlayıcı kural:** SOAR, yalnızca doğrulanabilir kanıt üretebildiği senaryolarda "çalışıyor" der. Raporsuz satış yok; sunumdan önce rapor.

---

***REMOVED******REMOVED*** 1. Raporun amacı (SOAR’un bakışıyla)

SOAR bir raporu şu soruya cevap vermek için üretir:

**"Bu ticari senaryo, gerçek dünyada çalışıyor mu?"**

- Rapor satış sunumu değildir.
- Pazarlama dokümanı değildir.
- "Olabilir" içermez.
- **Geçti / Kaldı** mantığıyla çalışır.

---

***REMOVED******REMOVED*** 2. Zorunlu rapor formatı

***REMOVED******REMOVED******REMOVED*** Başlık (her raporda aynı)

```text
SOAR — Proof-First Report
```

***REMOVED******REMOVED******REMOVED*** Alt bilgi (raporun en üstünde; kullanıcı sonradan değiştiremez)

- **Bölge**
- **Firma profili**
- **Çalışan sınırı**
- **Tarama limiti**
- **PASS / FAIL kriterleri**

Bu bilgiler raporun en üstünde yer alır.

---

***REMOVED******REMOVED*** 3. Section yapısı (standart 4 bölüm)

***REMOVED******REMOVED******REMOVED*** SECTION 1 — Lead Evidence

İçerir:

- Firma adı
- Lokasyon
- Firma büyüklüğü
- Kaynak (FDA, resmi site, kamu kaydı vb.)

**Yasak:** Tahmin, "Likely", "Seems".

**Drop kuralları:**

- Firma >50 çalışan ise → DROP
- Kaynağı yoksa → DROP
- Fiziksel adres yoksa → DROP

***REMOVED******REMOVED******REMOVED*** SECTION 2 — Export Readiness

Kanıtlananlar:

- Veriler nerede kullanılabilir? (LinkedIn Ads, Google Ads, fiziksel ziyaret)
- Hangi dosyalar üretildi / üretilecek
- Dosya formatı ve encoding

Henüz üretilmediyse: **"Pending verification"** yazılır; iddia edilmez.

***REMOVED******REMOVED******REMOVED*** SECTION 3 — Verification Logic

SOAR’un kendini denetlediği bölüm.

Zorunlu kriterler:

- Minimum READY lead sayısı
- Export üretimi
- Script / execution sonucu
- Sistem cevabı (200 / 422 / fail)

Sonuç **tek kelimeyle** verilir:

- **VERIFIED**
- **NOT VERIFIED**

Ara ton yok.

***REMOVED******REMOVED******REMOVED*** SECTION 4 — Audit & Traceability

Zorunlu alanlar:

- Query ID
- Run ID
- Timestamp
- Log formatı

Bu bölüm olmadan rapor geçersizdir.

---

***REMOVED******REMOVED*** 4. Raporun dili

- Düz, soğuk, nesnel.
- **Truth > Completion.**

Örnekler:

- 3 lead varsa → "3 lead var"
- 5 yoksa → FAIL
- "Ama potansiyel vardı" → kullanılmaz

---

***REMOVED******REMOVED*** 5. Hedef okuyucu

- Procurement
- Business development
- Ajans partneri
- Teknik ortak
- Yatırımcı (erken aşama)

Bu nedenle: satış dili yok, abartı yok, savunulabilirlik var.

---

***REMOVED******REMOVED*** 6. SOAR’un otomatik kararı

Rapor sonunda tek hüküm:

```text
FINAL VERDICT: VERIFIED | NOT VERIFIED
```

- FAIL ise → neden yazılır.
- Sonraki adım önerisi (opsiyonel, teknik) eklenebilir.

---

***REMOVED******REMOVED*** 7. Bu yetkinliğin sağladıkları

- SOAR "lead satan tool" değil, **kanıt üreten sistem** olur.
- Ajanslar SOAR’u arka plan altyapısı olarak kullanır.
- Müşteriye "bak böyle diyorum" denmez; **SOAR kendisi konuşur** (rapor ile).

---

***REMOVED******REMOVED*** 8. Bağlayıcı kurallar

- Sunumdan önce rapor.
- Raporsuz satış yok.
- Kanıtsız başarı iddiası yok.

SOAR önce rapor üretir; istenirse müşteri sunumuna çevrilebilir.

---

---

***REMOVED******REMOVED*** 9. Örnek rapor ve konum

- **Spec (bu dosya):** `docs/SOAR_PROOF_FIRST_EVIDENCE_REPORT_SPEC.md`
- **Örnek rapor (Small-Scale Pharma, East Coast):** `docs/SOAR_PHARMA_EAST_COAST_TEST_REPORT.md`
- Rapor üreten script: `backend/scripts/soar_pharma_east_coast_test.py` + `backend/scripts/verify_export_results.py`

Tüm SOAR Proof-First raporları bu spec’e uygun üretilir.
