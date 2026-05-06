***REMOVED*** UPAP Governance Layer — Compliance Report

**Truth > completion.** Bu rapor, SOAR backend’te UPAP zorunluluklarının teknik olarak nasıl uygulandığını özetler.

---

***REMOVED******REMOVED*** 1. Değişen / Eklenen Dosyalar

| Dosya | Değişiklik |
|-------|------------|
| `backend/src/core/upap/policy.py` | **Yeni.** Limitler ve eşikler: company_limit (100), company_size_max (50), min_ready_leads (5), decision_maker_confidence_threshold (0.65), region listeleri. |
| `backend/src/core/upap/enforce.py` | **Yeni.** Hard filter enforcement: discovery / enrichment / export’ta re-validate; ihlalde lead DROP, audit event. |
| `backend/src/core/upap/verify.py` | **Yeni.** Verification gate: export_verification.json, min_ready_leads kontrolü, PASS/FAIL. |
| `backend/src/core/upap/decision_maker.py` | **Genişletildi.** infer_decision_maker_persona: role, authority_level, department, decision_type, accessibility_score, decision_maker_confidence; is_decision_maker yalnızca confidence ≥ 0.65. |
| `backend/src/core/upap/regulated.py` | Plan’dan gelen açık regulated_domain (bool) öncelikli. |
| `backend/src/core/upap/gates.py` | EXPORT’ta enforce() + run_verification_gate(); plan limits (get_limits_from_plan); persona alanları lead’e yazılıyor. |
| `backend/src/models/plan_lifecycle.py` | simulation_mode, regulated_domain (Boolean) alanları eklendi. |
| `backend/src/models/plan_result.py` | verification_status, verification_report_path alanları eklendi. |
| `backend/src/http/export_results_router.py` | Plan’dan simulation_mode, regulated_domain okunuyor; UPAP FAIL → **422** (Unprocessable Entity). |
| `backend/tests/core/test_upap_gates.py` | min_ready_leads, enforce, verify gate, persona testleri eklendi/güncellendi. |

---

***REMOVED******REMOVED*** 2. Hangi Yetkinlikler ENFORCED

***REMOVED******REMOVED******REMOVED*** 2.1 Hard filters (ENFORCED)

- **company_limit** (varsayılan 100), **company_size_max** (varsayılan 50), **region** (allow/deny list).
- `enforce()` discovery → enrichment → export akışında kullanılacak şekilde tasarlandı; export path’te `run_upap_gates(EXPORT)` içinde çağrılıyor.
- İhlal: lead DROP, drop_reasons histogram ile audit’e yansıyor; sonuç export’a ihlal eden satırları içermiyor.

***REMOVED******REMOVED******REMOVED*** 2.2 Simulation / regulated mode (FLAG)

- **Plan:** `simulation_mode`, `regulated_domain` (PlanLifecycle’da kolon; ayrıca onboarding_data’dan okunuyor).
- **regulated_domain=true:** regulated gate’te zorunlu simulation / gerçek şirket adı engeli (mevcut mantık).
- **simulation_mode=true:** Dış iddialar “SIMULATED / NOT VERIFIED” olarak işaretlenebilir (UI/çıktı tarafında kullanım için alanlar hazır).
- Export cevabında plan’dan gelen `simulation_mode` ve `regulated_domain` UPAP evidence’a yazılıyor.

***REMOVED******REMOVED******REMOVED*** 2.3 Decision maker inference (ROLE + CONFIDENCE)

- Persona çıktısına eklenen alanlar: **role**, **authority_level**, **department**, **decision_type**, **accessibility_score**, **decision_maker_confidence** (0–1).
- **is_decision_maker:** Sadece `decision_maker_confidence >= 0.65` (DECISION_MAKER_CONFIDENCE_THRESHOLD) ise true.
- Heuristic + public signals (unvan / dept / keyword); audit’lenebilir skor.

***REMOVED******REMOVED******REMOVED*** 2.4 Cross-channel recommendation (OPTIONAL BASIC)

- Kanal önerisi: `channel_recommendation`, `channel_rule_id`, isteğe bağlı `channel_sequence`.
- Ürün tipi + persona erişilebilirlik skoru + hedefe göre basit kurallar; karar kullanıcı/admin’de.

***REMOVED******REMOVED******REMOVED*** 2.5 Verification gate (PASS/FAIL)

