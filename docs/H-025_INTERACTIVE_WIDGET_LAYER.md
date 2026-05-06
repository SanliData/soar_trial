***REMOVED*** H-025 — Interactive Intelligence Widget Layer

**Classification:** Foundation-Level Incremental  
**Status:** Foundation implemented (deterministic HTML fragments, no autonomous UI agents)

***REMOVED******REMOVED*** Interactive intelligence widgets

SOAR B2B is a **Commercial Intelligence OS**, not a generic chat surface. Intelligence must be **presentable**: executives need cards, timelines, and bounded graph summaries—not only JSON. This layer defines **structured widget contracts**, a **static registry**, **escaped deterministic HTML**, and **explainable rendering paths** suitable for Results Hub and future dashboards.

***REMOVED******REMOVED*** Why intelligence presentation matters

Raw payloads force every client to reinterpret semantics, increasing inconsistency and hiding authority/freshness signals. Widget contracts carry **authority level**, **freshness**, **visualization type**, and **typed data** so orchestration can enforce governance before display.

***REMOVED******REMOVED*** Widget contracts

`IntelligenceWidget` and `WidgetRenderRequest` constrain:

- **widget_type** (seven approved types: clusters, signals, executive card, funnel, graph view, procurement timeline, onboarding progress).
- **visualization_type** (card, chart, graph, timeline, table, map) with a **static allow-list** per widget type.
- **authority_level** (`low` | `medium` | `high`) and **freshness_days**.
- **data** as JSON-compatible structures—scanned for obvious script-like patterns.

No arbitrary HTML is accepted in fields; output uses **`html.escape`** for text nodes.

***REMOVED******REMOVED*** Deterministic rendering

Rendering is **template-table driven**: each visualization maps to a small, auditable HTML structure (lists, tables, placeholders). There is **no external JavaScript loading**, **no `<script>` tags**, and **no LLM-generated markup** in this foundation.

***REMOVED******REMOVED*** Future MCP compatibility (deferred)

A future Model Context Protocol integration could **export the same widget JSON** plus HTML fragments to external tools—without migrating the entire frontend to MCP or spawning autonomous widget agents. That remains **explicitly deferred**.

***REMOVED******REMOVED*** Explicitly deferred

- Full MCP migration of the product UI  
- Distributed widget orchestration clusters  
- Autonomous widget agents mutating DOM at runtime  
- Frontend rewrite to React-only architecture  
- Uncontrolled runtime DOM generation  

***REMOVED******REMOVED*** Related artefacts

- Proof: `docs/H-025_IMPLEMENTATION_PROOF.md`  
- Verification: `scripts/verify_h025_widgets.py`  
- API: `POST/GET /api/v1/system/widgets/*`
