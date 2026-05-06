***REMOVED*** H-028 Implementation Proof — Relative Trajectory Evaluation & Agent Reward Layer

**Classification:** Foundation-Level Incremental  
**Recorded:** 2026-05-05  

---

***REMOVED******REMOVED*** Summary

Append-only **trajectory** registry, same-workflow **grouping**, **deterministic weighted** relative scoring from explicit `reasoning_metadata` facets, **template** comparison text, and **evaluation trace** persistence. Governance envelope: `reinforcement_learning_training=false`, `hidden_reasoning_exposure=none`. **No** RL training code paths.

**MainBook / LiveBook:** Section **26** (section 25 is H-027 in the current HTML TOC).

---

***REMOVED******REMOVED*** Deliverables

| Area | Paths |
|------|--------|
| Domain | `backend/src/trajectory_evaluation/` |
| Router | `backend/src/http/v1/trajectory_evaluation_router.py` |
| App | `backend/src/app.py` registers `trajectory_evaluation_router` |
| H-020 | `trajectory.create`, `trajectory.group`, `trajectory.evaluate`, `trajectory.list_groups` — **35** capabilities |
| Tests | `backend/tests/test_trajectory_evaluation.py` |
| Docs | `docs/H-028_TRAJECTORY_EVALUATION_LAYER.md`, this file |
| Books / backlog | MainBook §26, LiveBook §26, `docs/SOARB2B_MASTER_BACKLOG.md` |
| Demos | `backend/src/ui/en/trajectory_evaluation_demo.html`, `tr/` mirror |
| Verify | `scripts/verify_h028_trajectory_layer.py` |

---

***REMOVED******REMOVED*** Endpoints

| Method | Path |
|--------|------|
| POST | `/api/v1/system/trajectory` |
| POST | `/api/v1/system/trajectory/group` |
| POST | `/api/v1/system/trajectory/evaluate` |
| GET | `/api/v1/system/trajectory/groups` |
| GET | `/api/v1/system/trajectory/evaluations` |

---

***REMOVED******REMOVED*** Commands

```bash
python scripts/verify_h028_trajectory_layer.py
cd backend && python -m pytest tests/test_trajectory_evaluation.py tests/test_semantic_capabilities.py -q
python scripts/verify_h020_semantic_layer.py
```

---

***REMOVED******REMOVED*** PASS / FAIL

| Step | Result |
|------|--------|
| `verify_h028_trajectory_layer.py` | **PASS** (exit 0) |
| `pytest tests/test_trajectory_evaluation.py` | **PASS** (9 tests) |
| `pytest tests/test_trajectory_evaluation.py` + `test_semantic_capabilities.py` | **PASS** (19 tests) |
| `verify_h020_semantic_layer.py` | **PASS** (35 capability rows) |

**H-028 foundation implemented successfully.**

---

***REMOVED******REMOVED*** Unresolved issues

- In-memory store only — swap for durable storage when audit retention requires it.
- Weights are constants — calibrate with governance-approved telemetry later.

---

***REMOVED******REMOVED*** Next recommended step

Pipe normalized facet extraction from production workflows into `reasoning_metadata` so rankings reflect measured signals rather than manual demos only.
