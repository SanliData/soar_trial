***REMOVED*** H-043 — Long-Context Sparse Inference, Private Runtime Hardening & Ensemble Governance

***REMOVED******REMOVED*** Scope

Governed foundation for adaptive (explainable) context loading plans, deterministic context pressure and sparse-provider **metadata**, private runtime isolation and network-exposure **detection**, and ensemble evaluation with **public** weights and consensus scoring — without autonomous swarms, public default runtimes, hidden MoE weighting, or giant sparse infra.

***REMOVED******REMOVED*** Packages

| Package | Role |
|---------|------|
| `long_context_runtime` | Adaptive loader, partitions, pressure, sparse metadata, retrieval fallback, validation, H-041 bridge hooks |
| `private_runtime_security` | Mesh policy, isolation, boundaries, exposure assessment, Tailscale governance, non-root preference |
| `ensemble_governance` | Multi-evaluator manifest, consensus math, variance flags, seeded rotation |

***REMOVED******REMOVED*** HTTP (all `GET`, prefix `/api/v1`)

**Context:** `/system/context/pressure`, `/partitions`, `/sparse-providers`, `/fallbacks`  
**Runtime:** `/system/runtime/isolation`, `/network-exposure`, `/private-mesh`, `/non-root`  
**Ensemble:** `/system/ensemble/evaluators`, `/consensus`, `/variance`, `/randomization`

***REMOVED******REMOVED*** Integrations

- **H-037:** `sparse_long_context_metadata_by_provider` on provider export (metadata only).
- **H-040:** Skills extended with `context_weight`, `partition_priority`, `retrieval_fallback_allowed`, `sparse_reasoning_compatible`.
- **H-041:** Telemetry and prefill manifests include H-043 hooks; token budgets add `ensemble_evaluation` and ensemble-aware flags.
- **H-039:** `runtime_inference_alignment` adds H-043 exposure detections (**detection only**).

***REMOVED******REMOVED*** Explicitly deferred

Autonomous internet-scale swarms, unrestricted long-context workflows, giant sparse inference platforms, hidden ensemble weights, uncontrolled network exposure defaults.

***REMOVED******REMOVED*** Verification

```bash
python scripts/verify_h043_long_context_private_runtime.py
cd backend && python -m pytest tests/test_h043_long_context_private_runtime.py -q
```
