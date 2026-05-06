***REMOVED*** SOARB2B — Son Yapılan Değişiklikler Raporu

Bu dokümanda SOARB2B platformuna eklenen yeni modüller ve değişiklikler özetlenmektedir.

---

***REMOVED******REMOVED*** 1. COMPANY INTELLIGENCE GRAPH (Şema + Semantik Graf)

***REMOVED******REMOVED******REMOVED*** Eklenen / Güncellenen Dosyalar
- **backend/src/intelligence_graph/**
  - `schema_mapper.py` — Tabloları graf düğümlerine map eder
  - `relationship_extractor.py` — FK ilişkilerini çıkarır
  - `graph_builder.py` — Grafı oluşturur, Redis’te cache’ler
  - `graph_query_engine.py` — Join path, similar_companies, high_response_industries, role_response_correlations
  - `graph_store.py` — Semantik grafı Redis’te saklar (node: company, contact, industry, campaign, message, geography)
  - `models/graph_node.py`, `models/graph_edge.py` — Şema seviyesi
  - `models/node.py`, `models/edge.py` — Semantik node/edge tipleri

- **backend/src/company_graph/** (yeni modül)
  - `graph_builder.py`, `graph_store.py`, `relationship_extractor.py`, `graph_query_engine.py`, `similarity_engine.py`
  - `models/node.py`, `models/edge.py` — company, contact, industry, campaign, message, technology, geography

**Ne değişti:** Veritabanı şeması grafa dönüştürülüyor; benzer şirket, yüksek yanıt veren sektör ve rol–yanıt korelasyonları sorgulanabiliyor.

---

***REMOVED******REMOVED*** 2. NATURAL LANGUAGE SALES QUERY ENGINE (NL Sorgu)

***REMOVED******REMOVED******REMOVED*** Eklenen Dosyalar
- **backend/src/nl_query/**
  - `question_parser.py` — Doğal dil → yapılandırılmış intent (tables, group_by, metric, time_range)
  - `graph_sql_planner.py` — Graf ile join path planlama
  - `sql_generator.py` — Parametreli SQL üretimi (güvenli)
  - `query_validator.py` — Sadece SELECT, whitelist tablo/sütun
  - `response_formatter.py` — Sonuç + özet

**Ne değişti:** Kullanıcılar doğal dille soru sorabiliyor; cevap veritabanından güvenli SQL ile alınıyor.

---

***REMOVED******REMOVED*** 3. SALES DATA ANALYTICS API

***REMOVED******REMOVED******REMOVED*** Eklenen / Güncellenen
- **backend/src/http/v1/analytics_router.py**
  - `POST /v1/analytics/query` — Body: `{"question": "..."}`, yanıt: `sql_used`, `result`, `summary`

**Ne değişti:** Analytics için tek endpoint; NL soru → SQL → sonuç + özet dönüyor.

---

***REMOVED******REMOVED*** 4. MONITORING ENTEGRASYNU

***REMOVED******REMOVED******REMOVED*** Güncellenen Dosyalar
- **backend/src/monitoring/log_ingestor.py**
  - Yeni incident tipleri: `analytics_query_failure`, `graph_generation_failure`, `invalid_sql_generation`, `query_timeout`, `nl_query_parsing_error`
- **backend/src/monitoring/root_cause_analyzer.py**
  - Bu tipler için varsayılan kök neden ve önerilen adım
- **backend/src/monitoring/github_context_finder.py**
  - nl_query, intelligence_graph, analytics_router için muhtemel kaynak dosyalar

**Ne değişti:** Analytics ve graf/NL hataları izlenebilir ve sınıflandırılabilir hale geldi.

---

***REMOVED******REMOVED*** 5. SALES SKILL ENGINE (sales_skills)

***REMOVED******REMOVED******REMOVED*** Eklenen Dosyalar
- **backend/src/sales_skills/**
  - `base_skill.py`, `skill_registry.py`, `skill_executor.py`, `register_all.py`
  - `discovery/company_discovery_skill.py`, `similar_company_finder.py`
  - `persona/decision_maker_selection_skill.py`
  - `outreach/email_generation_skill.py`, `followup_generation_skill.py`
  - `qualification/lead_scoring_skill.py`

**Ne değişti:** Tekrar kullanılabilir satış becerileri; `run(context) -> dict` ile sıralı çalıştırma (SkillExecutor).

---

***REMOVED******REMOVED*** 6. SKILLS/SALES (async skills)

***REMOVED******REMOVED******REMOVED*** Eklenen Dosyalar
- **backend/src/skills/sales/**
  - `company_discovery_skill.py`, `company_qualification_skill.py`, `persona_selection_skill.py`
  - `contact_enrichment_skill.py`, `outreach_generation_skill.py`
  - `reply_classification_skill.py`, `followup_strategy_skill.py`

**Ne değişti:** JSON giriş/çıkışlı, async, log’lanan satış becerileri eklendi.

---

***REMOVED******REMOVED*** 7. MARKET SIGNALS ENGINE

***REMOVED******REMOVED******REMOVED*** Eklenen Dosyalar
- **backend/src/market_signals/**
  - `signal_detector.py` — Sektör/bölge sinyalleri (industry_engagement_surge vb.)
  - `signal_classifier.py` — hiring_spike, technology_adoption, funding_event, vb.
  - `signal_store.py` — Redis’te sinyal listesi
  - `opportunity_detector.py` — Canlı + saklı sinyalleri birleştirir

**Ne değişti:** Pazar sinyalleri tespit edilip sınıflandırılıyor ve saklanıyor.

---

***REMOVED******REMOVED*** 8. AGENT CONTEXT ENGINE (Katmanlı bağlam)

***REMOVED******REMOVED******REMOVED*** Güncellenen / Eklenen
- **backend/src/agents/context_engine.py**
  - `build_context_from_request()` — intent, entities, available_skills
  - `build_layered_context()` — instructions, examples, knowledge, memory, tools, tool_results, market_intelligence (sıralı)
- **backend/src/agents/agent_pipeline.py**
  - `run_agent_pipeline()` — İstek → Context Engine → Agent Reasoning → Skill Execution → Güncel bağlam → LLM yanıtı

**Ne değişti:** Ajanlara verilen bağlam yapılandırıldı; tam pipeline (istek → bağlam → beceri → sonuç → LLM) kullanılabiliyor.

---

***REMOVED******REMOVED*** 9. AUTOMATION ENGINE

***REMOVED******REMOVED******REMOVED*** Eklenen Dosyalar
- **backend/src/automation_engine/**
  - `campaign_executor.py` — Kampanya kuyruğa alır (Redis)
  - `scheduling_engine.py` — Takip sırası planlama
  - `response_router.py` — Yanıtı sınıflandırma becerisine yönlendirir (async)

**Ne değişti:** Kampanya başlatma, planlama ve yanıt yönlendirme otomasyonu eklendi.

---

***REMOVED******REMOVED*** 10. CAMPAIGN LEARNING (campaign_learning)

***REMOVED******REMOVED******REMOVED*** Eklenen Dosyalar
- **backend/src/campaign_learning/**
  - `campaign_metrics_collector.py` — Kampanya sonuçlarını campaign_metrics’e yazar
  - `reply_rate_analyzer.py` — Açılma/yanıt oranları
  - `message_performance_analyzer.py` — Mesaj performansı
  - `industry_performance_model.py` — get_industry_rates(), refresh_industry_performance()
  - `persona_performance_model.py` — get_persona_scores(), refresh_persona_performance()

**Ne değişti:** Kampanya sonuçları toplanıp sektör ve persona performansına dönüştürülüyor.

---

***REMOVED******REMOVED*** 11. LEARNING ENGINE (learning_engine)

***REMOVED******REMOVED******REMOVED*** Eklenen Dosyalar
- **backend/src/learning_engine/**
  - `campaign_analyzer.py` — analyze_campaigns()
  - `persona_performance.py` — get_persona_metrics()
  - `message_performance.py` — get_message_metrics()
  - `industry_performance.py` — get_industry_metrics()

**Ne değişti:** Tarihsel kampanya verisi analiz edilip metrikler üretiliyor; fırsat motoruna beslenebilir.

---

***REMOVED******REMOVED*** 12. LLM ROUTER

***REMOVED******REMOVED******REMOVED*** Eklenen Dosyalar
- **backend/src/llm_router/**
  - `model_registry.py` — classification/parsing → gpt-3.5-turbo; email_generation/strategy → gpt-4
  - `router.py` — route_and_call(task_type, messages)

**Ne değişti:** Görev tipine göre model seçimi ve tek noktadan LLM çağrısı.

---

***REMOVED******REMOVED*** 13. NEXT BEST OPPORTUNITY ENGINE (opportunity_engine)

***REMOVED******REMOVED******REMOVED*** Eklenen / Güncellenen Dosyalar
- **backend/src/opportunity_engine/**
  - `models/opportunity.py` — Opportunity (company, industry, region, signals)
  - `models/opportunity_score.py` — OpportunityScore (score 0–1, recommended_persona, confidence, score_breakdown)
  - `opportunity_detector.py` — Sinyallerle aday fırsatları tespit (hiring_spike, similar_company_response, industry_reply_rate_increase, geographic_engagement_cluster)
  - `opportunity_ranker.py` — Skor 0–1 (industry, persona, similarity, market_signals, engagement) + en iyi persona seçimi
  - `opportunity_store.py` — Redis’te öneri cache’i
  - `recommendation_engine.py` — detect → score → rank → cache → nihai sıralı öneri listesi
  - (Mevcut: `opportunity_scorer.py` — eski kullanım için korundu)

**Ne değişti:** Ham liste yerine skorlanmış, persona önerili, sıralı “sonraki en iyi fırsat” listesi üretiliyor.

---

***REMOVED******REMOVED*** 14. API ROUTES

***REMOVED******REMOVED******REMOVED*** Eklenen / Güncellenen
- **backend/src/http/v1/router_registry.py**
  - company_graph_router, market_signals_router, opportunities_router eklendi
- **backend/src/http/v1/company_graph_router.py**
  - `GET /v1/graph/company/{id}` — Şirket düğümü + ilişkili kişiler
  - `GET /v1/graph/similar/{id}` — Benzer şirketler + skor
  - `POST /v1/graph/refresh` — Grafı yeniden oluşturur
- **backend/src/http/v1/market_signals_router.py**
  - `GET /v1/signals/industry?industry=...`
  - `GET /v1/signals/region?region=...`
- **backend/src/http/v1/opportunities_router.py**
  - `GET /v1/opportunities/recommendations?industry=...&region=...&limit=...&use_cache=...` — Sıralı fırsat önerileri

**Ne değişti:** Graf, sinyal ve fırsat önerileri için yeni HTTP endpoint’leri eklendi.

---

***REMOVED******REMOVED*** 15. UYGULAMA BAŞLANGICI (startup)

***REMOVED******REMOVED******REMOVED*** Güncellenen
- **backend/src/app.py**
  - Startup’ta `src.models` import + `refresh_graph_cache()` (intelligence graph) çağrısı

**Ne değişti:** Uygulama açılışında şema grafı (ve gerekiyorsa cache) güncelleniyor.

---

***REMOVED******REMOVED*** 16. DOKÜMANTASYON

***REMOVED******REMOVED******REMOVED*** Eklenen Dosyalar
- **backend/docs/ANALYTICS_NL_QUERY_API.md** — NL analytics API örnekleri
- **backend/docs/AGENT_PIPELINE_FLOW.md** — İstek → Context → Reasoning → Skill → Sonuç → LLM akışı
- **backend/docs/REVENUE_INTELLIGENCE_API.md** — Graf, sinyal ve fırsat API örnekleri
- **docs/DEGISIKLIK_RAPORU.md** — Bu rapor

---

***REMOVED******REMOVED*** Özet Tablo

| Alan              | Eklenen modül / değişiklik                          |
|-------------------|-----------------------------------------------------|
| Intelligence Graph| intelligence_graph (şema + semantik), company_graph |
| NL Sorgu          | nl_query (parser → planner → SQL → validator)      |
| Analytics API     | POST /v1/analytics/query                            |
| Monitoring        | 5 yeni incident tipi + kaynak eşlemesi             |
| Sales Skills      | sales_skills + skills/sales                         |
| Market Signals    | market_signals (detector, classifier, store)       |
| Context / Agent   | Katmanlı bağlam + agent_pipeline                    |
| Automation        | automation_engine (campaign, scheduling, response) |
| Learning          | campaign_learning + learning_engine                 |
| LLM               | llm_router (model_registry, router)                |
| Fırsat motoru     | opportunity_engine (detector, ranker, store, recs) |
| API               | /v1/graph/*, /v1/signals/*, /v1/opportunities/*    |

Tüm bu değişikliklar mevcut auth, routes, services, models yapısına dokunmadan eklenmiştir; yalnızca yeni dosyalar ve belirtilen satır güncellemeleri yapılmıştır.

---

***REMOVED******REMOVED*** Admin kullanıcı ve ödeme muafiyeti

- **isanli058@gmail.com** admin olarak tanımlıdır (hem admin API hem ödeme/limit muafiyeti).
- Ek admin e-postaları `.env` içinde **SOARB2B_ADMIN_EMAILS** (virgülle ayrılmış) ile verilebilir.

**Admin için uygulama davranışı:**
- **Admin API** (`/api/v1/admin/*`): X-Admin-Key veya Bearer JWT ile admin e-postası yetkisi.
- **Ödeme / quote_token**: Plan oluşturma ve `assistant/start-run` isteklerinde `Authorization: Bearer <JWT>` ile giriş yapmış admin için `quote_token` zorunlu değil; maliyet otomatik onaylı sayılır.
- **Plan limiti**: `plan_limit_middleware` (companies/personas/campaigns limitleri) admin e-postası için uygulanmaz.
- **Abonelik durumu**: `GET /v1/subscriptions/current` admin için `activation_fee_paid: true`, `admin_override_active: true` döner; arayüz ödeme adımını atlar.

**İlgili dosyalar:** `auth_service` (get_admin_emails, is_admin_email, get_email_from_jwt), `admin_router`, `b2b_api_router`, `plan_limit_middleware`, `subscription_router`.
