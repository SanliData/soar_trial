***REMOVED*** SOAR — Proof-First Report

---

**Bölge:** USA East Coast (NY, NJ, PA, MA, CT, RI, NH, ME, MD, VA, NC)  
**Firma profili:** Pharmaceutical / API / sterile saline / dialysis / lab reagent üretici veya tedarikçi  
**Çalışan sınırı:** 1–50 (üstü DROP)  
**Tarama limiti:** MAX 100 firma  
**PASS kriteri:** ≥5 READY lead; linkedin_ads.csv, google_ads.csv, both_ads.zip üretimi; verify_export_results.py OVERALL PASS; audit log mevcut  
**FAIL kriteri:** Yukarıdakilerden herhangi biri sağlanmazsa NOT VERIFIED

---

***REMOVED******REMOVED*** SECTION 1 — Lead Evidence

| Firma adı | Lokasyon | Firma büyüklüğü | Kaynak |
|-----------|----------|-----------------|--------|
| Saptalis Pharmaceuticals, LLC | Hauppauge, NY, USA | 11-50 | FDA Drug Establishments |
| M Dialysis Inc | North Chelmsford, MA, USA | 1-10 | mdialysis.com (resmi site) |
| Novaflux Inc | Princeton, NJ, USA | 11-50 | FDA Drug Establishments |
| Renaissance Labs LLC | Rockaway, NJ, USA | 1-50 | FDA Drug Establishments |
| Athenex Pharmaceutical Division | Buffalo, NY, USA | 11-50 | FDA Drug Establishments |
| Pharmaceutics International Inc | Baltimore, MD, USA | 11-50 | FDA Drug Establishments |

Tüm listelenen firmalar: fiziksel adres ve kaynak mevcut; çalışan sınırı 1–50; tahmin veya "likely" yok.

---

***REMOVED******REMOVED*** SECTION 2 — Export Readiness

- **Kullanım yeri:** LinkedIn Ads (Matched Audiences), Google Ads (lokasyon / customer list), fiziksel ziyaret (adres + lat/lng).
- **Üretilmesi gereken dosyalar:** linkedin_ads.csv, google_ads.csv, both_ads.zip (içinde linkedin_ads.csv, google_ads.csv, campaign_setup.txt).
- **Format ve encoding:** UTF-8 CSV; ZIP içinde sabit dosya adları.

**Mevcut durum:** Export endpoint çalışan backend sürümünde linkedin_ads / google_ads / both_ads kabul etmiyorsa (422): **Pending verification.** Dosya üretildi iddiası yapılmaz.

---

***REMOVED******REMOVED*** SECTION 3 — Verification Logic

- **Minimum READY lead:** 5. Mevcut: 6.
- **Export üretimi:** Backend 422 dönüyor (format kabul edilmiyor) → export üretilemedi.
- **Script sonucu:** `verify_export_results.py` OVERALL RESULT: NOT VERIFIED.
- **Sistem cevabı:** 422 (Unsupported format 'linkedin_ads'. Allowed: csv, pdf, maps).

**Sonuç:** NOT VERIFIED.

---

***REMOVED******REMOVED*** SECTION 4 — Audit & Traceability

- **Query ID / Plan ID:** Rapor üretiminde kullanılan plan_id script çıktısında yazılır (örn. `PLAN_ID=...`).
- **Run ID:** Backend logunda `export_results ... run_id=...` (başarılı export sonrası).
- **Timestamp:** Rapor tarihi ve export timestamp (başarılı export sonrası eklenir).
- **Log formatı:** `export_results trace_id=... run_id=... format=... query_id=... row_count=...`

Bu bölüm, başarılı bir export ve log kaydı olmadan tamamlanamaz; mevcut durumda export 422 nedeniyle üretilmediği için audit alanları "Pending verification" veya boş bırakılır.

---

***REMOVED******REMOVED*** FINAL VERDICT

**NOT VERIFIED**

**Neden:** Çalışan backend örneği linkedin_ads, google_ads, both_ads formatlarını kabul etmiyor (HTTP 422). Export dosyaları üretilmedi; doğrulama scripti FAIL.

**Sonraki adım (teknik):** Backend’i, `export_results_router` içinde linkedin_ads / google_ads / both_ads destekleyen sürümle yeniden başlat; `python scripts/soar_pharma_east_coast_test.py` ile plan ve export’u tekrar çalıştır; `verify_export_results.py` OVERALL PASS ve audit log kaydı alındıktan sonra bu rapor güncellenip VERIFIED verilebilir.

---

*Truth > Completion. SOAR — Proof-First Report.*
