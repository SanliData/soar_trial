***REMOVED*** H-037 — Capability Gateway Layer (Foundation)

***REMOVED******REMOVED*** Purpose

Introduce a **governed** “MCP-style” capability gateway surface: static gateway registries, provider abstraction metadata, explicit execution policies, local-first inference **descriptors**, external tool governance (bounded chaining), browser automation **sandbox** rules, and hybrid serving **abstractions** — all returned via deterministic read APIs.

***REMOVED******REMOVED*** Architecture

- **Routers** expose JSON manifests only; **services** hold governance metadata.
- No outbound tool invocation or browser automation is executed in this foundation layer.

***REMOVED******REMOVED*** Components

| Area | Role |
|------|------|
| `mcp_gateway_registry` | Named gateways (`browser_intelligence`, `procurement_lookup`, …) with scope, trust, sandbox flags. |
| `provider_abstraction_service` | Uniform capability/restriction metadata per provider type; **explainable** `select_provider` routing table. |
| `capability_execution_policy` | Budgets, domain lists, rate limits, escalation labels per gateway. |
| `local_inference_service` | Offline/local inference slots — metadata only. |
| `external_tool_governance_service` | Tool trust, replay logging, **max_chain_depth=1**. |
| `browser_automation_policy_service` | Domain allowlists, session isolation, replay traces required. |
| `hybrid_serving_service` | Hosted vs local vs future internal vLLM placeholders — **no cluster rewrite**. |
| `gateway_validation_service` | Validates gateway names, scopes, rejects unsafe execution flags. |

***REMOVED******REMOVED*** HTTP API

Routes under `/api/v1/system/`:

- `GET /gateways`
- `GET /providers`
- `GET /execution-policies`
- `GET /local-inference`
- `GET /browser-policies`
- `GET /hybrid-serving`

Envelope always includes `capability_gateway_foundation: true` and negated risk flags for unrestricted execution, autonomous internet orchestration, and unrestricted tool chaining.

***REMOVED******REMOVED*** Explicitly deferred

- Unrestricted browser agents and autonomous internet orchestration.
- Open MCP marketplaces and arbitrary tool marketplaces.
- Distributed serving cluster rewrites or production MCP wiring.

***REMOVED******REMOVED*** Verification

```bash
python scripts/verify_h037_capability_gateway.py
cd backend && python -m pytest tests/test_capability_gateway.py tests/test_semantic_capabilities.py -q
```

Optional live smoke:

```bash
set VERIFY_BASE_URL=http://127.0.0.1:8000
python scripts/verify_h037_capability_gateway.py
```
