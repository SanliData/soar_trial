***REMOVED******REMOVED*** SOAR B2B / FinderOS — Deep UX Architecture (Part 2)

This document deepens the product UX architecture for FinderOS as an **operational intelligence platform**.

***REMOVED******REMOVED******REMOVED*** Core cognitive model (authority hierarchy)

FinderOS users are procurement operators and intelligence analysts. The UI must reinforce a strict authority order:

**Human intent → Workflow structure → Agent execution → Evidence → Result**

Operational rule: AI outputs are **downstream proposals**, never upstream of human decision.

---

***REMOVED******REMOVED*** 1) Navigation architecture — Two-rail system

***REMOVED******REMOVED******REMOVED*** Rail 1 (56px, always visible)

- **Icon-only** rail with 5 primary zones.
- Search and Settings pinned at bottom.
- Active zone indicated by **2px left accent** on the icon.
- No text labels, chevrons, or sub-menus.
- Goal: users can navigate without looking after habituation.

***REMOVED******REMOVED******REMOVED*** Rail 2 (148–220px, context-dependent)

Rail 2 is determined by the selected zone and provides persistent context that replaces “sub-navigation in content”.

Examples:
- **Cockpit zone**: active workflows, open approvals, pinned connectors
- **Results Hub zone**: active filter sets, saved searches, recent entities
- **Workflows zone**: stage progression for the current workflow

Why: keeps wayfinding out of the main working surface and reduces scroll past navigation elements.

---

***REMOVED******REMOVED*** 2) Cockpit — first 10 seconds

Cockpit is not a homepage. It is an instrument panel read in under 10 seconds.

Priority order:
1. **Is anything broken or blocked?**
2. **What requires my attention?** (approvals/escalations)
3. **What is running and at what stage?**
4. **Is the data fresh?**

Visual hierarchy:
- Top band is a **status bar** with segmented severity (gray/amber/red).
- The eye should land on the status band first, every time.

---

***REMOVED******REMOVED*** 3) Results Hub — anatomy of an intelligence card

The intelligence card is the most visible AI output surface.

Card rules:
- Left border encodes confidence at a glance (green/amber/red).
- AI attribution line is always present but secondary.
- “Why this appeared” uses a subtle interactive affordance (e.g., dotted underline).
- Evidence count is visible before actions (between body and actions).

---

***REMOVED******REMOVED*** 4) Explainability UX — trust architecture

Trust is earned through legibility. Explainability UI decisions must reduce ambiguity.

***REMOVED******REMOVED******REMOVED*** The three sins
- Confidence score without meaning.
- Evidence buried behind multiple steps.
- “AI-generated” labels used as warnings rather than attribution.

***REMOVED******REMOVED******REMOVED*** The three virtues
- Evidence is one click away and rendered **inline**, not a new tab.
- AI claims are **footnote-linked**, not assertions.
- Source chain uses operational language (“retrieved from SAM.gov, 2 hours ago”) not technical similarity numbers.

***REMOVED******REMOVED******REMOVED*** Evidence drawer (core trust artifact)

The evidence drawer should avoid:
- raw similarity scores
- model names
- embedding internals

Use:
- operational timestamps
- source authority/freshness
- provenance chain

Confidence breakdown:
- Use **bar metaphors** (magnitude without numeric worship).
Policy alignment:
- Use **checklists** (procurement mental model).

---

***REMOVED******REMOVED*** 5) Agent OS UX — preventing autonomy anxiety

User fear: “I don’t know what the system is doing.”

Principle:
**Scope boundaries are rendered as prominently as capabilities.**

Requirements:
- Display **CAN** and **CANNOT** lists with equal prominence.
- Shadow agent warning is a feature: visible detection proves governance.
- MCP governance is visible: what endpoints exist, scope limits, and restrictions.

---

***REMOVED******REMOVED*** 6) Retrieval + context UX — token budget as instrument

Token/context budget should be treated as a managed operational resource (fuel gauge).

Requirements:
- Context panel shows **budget** and **pressure**.
- Disabled expansion options should be **visible but disabled** (show constraints).
- Cache efficiency is a visible operational benefit (saved prefill/budget).

---

***REMOVED******REMOVED*** 7) AI interaction model — inline copilot (non-chat)

FinderOS must not feel like a chatbot. AI is integrated, but subordinate and scoped.

***REMOVED******REMOVED******REMOVED*** Surface 1 — Inline annotation (passive)
- AI content embedded in result cards and workflow summaries.
- Subtle attribution; evidence-linked.

***REMOVED******REMOVED******REMOVED*** Surface 2 — Contextual recommendation strip (semi-active)
- Bottom strip in workflow stages with 1–3 suggestions.
- Dismissible; no response required; each links to evidence.

***REMOVED******REMOVED******REMOVED*** Surface 3 — Inline copilot invocation (active, scoped)
- Command palette (`Ctrl/⌘K`) that is workflow-aware:
  - active workflow + stage
  - visible results
  - pending approvals
- Outputs structured prose (not chat bubbles), always with sources.
- No actions; evidence surfaced.

***REMOVED******REMOVED******REMOVED*** Surface 4 — Workflow copilot sidebar (deep active, optional)
- Optional right panel: “briefing ticker” on workflow progress.
- Dismissible; not chat; evidence-linked commentary.

---

***REMOVED******REMOVED*** Screens not yet wireframed (recommended next)

- Two-rail shell (Rail 1 + Rail 2) with zone-specific Rail 2 templates
- Results Hub card spec (confidence strip + evidence band + why affordance)
- Evidence drawer + confidence breakdown + policy checklist layout
- Context budget panel (pressure + disabled expansions + cache benefit)
- Command palette interaction spec (inputs, output format, evidence linking)

