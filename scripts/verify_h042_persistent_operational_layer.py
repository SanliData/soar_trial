***REMOVED***!/usr/bin/env python3
"""
H-042 verification: persistent workspace, graph intelligence, runtime clustering foundations.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND = REPO_ROOT / "backend"

REQUIRED_FILES = [
    REPO_ROOT / "docs" / "H-042_IMPLEMENTATION_PROOF.md",
    REPO_ROOT / "docs" / "H-042_PERSISTENT_OPERATIONAL_LAYER.md",
    BACKEND / "src" / "persistent_workspace" / "__init__.py",
    BACKEND / "src" / "persistent_workspace" / "typed_state_registry.py",
    BACKEND / "src" / "persistent_workspace" / "workspace_state_service.py",
    BACKEND / "src" / "persistent_workspace" / "cross_session_context_service.py",
    BACKEND / "src" / "persistent_workspace" / "persistent_workflow_service.py",
    BACKEND / "src" / "persistent_workspace" / "scheduled_execution_service.py",
    BACKEND / "src" / "persistent_workspace" / "state_snapshot_service.py",
    BACKEND / "src" / "persistent_workspace" / "workspace_indexing_service.py",
    BACKEND / "src" / "persistent_workspace" / "workspace_validation_service.py",
    BACKEND / "src" / "graph_intelligence" / "__init__.py",
    BACKEND / "src" / "graph_intelligence" / "graph_projection_service.py",
    BACKEND / "src" / "graph_intelligence" / "relationship_traversal_service.py",
    BACKEND / "src" / "graph_intelligence" / "hybrid_query_service.py",
    BACKEND / "src" / "graph_intelligence" / "graph_cache_service.py",
    BACKEND / "src" / "graph_intelligence" / "graph_reasoning_service.py",
    BACKEND / "src" / "graph_intelligence" / "graph_validation_service.py",
    BACKEND / "src" / "runtime_clustering" / "__init__.py",
    BACKEND / "src" / "runtime_clustering" / "embedding_cluster_service.py",
    BACKEND / "src" / "runtime_clustering" / "retrieval_partition_service.py",
    BACKEND / "src" / "runtime_clustering" / "dynamic_index_grouping_service.py",
    BACKEND / "src" / "runtime_clustering" / "semantic_batching_service.py",
    BACKEND / "src" / "runtime_clustering" / "cluster_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "persistent_workspace_router.py",
    BACKEND / "src" / "http" / "v1" / "graph_intelligence_router.py",
    BACKEND / "src" / "http" / "v1" / "runtime_clustering_router.py",
    BACKEND / "tests" / "test_persistent_operational_layer.py",
]

SECRET_PATTERNS = [
    (re.compile(r"(?i)sk_live_[0-9a-zA-Z]{16,}"), "Stripe-like"),
]

UNSAFE_MARKERS = re.compile(r"(?i)(\beval\s*\(|exec\s*\(|subprocess\.|socket\.socket\s*\()")


def ok(msg: str) -> None:
    print(f"PASS: {msg}", flush=True)


def fail(msg: str) -> int:
    print(f"FAIL: {msg}", flush=True)
    return 1


def has_bom(path: Path) -> bool:
    try:
        return path.read_bytes().startswith(b"\xef\xbb\xbf")
    except OSError:
        return False


def router_is_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    return "APIRouter(" in txt and "def export_" not in txt


def main() -> int:
    rc = 0
    print("H-042 verification...", flush=True)

    for p in REQUIRED_FILES:
        if p.exists():
            ok(f"exists: {p.relative_to(REPO_ROOT)}")
        else:
            rc |= fail(f"missing {p.relative_to(REPO_ROOT)}")

    scanned = REQUIRED_FILES + [
        BACKEND / "src" / "app.py",
        BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html",
        BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html",
        REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md",
        Path(__file__).resolve(),
    ]

    for p in scanned:
        if p.exists() and p.is_file():
            if has_bom(p):
                rc |= fail(f"BOM: {p.relative_to(REPO_ROOT)}")
            else:
                ok(f"No BOM: {p.relative_to(REPO_ROOT)}")

    app_txt = (BACKEND / "src" / "app.py").read_text(encoding="utf-8")
    for name, needle in (
        ("persistent_workspace_router", "persistent_workspace_router"),
        ("graph_intelligence_router", "graph_intelligence_router"),
        ("runtime_clustering_router", "runtime_clustering_router"),
    ):
        if needle in app_txt and f"include_router({needle}" in app_txt:
            ok(f"app.py registers {name}")
        else:
            rc |= fail(f"app.py missing {name}")

    for rel in (
        "http/v1/persistent_workspace_router.py",
        "http/v1/graph_intelligence_router.py",
        "http/v1/runtime_clustering_router.py",
    ):
        rp = BACKEND / "src" / rel
        if not router_is_thin(rp):
            rc |= fail(f"router must be thin (no export defs): {rel}")
        else:
            ok(f"thin router: {rel}")

    combined_pw = "".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in (BACKEND / "src" / "persistent_workspace").glob("*.py")
    )
    if UNSAFE_MARKERS.search(combined_pw):
        rc |= fail("unsafe markers in persistent_workspace")
    else:
        ok("persistent_workspace passes unsafe marker scan")

    combined_gi = "".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in (BACKEND / "src" / "graph_intelligence").glob("*.py")
    )
    if UNSAFE_MARKERS.search(combined_gi):
        rc |= fail("unsafe markers in graph_intelligence")
    else:
        ok("graph_intelligence passes unsafe marker scan")

    combined_rc = "".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in (BACKEND / "src" / "runtime_clustering").glob("*.py")
    )
    if UNSAFE_MARKERS.search(combined_rc):
        rc |= fail("unsafe markers in runtime_clustering")
    else:
        ok("runtime_clustering passes unsafe marker scan")

    reg = BACKEND / "src" / "persistent_workspace" / "typed_state_registry.py"
    if reg.exists() and "workflow_state" in reg.read_text(encoding="utf-8"):
        ok("typed state registry present")
    else:
        rc |= fail("typed_state_registry missing")

    sch = BACKEND / "src" / "persistent_workspace" / "scheduled_execution_service.py"
    if sch.exists() and "sch-permit-monitor" in sch.read_text(encoding="utf-8"):
        ok("scheduled workflows present")
    else:
        rc |= fail("scheduled_execution_service incomplete")

    trav = BACKEND / "src" / "graph_intelligence" / "relationship_traversal_service.py"
    if trav.exists() and "plan_relationship_traversal" in trav.read_text(encoding="utf-8"):
        ok("graph traversal present")
    else:
        rc |= fail("relationship_traversal_service incomplete")

    hyb = BACKEND / "src" / "graph_intelligence" / "hybrid_query_service.py"
    if hyb.exists() and "mandatory_graph_dependency" in hyb.read_text(encoding="utf-8"):
        ok("hybrid query present")
    else:
        rc |= fail("hybrid_query_service incomplete")

    emb = BACKEND / "src" / "runtime_clustering" / "embedding_cluster_service.py"
    if emb.exists():
        ok("runtime clustering embeddings present")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-042 Persistent Agent Workspace" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-042 section")
    else:
        rc |= fail("MainBook missing H-042")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-042 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-042 verification")
    else:
        rc |= fail("LiveBook missing H-042 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "***REMOVED******REMOVED*** H-042" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-042")
    else:
        rc |= fail("Master backlog missing H-042")

    docs_py = [p for p in scanned if p.exists() and p.suffix == ".py"]
    for p in docs_py:
        txt = p.read_text(encoding="utf-8", errors="replace")
        for rx, label in SECRET_PATTERNS:
            if rx.search(txt):
                rc |= fail(f"secret heuristic: {p.relative_to(REPO_ROOT)} ({label})")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        try:
            for path in (
                "/api/v1/system/workspace/state",
                "/api/v1/system/graph/traversals",
                "/api/v1/system/clustering/groups",
            ):
                req = Request(root + path, headers={"User-Agent": "verify-h042/1"})
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live GET {path} status {resp.status}")
                    json.loads(resp.read().decode("utf-8"))
            ok("live VERIFY_BASE_URL smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h042-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h042-key")
        out = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(BACKEND / "tests" / "test_persistent_operational_layer.py"),
                "-q",
            ],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_persistent_operational_layer.py passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-042 verification complete." if rc == 0 else "FAIL: H-042 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
