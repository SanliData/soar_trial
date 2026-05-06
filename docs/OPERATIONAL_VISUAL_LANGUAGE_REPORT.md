***REMOVED*** Operational Visual Language System — Implementation report

FinderOS is a **trustworthy operational intelligence platform**. The visual language must communicate calm, governance, and explainability without “AI theater”.

***REMOVED******REMOVED*** Visual philosophy implemented

- **Calm + precise**: grayscale-first surfaces, restrained borders, low-fatigue shadows.
- **Governed**: metadata and audit fields are always present, but visually recessed.
- **Explainable**: evidence and lineage are treated as first-class operational surfaces.
- **AI-native, not AI-centric**: AI output is styled as an attributed operational note, not a chat product.

***REMOVED******REMOVED*** Typography system

- Font: `Inter` first, with safe system fallbacks.
- Weights: **400 / 500 only** via tokens.
- Hierarchy: operational metrics, section/panel titles, body, metadata labels, evidence text.
- Metadata labels: small uppercase with restrained tracking.

Files:

- `backend/src/ui/shared/operational_tokens.css`
- `backend/src/ui/shared/operational_typography.css`

***REMOVED******REMOVED*** Spacing system

- 4px base grid, 8px rhythm helpers.
- Nested stack rules for dense-but-readable panel content.

File:

- `backend/src/ui/shared/operational_spacing.css`

***REMOVED******REMOVED*** Panel hierarchy

Operational panel roles are expressed via subtle border/background variants:

- Operational
- Intelligence
- Explainability
- Evidence
- Workflow
- Approval
- Telemetry

File:

- `backend/src/ui/shared/operational_panels.css`

***REMOVED******REMOVED*** Explainability language

- Evidence drawers and explainability panels rely on:
  - Left-rail confidence language
  - Evidence linkage
  - Metadata visibility rules

Files:

- `backend/src/ui/shared/operational_components.css`
- `backend/src/ui/shared/operational_timeline.css`

***REMOVED******REMOVED*** Governance language (approvals / escalations)

- Unified operational status vocabulary: healthy, warning, elevated, critical; approved, pending, blocked; stale, live, cached.
- Alerts are informational (not alarming) and use subtle fills/borders.

File:

- `backend/src/ui/shared/operational_states.css`

***REMOVED******REMOVED*** Motion rules

File:

- `backend/src/ui/shared/operational_motion_rules.md`

***REMOVED******REMOVED*** Unresolved gaps / next priorities

- Apply the new panel role classes consistently across EN/TR pages (some remaining inline weights exist).
- Add a restrained graph style sheet specifically for relationship graph views (node spacing, edge hierarchy).
- Standardize evidence chips / lineage badges where repeated across surfaces.

