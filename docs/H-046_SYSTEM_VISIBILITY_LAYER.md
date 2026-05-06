***REMOVED******REMOVED*** H-046 — Unified Operational Admin & System Visibility Layer

This is a **governed foundation implementation** focused on product consolidation: **operational visibility**, **governance visibility**, and **system status clarity** across the existing AI-native infrastructure (H-020 → H-045).

***REMOVED******REMOVED******REMOVED*** Why this layer exists

Operational visibility is required for sustainable AI governance. Without it, the platform risks becoming “architecture-rich but product-poor.”

***REMOVED******REMOVED******REMOVED*** What this layer provides

- **System health**: active routers/domains, verification coverage signals, failed validation counts, runtime warnings, stale workflow signals (deterministic).
- **Runtime pressure**: token/context/orchestration/retrieval/agent/retry pressure with explainable thresholds.
- **Workflow audit**: timeline metadata including approvals, traces, retrieval lineage visibility, context expansion/compression events.
- **Retrieval visibility**: connector visibility, authority distribution, freshness summaries, token-cost signals, selective expansion rates.
- **Connector freshness**: deterministic classification: healthy/stale/degraded/disconnected.
- **Orchestration trace visibility**: skill activation metadata, NL routing, approval detection, retrieval steps, expansion decisions.
- **Approval queue**: pending/escalated/denied operations metadata; **no auto-approval**.
- **Active agent visibility**: active/idle/restricted/high-risk/approval-blocked (observability only).

***REMOVED******REMOVED******REMOVED*** Domains and router

- Domain: `backend/src/system_visibility/`
- Router: `backend/src/http/v1/system_visibility_router.py`

Endpoints:

- `GET /api/v1/system/visibility/health`
- `GET /api/v1/system/visibility/runtime-pressure`
- `GET /api/v1/system/visibility/workflow-audit`
- `GET /api/v1/system/visibility/retrieval`
- `GET /api/v1/system/visibility/connectors`
- `GET /api/v1/system/visibility/orchestration`
- `GET /api/v1/system/visibility/approvals`
- `GET /api/v1/system/visibility/agents`

***REMOVED******REMOVED******REMOVED*** UI dashboard

- `backend/src/ui/en/system_visibility_dashboard.html`
- `backend/src/ui/tr/system_visibility_dashboard.html`

***REMOVED******REMOVED******REMOVED*** Explicitly deferred (non-goals)

- Hidden admin backdoors.
- Unrestricted internal runtime controls.
- Fake uptime metrics.
- Autonomous UI orchestration.

