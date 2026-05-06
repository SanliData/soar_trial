***REMOVED******REMOVED*** H-044 — Typed Context Orchestration, Document Intelligence & MCP Runtime Compatibility Layer

This is a **governed foundation implementation**. It deliberately implements **typed, deterministic, auditable** infrastructure for context orchestration, document intelligence abstractions, and MCP-compatible projections.

***REMOVED******REMOVED******REMOVED*** Goals

- **Context is first-class infrastructure**, not an untyped prompt blob.
- **Typed context domains** with hard type boundaries:
  - instructions
  - examples
  - knowledge
  - memory
  - tools
  - guardrails
- **Deterministic semantic compression** (no LLM calls).
- **Workflow-scoped isolation** (no shared global context blobs).
- **Document intelligence abstraction** (metadata + placeholder extraction, lineage preserved).
- **MCP runtime compatibility projection** (policy-scoped tools, no live MCP server required).

***REMOVED******REMOVED******REMOVED*** Explicitly deferred (non-goals)

- Giant MCP-native rewrite.
- Uncontrolled sub-agent spawning.
- Autonomous orchestration meshes.
- GPU OCR infrastructure / OCR clusters.
- Unrestricted MCP execution or public exposure.
- Hidden context mutation or global prompt dumping.

***REMOVED******REMOVED******REMOVED*** Architecture summary

**Typed context orchestration** lives in `backend/src/context_orchestration/`.

- `context_validation_service.py`: strict type checks and required fields.
- `context_lifecycle_service.py`: register/list/prioritize/stale/summarize without hidden deletion.
- Per-type services: `instruction_context_service.py`, `example_context_service.py`, `knowledge_context_service.py`, `memory_context_service.py`, `tool_context_service.py`, `guardrail_context_service.py`.

**Deterministic compression and dedupe** live in `backend/src/context_compression/`.

- `semantic_context_summarizer.py`: deterministic truncation + visible marker:
  - `[Context compressed deterministically]`
- `duplicate_context_detector.py`: fingerprint-based duplicate grouping (recommendations only).
- `retrieval_relevance_service.py`: authority/freshness/workflow/geographic/commercial scoring (H-024 trust anchors).
- `context_token_optimizer.py`: token-budget-aware guidance used by runtime telemetry (no mutation).

**Context isolation** lives in `backend/src/context_isolation/`.

- Workflow partitions defined in `workflow_context_partitioning.py`.
- Cross-workflow access blocked by default in `context_boundary_service.py`.
- Isolated subagent metadata in `subagent_context_service.py` and `isolated_execution_context.py`.

**Document intelligence abstraction** lives in `backend/src/document_intelligence/`.

- `ocr_pipeline_service.py`: pipeline metadata + deterministic placeholder extraction.
- `layout_extraction_service.py`: bounding box/layout schema + placeholder layout.
- `form_structure_service.py`: field/value schema + placeholder fields.
- `markdown_projection_service.py`: placeholder markdown projection preserving lineage.
- `multilingual_document_service.py`: language metadata (no auto-detect).
- `document_validation_service.py`: lineage + unsafe metadata rejection.

**MCP runtime compatibility** lives in `backend/src/mcp_runtime/`.

- `mcp_capability_registry.py`: MCP-friendly capability projection.
- `mcp_tool_projection_service.py`: projects only **orchestration_safe + non-destructive** capabilities into tools.
- `mcp_transport_service.py`: transport metadata only (no public server).
- `mcp_agent_gateway.py`: gateway metadata only (aligns with H-037).
- `mcp_runtime_validation.py`: rejects unsafe tool projections and invalid policy scopes.

***REMOVED******REMOVED******REMOVED*** API surfaces (read-only)

- Context orchestration:
  - `GET /api/v1/system/context/types`
  - `GET /api/v1/system/context/lifecycle`
  - `GET /api/v1/system/context/priorities`
- Context compression:
  - `GET /api/v1/system/context/compression`
  - `GET /api/v1/system/context/duplicates`
  - `GET /api/v1/system/context/relevance`
- Context isolation:
  - `GET /api/v1/system/context/isolation`
  - `GET /api/v1/system/context/boundaries`
  - `GET /api/v1/system/context/partitions`
- Document intelligence:
  - `GET /api/v1/system/documents/ocr-pipeline`
  - `GET /api/v1/system/documents/layout`
  - `GET /api/v1/system/documents/form-structure`
  - `GET /api/v1/system/documents/markdown-projection`
- MCP runtime:
  - `GET /api/v1/system/mcp/capabilities`
  - `GET /api/v1/system/mcp/tools`
  - `GET /api/v1/system/mcp/transports`
  - `GET /api/v1/system/mcp/gateway`

***REMOVED******REMOVED******REMOVED*** Integrations (incremental)

- **H-024 Knowledge ingestion**: added document-oriented source types (`ocr_document`, `bid_pdf`, `scanned_form`, `multilingual_document`) with registry trust anchors.
- **H-030 Runtime context**: exposes typed context integration metadata and token metrics in the orchestration bundle.
- **H-039 Firewall**: adds policy domains for guardrail/tool/MCP/document-derived recognition (interception only).
- **H-040 Skill runtime**: skills can declare required/forbidden context types and isolation/compression flags.
- **H-041 Inference runtime**: telemetry includes typed-context metrics (token cost, savings, duplicate waste, prefill pressure).

***REMOVED******REMOVED******REMOVED*** Demo pages

- `backend/src/ui/en/context_orchestration_demo.html` (and `tr/…`)
- `backend/src/ui/en/document_intelligence_demo.html` (and `tr/…`)
- `backend/src/ui/en/mcp_runtime_demo.html` (and `tr/…`)

