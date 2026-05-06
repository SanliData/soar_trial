***REMOVED*** H-041 — Inference Runtime Governance Layer

***REMOVED******REMOVED*** Purpose

Provide a **production foundation** for governed inference: deterministic token budgets, KV cache **metadata**, continuous batching **abstractions**, explainable telemetry, collapse-risk **detection**, prefill pressure classification, parallelism caps, speculative execution **metadata**, and cost estimation — **without** autonomous scheduling, recursive orchestration loops, or hidden tuning.

***REMOVED******REMOVED*** Components

| Module | Role |
|--------|------|
| `kv_cache_registry` | Workflow KV metadata: scope, signatures, reuse flags, estimated savings |
| `continuous_batching_service` | Workflow grouping & batch eligibility metadata |
| `runtime_token_budget_service` | Categories: orchestration, reflection, evaluation, skill_activation, retrieval, graph_reasoning |
| `prefill_decode_optimizer` | Prefill/decode guidance only — no mutation |
| `inference_cost_governance_service` | Deterministic USD estimates from documented rates |
| `speculative_execution_service` | Candidate/rollback/confidence metadata — no uncontrolled execution |
| `runtime_parallelism_service` | Caps for workflows, tokens, retries |
| `runtime_telemetry_service` | Canonical explainable telemetry shape |
| `runtime_collapse_detection_service` | Rule-based flags — **detection only** |
| `prefill_pressure_service` | Levels: low, moderate, high, critical |
| `runtime_efficiency_service` | Weighted score with explicit weights |
| `inference_validation_service` | Validate budgets, batching, parallelism, speculative meta, KV, telemetry |

***REMOVED******REMOVED*** HTTP API

Base: `/api/v1/system/inference`

- `/kv-cache`, `/batching`, `/token-budgets`, `/costs`, `/parallelism`, `/speculative`, `/telemetry`, `/collapse-risk`, `/prefill-pressure`, `/efficiency` (includes prefill/decode guidance JSON)

Envelope negates uncontrolled expansion, autonomous scheduling, recursive orchestration.

***REMOVED******REMOVED*** Integrations

- **H-040**: Skills optionally expose `estimated_token_cost`, `prefill_weight`, `cache_eligibility`, `batching_eligibility`, `runtime_efficiency_score` (metadata).
- **H-039**: `GET /api/v1/system/firewall/gateways` includes `runtime_inference_alignment` — anomaly **signals** aligned with firewall policy domains; **no autonomous blocking** from this manifest.

***REMOVED******REMOVED*** Explicitly deferred

- Giant vLLM rewrites and custom CUDA kernels.
- Uncontrolled speculative execution and self-tuning runtimes.

***REMOVED******REMOVED*** Verification

```bash
python scripts/verify_h041_inference_runtime.py
cd backend && python -m pytest tests/test_inference_runtime.py -q
```
