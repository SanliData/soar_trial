***REMOVED*** SOARB2B — 10x Mimari: Agent + Data Graph + Automation Engine

Rakipler (Apollo, ZoomInfo, Clay, Instantly) tek katmanda güçlü; SOARB2B üç katmanı birleştirerek **satış sürecini kendisi yürüten** bir platform olur.

---

***REMOVED******REMOVED*** 1. Mimari Özeti

```
User
  ↓
AI Sales Agent          ← Hedefi alır, workflow orkestre eder
  ↓
Company & Contact       ← Canlı veri grafı (statik değil)
Intelligence Graph
  ↓
Automation Engine       ← Kampanya yürütme, outreach, follow-up
  ↓
Outreach + Follow-up
```

**Fark:** Rakipler çoğunlukla sadece veri sunar; bu mimari **satış sürecini üretir ve işler**.

---

***REMOVED******REMOVED*** 2. Katman 1 — AI Sales Agent

**Konum:** `backend/src/agents/` (mevcut)

Kullanıcıdan sadece hedef alınır:
- industry, location, target_roles, goal

Agent sırasıyla:
1. Şirketleri bulur  
2. Şirketleri analiz eder (LLM)  
3. Karar vericileri çıkarır  
4. İletişim bilgilerini toplar (enrichment)  
5. Kişiselleştirilmiş outreach üretir  

**Teknoloji:** LLM + workflow orchestration (`orchestrator`, `workflows/sales_engine_workflow`, `skills/`).

---

***REMOVED******REMOVED*** 3. Katman 2 — Company Intelligence Graph

**Konum:** `backend/src/data_graph/` (önerilen)

Rakiplerin zayıf noktası: **veri statiktir**. Burada **canlı veri grafı** kullanılır.

**Örnek yapı:**

```
Company
 ├─ industry, location
 ├─ technologies, projects
 └─ contacts

Contact
 ├─ role, email, LinkedIn
 └─ activity
```

**Yeteneği:**
- Benzer şirket bulma  
- Yeni hedef pazar keşfi  
- Karar verici ağlarını çıkarma  

**Teknoloji:** Embedding + similarity search; graf ilişkileri (company ↔ contact).

**En kritik bileşen:** Veri katmanı güçlü olmayan AI sistemleri genelde başarısız olur. Graph, agent ve otomasyonu besler.

---

***REMOVED******REMOVED*** 4. Katman 3 — Automation Engine

**Konum:** `backend/src/automation/` (önerilen)

Satış sürecini **yürüten** motor:

```
lead discovery → contact enrichment → email generation
    → outreach → response detection → follow-up
```

- Kampanyalar otomatik ilerler  
- Kullanıcı sürekli müdahale etmek zorunda kalmaz  

**Teknoloji:** Redis queue / background workers; campaign_engine, response_engine, followup_engine.

---

***REMOVED******REMOVED*** 5. Neden 10 Kat Güçlü

| Özellik              | Rakipler      | SOARB2B (bu mimari)     |
|----------------------|---------------|--------------------------|
| Otonom müşteri bulma | Kısıtlı       | Agent + Graph            |
| Kişiselleştirilmiş outreach | Şablon ağırlıklı | LLM + graf bağlamı |
| Self-running campaigns | Ayrı araçlar | Tek platform (Automation) |

**Sonuç:** Platform **lead tool** değil **AI sales engine** olur.

---

***REMOVED******REMOVED*** 6. Kullanıcı Deneyimi Hedefi

Kullanıcı tek cümle hedef verir, örn:

> “Find aluminum fence distributors in Texas.”

Sistem üretir:
- ~80 şirket  
- ~240 karar verici  
- 240 e-posta taslağı  
- Çalışan bir outreach kampanyası  

Süre: birkaç dakika.

---

***REMOVED******REMOVED*** 7. Öğrenen Sistem (uzun vadeli)

Platform zamanla:
- Hangi sektörler dönüşüm sağlıyor  
- Hangi e-postalar işe yarıyor  
- Hangi roller gerçekten karar verici  

öğrenir; agent hedefleri ve otomasyonu buna göre iyileştirir.

---

***REMOVED******REMOVED*** 8. Teknik Modül Haritası

| Katman   | Modül (önerilen)        | Açıklama                          |
|----------|-------------------------|-----------------------------------|
| Agent    | `agents/`               | Zaten var: skills, workflows, orchestrator |
| Data     | `data_graph/`          | company_graph, contact_graph, embeddings/similarity |
| Automation | `automation/`        | campaign_engine, response_engine, followup_engine |

Tümü FastAPI içinde; Redis queue ile uzun işler bloklamadan çalışabilir.

---

***REMOVED******REMOVED*** 9. Uygulama Sırası Önerisi

1. **Agent** — Tamamlandı / iyileştirmeye açık (sales_engine_workflow, skills).  
2. **Data Graph** — Company/Contact grafı + (opsiyonel) embedding/similarity; agent’ın “hedef listesi” ve kişiselleştirme kaynağı.  
3. **Automation** — Redis tabanlı kuyruk + campaign_engine (outreach akışı) + response_engine + followup_engine; agent çıktısını alıp kampanyayı yürütür.

Bu sıra ile önce “doğru hedefler”, sonra “bu hedeflere otomatik ve kişiselleştirilmiş outreach” sağlanır.
