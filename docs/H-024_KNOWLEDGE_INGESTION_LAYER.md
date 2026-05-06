***REMOVED*** H-024 — Context Acquisition & Structured Knowledge Ingestion Layer

**Classification:** Foundation-Level Incremental  
**Status:** Foundation implemented (deterministic ingestion, no scraping execution)

***REMOVED******REMOVED*** Why naive RAG fails for Commercial Intelligence OS

Chunking raw documents into fixed token windows without authority, lineage, or freshness metadata amplifies four failure modes: **stale signals** treated as current, **low-trust sources** ranked beside official procurement artefacts, **lost section context** across arbitrary splits, and **non-auditable retrieval** when downstream teams cannot explain why an excerpt surfaced. SOAR B2B targets precision exposure and market access—retrieval must support governance and explainability, not only cosine similarity.

***REMOVED******REMOVED*** Why a representation layer matters

Structured **semantic knowledge blocks** encode commercial intent: procurement notices, opportunity signals, graph relationships, exposure patterns. Metadata (industry, geography, commercial relevance, lineage) lets orchestration layers enforce policies before any vector search or LLM call. This foundation prepares Results Hub, Opportunity Engine, and graph reasoning without mandating a vector database rewrite.

***REMOVED******REMOVED*** Semantic blocks vs naive chunks

| Aspect | Naive fixed-size chunks | Semantic blocks (H-024) |
|--------|-------------------------|---------------------------|
| Splitting | Character/token windows | Paragraph-first, then bounded line splits |
| Context | Often breaks sections | Preserves section boundaries where possible |
| Governance | Implicit | Explicit block types and source classes |
| Audit | Weak | Lineage + deterministic scores |

The `semantic_chunk_service` performs **deterministic** segmentation only—no LLM summarisation inside the chunker.

***REMOVED******REMOVED*** Authority metadata

Authority combines **registry trust** for approved source classes (e.g. public procurement feeds vs uploaded documents) with **freshness decay** and optional lineage boosts when a parent document identifier is present. Unverified anonymous scraping classes are **rejected at validation**, not merely down-ranked.

***REMOVED******REMOVED*** Freshness metadata

Freshness uses explicit age in days (`freshness_days`) plus a confidence score that decreases with age and a configurable stale threshold for operational signalling. This avoids pretending outdated filings are “fresh” because embeddings cluster tightly.

***REMOVED******REMOVED*** Source lineage

Each block carries `source_lineage` (`source_type`, `source_record_id`, optional `parent_document_id`). Only registry-approved `source_type` values are accepted; `unverified_anonymous_scraping_source` is explicitly blocked.

***REMOVED******REMOVED*** Retrieval policy design

Ranking is a **weighted linear combination** of authority, freshness confidence, commercial relevance, and geographic/industry alignment—with **per-block factor breakdowns** returned on list responses for explainability. Policies are exposed via `GET /api/v1/system/knowledge/policies` without executing retrieval agents.

***REMOVED******REMOVED*** Deferred (explicit)

- Massive distributed scraping infrastructure  
- Autonomous crawling swarms or recursive retrieval agents  
- Aggressive protected-platform harvesting  
- BrightData-scale proxy orchestration  
- Replacing existing vector stores or embedding pipelines (not required for this foundation)

***REMOVED******REMOVED*** Related artefacts

- Documentation proof: `docs/H-024_IMPLEMENTATION_PROOF.md`  
- Verification: `scripts/verify_h024_knowledge_ingestion.py`  
- API: `POST/GET /api/v1/system/knowledge/*`
