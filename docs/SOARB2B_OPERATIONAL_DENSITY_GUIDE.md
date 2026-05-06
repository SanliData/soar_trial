***REMOVED*** SOAR B2B / FinderOS — Operational Density Guide

FinderOS is designed for **8-hour operational usage**. Density is not “more stuff”; it is **more signal per glance** with preserved readability, hierarchy, and explainability.

***REMOVED******REMOVED*** Information hierarchy (scan order)

- **Primary**: What requires attention now (queues, blocked states, elevated risk).
- **Secondary**: Why it matters (evidence, lineage, policy alignment, confidence).
- **Tertiary**: Metadata for audit (timestamps, workflow IDs, agent IDs, token counts).

***REMOVED******REMOVED*** Panel density rules

- Keep panels **short, scannable, and structured**:
  - Header: title + one short meta line.
  - Body: 1–3 “signal blocks” (tiles, table, timeline slice).
  - Details: expandable (`details`) for audit depth.
- Avoid walls of text. Prefer:
  - Key/value rows
  - Short bullets
  - Tables for repeated structures

***REMOVED******REMOVED*** Cognitive load rules

- Use **grayscale-first** UI; reserve color for state and meaning.
- Minimize competing emphasis:
  - Only one “attention color” per panel.
  - Prefer borders/left-rails over filled alarm blocks.
- Keep typography restrained:
  - No huge headings.
  - Body text is stable and readable.

***REMOVED******REMOVED*** Progressive disclosure

- Default view shows:
  - What happened
  - Severity
  - One-line explanation
- Expand to reveal:
  - Evidence links
  - Lineage/source references
  - Full payload / audit fields

***REMOVED******REMOVED*** Operational focus zones

- **Top row**: current posture (pressure, approvals, connector health).
- **Left rail (main)**: work queue and timeline.
- **Right rail (drawer)**: explainability, evidence, governance rationale.

***REMOVED******REMOVED*** Dashboard scanning behavior

Target “10-second scan”:

- 2 seconds: posture tiles (pressure/approvals/connectors).
- 4 seconds: queue/timeline “what changed”.
- 4 seconds: open 1 detail item for evidence / governance context.

***REMOVED******REMOVED*** What to avoid (fatigue patterns)

- Large empty whitespace “SaaS marketing” layouts.
- Continuous animations or shimmering.
- Overloaded dashboards with too many equal-weight tiles.
- Chat-centric AI surfaces that dominate operational work.