- Export öncesi **verification gate** çalışıyor.
- **export_verification_{plan_id}_{run_id}.json** üretiliyor:
  - plan_id, run_id, timestamp
  - enforced_limits (company_limit, company_size_max, min_ready_leads, region)
  - totals_scanned, totals_kept, totals_dropped, drop_reasons histogram
  - min_ready_leads kontrolü (varsayılan 5)
  - status: PASS | FAIL, reason
- **FAIL:** Export endpoint’leri **422** ile bloklanıyor; body’de trace_id, run_id, reason vb. dönüyor.

***REMOVED******REMOVED******REMOVED*** 2.6 Audit & trace propagation

- Pipeline’da trace_id / run_id kullanılıyor (export’ta request_id + uuid).
- Lead başına: **evidence_sources[]**, **verification_status**, **dropped_reason**, **applied_filters** (enforce çıktısında).
- “No claims without evidence”: evidence yoksa **verification_status = "unverified"**.

---

***REMOVED******REMOVED*** 3. Test komutları

```bash
cd backend
python -m pytest tests/test_upap_limits.py tests/core/test_upap_gates.py -v
```

**Beklenen:** Tüm UPAP testleri geçer (33 test).

---

***REMOVED******REMOVED*** 4. Örnek PASS / FAIL run çıktısı

***REMOVED******REMOVED******REMOVED*** 4.1 PASS (export başarılı)

- **Koşul:** Plan limits sağlanıyor (company_size ≤ 50, company_limit 100, min_ready_leads karşılanıyor), regulated/simulation gate PASS, verification gate PASS.
- **Çıktı:**
  - `data/exports/evidence/upap_evidence_{query_id}_{run_id}.json` → status: PASS
  - `data/exports/evidence/export_verification_{plan_id}_{run_id}.json` → status: PASS
  - HTTP 200 + export body (CSV/PDF/maps/ads)

***REMOVED******REMOVED******REMOVED*** 4.2 FAIL — min_ready_leads

- **Koşul:** totals_kept < min_ready_leads (örn. 5).
- **Çıktı:** HTTP **422**, body örneği:
```json
{
  "error": "UPAP export validation failed",
  "error_code": "UPAP_EXPORT_FAIL",
  "trace_id": "...",
  "run_id": "...",
  "reason": "min_ready_leads_not_met: kept=2, required=5",
  "status": "FAIL",
  "rows_before": 10,
  "rows_after": 2,
  "rejected_counts": { ... },
  "timestamp": "..."
}
```

***REMOVED******REMOVED******REMOVED*** 4.3 FAIL — hard filters (tüm satırlar drop)

- **Koşul:** Tüm lead’ler company_size > 50 veya region filter’a takılıyor.
- **Çıktı:** HTTP **422**, reason örn. `no_rows_after_upap_filters`, rows_after: 0.

***REMOVED******REMOVED******REMOVED*** 4.4 FAIL — regulated + simulation

- **Koşul:** regulated_domain=true ve simulation_mode yok/ false veya gerçek şirket adı.
- **Çıktı:** HTTP **422**, reason örn. `regulated_domain_requires_simulation_mode`.

---

***REMOVED******REMOVED*** 5. Kabul kriterleri (Definition of Done)

| Kriter | Durum |
|--------|--------|
| company_limit ve company_size_max export dahil ihlal edilemiyor | ✅ enforce() + verification gate |
| simulation_mode ve regulated_domain export çıktısına / evidence’a yansıyor | ✅ evidence + plan kolonları |
| Persona’da decision_maker_confidence var; threshold ile is_decision_maker | ✅ infer_decision_maker_persona |
| export_verification.json her run sonunda; PASS/FAIL bloklaması | ✅ verify.py + 422 |
| Lead başına evidence + applied_filters + dropped_reason | ✅ enforce() çıktısı |
| Evidence yoksa lead “verified” sayılmıyor | ✅ verification_status = "unverified" |

---

***REMOVED******REMOVED*** 6. Veritabanı migration notu

- **PlanLifecycle:** `simulation_mode`, `regulated_domain` (Boolean, nullable).
- **PlanResult:** `verification_status`, `verification_report_path` (nullable).

Mevcut DB’de bu kolonlar yoksa migration gerekir (Alembic veya manuel ALTER). Kolonlar nullable olduğu için mevcut kayıtlar etkilenmez.
