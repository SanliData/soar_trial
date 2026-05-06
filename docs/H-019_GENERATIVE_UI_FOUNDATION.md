***REMOVED*** H-019 — Controlled Generative UI Foundation

***REMOVED******REMOVED*** What “Open Generative UI” / runtime AI UI means

In an unconstrained interpretation, models generate UI markup or scripts at runtime that the host application injects directly into the DOM. That pattern can surface dynamic dashboards and explanations quickly, but it expands the trusted computing base to include model output as executable intent.

***REMOVED******REMOVED*** Why SOAR B2B uses controlled mode now

Commercial Intelligence positioning requires explainability, provenance discipline, and security boundaries. Ship model-driven UX only when rendering is deterministic, audited, sandboxed, and template-bound—not when models can freely emit scripts or steer the parent shell.

***REMOVED******REMOVED*** Approved first use cases (foundation)

Structured widgets only:

- Results Hub **AI briefing** widget (`executive_briefing`)
- **Intelligence Graph** summary widget (`graph_summary`)
- **Market signals** cockpit widget (`market_signal_cockpit`)
- **Opportunity cluster** summary widget (`opportunity_cluster`)

***REMOVED******REMOVED*** Explicitly rejected (for now)

- Unrestricted arbitrary HTML generation
- Arbitrary JavaScript execution in the parent application
- Parent DOM access from generated markup
- Cookie or `localStorage` access from generated UI contexts (sandbox blocks)

***REMOVED******REMOVED*** Security model

- **`iframe sandbox`**: host embeds server-returned snippets in isolated frames without relaxing sandbox unless externally reviewed.
- **No parent access**: generated fragments must not rely on scripts that reach `window.parent`.
- **No credentials exposed**: API calls use standard B2B auth; payloads must not embed secrets or tokens inside HTML.
- **Template-bound rendering**: only allowlisted widgets; all dynamic text escaped server-side (`html.escape`).
- **Allowlist of widget types**: enforced in `widget_registry.py` plus Pydantic `Literal`.

***REMOVED******REMOVED*** Implementation status

- **Foundation Implemented** — structured render API, deterministic templates, no LLM calls, no raw HTML ingestion.
- **Full Runtime Deferred** — model-authored scripts, unrestricted HTML/CSS, hybrid client composition.

***REMOVED******REMOVED*** Verification method

Run:

```bash
python scripts/verify_h019_generative_ui.py
cd backend
python -m pytest tests/test_generative_ui.py -q
```

Optional live check (`VERIFY_BASE_URL` set):

```bash
VERIFY_BASE_URL=http://127.0.0.1:9000 python scripts/verify_h019_generative_ui.py
```

Manual: open `/ui/en/soarb2b_generative_ui_demo.html` or `/ui/tr/soarb2b_generative_ui_demo.html`; confirm iframe `sandbox` and no `<script>` in embedded HTML payload.
