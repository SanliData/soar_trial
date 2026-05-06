***REMOVED******REMOVED*** H-048 — Conversational Evaluation Runtime, Generative Operational UI & AG-UI Event Streaming Layer

H-048 is a **governed foundation** implementation that evolves FinderOS from request/response into **event-driven operational intelligence workflows** with deterministic, explainable, auditable primitives.

***REMOVED******REMOVED******REMOVED*** What H-048 adds

- **Conversational evaluation runtime** (`backend/src/conversational_evaluation/`)
  - Multi-turn evaluation sessions (registry only; deterministic).
  - Turn-level governance scoring and risk visibility.
  - Immutable-style trace events (metadata only).
- **Generative operational UI (governed)** (`backend/src/generative_operational_ui/`)
  - Whitelisted component registry only.
  - Safe component projection (sanitized props; no raw HTML/JS).
  - Dashboard/chart/graph “generation” as metadata-driven component composition.
- **AG-UI runtime** (`backend/src/agui_runtime/`)
  - Event schemas for operational timelines (RUN_STARTED, TOOL_CALL, APPROVAL_REQUIRED, etc).
  - Workflow event bus (in-memory metadata; no distributed infra).
  - Tool-call and approval stream projections (metadata only).
- **HITL runtime** (`backend/src/hitl_runtime/`)
  - Approval checkpoints and review queue primitives.
  - Deterministic escalation policy classification.
  - No automatic approvals; approval lineage required.

***REMOVED******REMOVED******REMOVED*** Routers and endpoints

Conversational evaluation:
- `GET /api/v1/system/conversation-eval/sessions`
- `GET /api/v1/system/conversation-eval/traces`
- `GET /api/v1/system/conversation-eval/policy-alignment`
- `GET /api/v1/system/conversation-eval/turn-analysis`

Generative operational UI:
- `GET /api/v1/system/generative-ui/components`
- `GET /api/v1/system/generative-ui/dashboards`
- `GET /api/v1/system/generative-ui/charts`
- `GET /api/v1/system/generative-ui/graphs`

AG-UI runtime:
- `GET /api/v1/system/agui/events`
- `GET /api/v1/system/agui/workflows`
- `GET /api/v1/system/agui/tool-streams`
- `GET /api/v1/system/agui/approval-stream`

HITL runtime:
- `GET /api/v1/system/hitl/checkpoints`
- `GET /api/v1/system/hitl/review-queue`
- `GET /api/v1/system/hitl/escalations`

***REMOVED******REMOVED******REMOVED*** Explicit deferrals (non-goals)

- Uncontrolled generative UI or arbitrary HTML/JS generation.
- Unrestricted frontend code generation or executable payload injection.
- Autonomous workflow completion or hidden event execution.
- Unrestricted live agent execution or uncontrolled streaming infrastructure.
- Invisible approval bypasses.

