***REMOVED******REMOVED*** SOAR B2B — Operational UI Guidelines (Phase 1)

This document defines the **foundation UI system** rules for SOAR B2B’s productization Phase 1.

***REMOVED******REMOVED******REMOVED*** Cognitive load rules

- **Prefer calm density**: show essential operational signals first; defer deep detail to expandable panels.
- **Avoid “dashboard theater”**: no flashy animations, gradients, glowing AI visuals, or celebratory UI.
- **Stable surfaces**: navigation, status, and approvals must remain in consistent locations.
- **Explainability-first**: evidence, lineage, and “why” must be visible without hunting.
- **No hidden governance**: do not bury policy scope or approvals in tooltips-only surfaces.
- **Authority hierarchy must be legible**: human intent → workflow structure → agent execution → evidence → result.

***REMOVED******REMOVED******REMOVED*** Operational spacing rules

- **Compact by default**: prefer smaller spacing increments and consistent rhythm.
- **Use whitespace intentionally**: whitespace is for grouping and readability, not marketing feel.
- **Limit layout jumps**: avoid shifting panels based on data changes.

***REMOVED******REMOVED******REMOVED*** Progressive disclosure strategy

- **Tier 0**: status chips, counts, risk indicators.
- **Tier 1**: panel summaries and short explanations.
- **Tier 2**: expandable details (timeline event details, evidence lists, audit snippets).
- **Tier 3**: deep operational views (system visibility, traces, raw JSON endpoints).

***REMOVED******REMOVED******REMOVED*** AI interaction model (non-chat)

- **Inline-first**: AI content appears as inline annotations and evidence-linked proposals.
- **Workflow-scoped invocation**: prefer command-palette style requests (context-aware) over chat surfaces.
- **No self-executing actions**: AI suggestions are proposals; approvals remain explicit and visible.

***REMOVED******REMOVED******REMOVED*** Dashboard density rules

- Show **counts and status** first, then allow drill-down.
- Avoid more than **3 primary columns** on desktop.
- Use consistent table and card styles; do not introduce bespoke widgets.

***REMOVED******REMOVED******REMOVED*** Alert hierarchy

- **Info**: muted blue background; for operational guidance.
- **Warn**: restrained amber; for approvals pending, degraded connectors, or pressure signals.
- **Critical**: restrained red; for policy violations or severe runtime pressure.

***REMOVED******REMOVED******REMOVED*** Explainability visibility rules

- Every operational decision surface should provide:
  - **what happened**
  - **why it happened** (brief)
  - **evidence/lineage** pointer
  - **approval/policy scope** if applicable

***REMOVED******REMOVED******REMOVED*** Mobile policy (Phase 1)

- Mobile surfaces are limited to:
  - alerts
  - approvals
  - executive summaries
- Do **not** attempt full orchestration UX on mobile.

