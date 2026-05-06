***REMOVED*** H-028 — Relative Trajectory Evaluation & Agent Reward Layer

**Scope:** Foundation only (in-process registry, deterministic rules, no training stack).

***REMOVED******REMOVED*** Purpose

Enterprise SOAR B2B workflows often lack a single “gold” answer. **Relative evaluation** compares two or more **candidate trajectories** (same workflow, comparable input) and ranks them using **explicit, auditable signals** instead of a single binary pass/fail.

This layer stores:

- **Trajectory** records (immutable append preferred; no API deletion in this foundation).
- **Trajectory groups** for same-`workflow_name` comparison sets.
- **RelativeEvaluation** results with **ranked IDs**, a **template-built `scoring_reasoning` string**, and structured `evaluation_metadata` (per-trajectory score breakdown).

***REMOVED******REMOVED*** Relative evaluation (not online RL)

Deterministic steps:

1. Register trajectories with `reasoning_metadata` numeric facets (defaults apply when absent).
2. Create a group referencing ≥ 2 trajectory IDs sharing `workflow_name`.
3. Run `/evaluate` → weighted linear composite score, lexicographic tie-break by `trajectory_id`.

Ranking factors (weights fixed in `relative_scoring_service.py`):

| Facet | Role |
|-------|------|
| `commercial_usefulness` | Procurement / deal relevance |
| `graph_consistency` | Relationship coherence vs graph context |
| `geographic_relevance` | Region alignment |
| `structured_output_quality` | Contract / schema adherence |
| `hallucination_risk` | Higher is worse (score uses \(1 - risk\)) |
| `verbosity_excess` | Penalizes overly long / noisy outputs |

***REMOVED******REMOVED*** Comparison reasoning

`comparison_reasoning_service.py` emits short **template phrases** when dimension deltas exceed a small epsilon (no client-visible hidden scratchpad). Tie-break explanations reference the deterministic ordering rule.

***REMOVED******REMOVED*** Relationship to GRPO-style ideas

**GRPO** (group-relative preference optimization) trains policies from group-wise comparisons. SOAR’s foundation borrows the **group-and-rank** shape **without** policy gradients, GPU clusters, or weight updates—same-process scoring only.

***REMOVED******REMOVED*** Trajectory groups

Groups enforce:

- Non-empty `trajectory_ids`.
- Every trajectory exists.
- All members share the **same** `workflow_name` as the group header.

***REMOVED******REMOVED*** Evaluation traces

Each evaluation is appended to the store (`evaluation_trace_service`) with immutable metadata—no silent mutation of prior trajectory scores.

***REMOVED******REMOVED*** Explicit deferrals

- RL training infrastructure (PPO, GRPO clusters, distributed trainers).
- Online model / policy weight updates.
- Autonomous self-improving agents or self-training loops.
- GPU orchestration for learning.

***REMOVED******REMOVED*** HTTP surface

| Method | Path |
|--------|------|
| POST | `/api/v1/system/trajectory` |
| POST | `/api/v1/system/trajectory/group` |
| POST | `/api/v1/system/trajectory/evaluate` |
| GET | `/api/v1/system/trajectory/groups` |
| GET | `/api/v1/system/trajectory/evaluations` |

Governance envelope keys on responses:

- `deterministic_trajectory_evaluation=true`
- `reinforcement_learning_training=false`
- `hidden_reasoning_exposure=none`

***REMOVED******REMOVED*** Verification

```bash
python scripts/verify_h028_trajectory_layer.py
cd backend && python -m pytest tests/test_trajectory_evaluation.py -q
```
