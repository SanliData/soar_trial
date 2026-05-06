***REMOVED***!/usr/bin/env python3
"""
H-026 verification: commercial graph intelligence foundation.
Exit code 0 only if structural checks + pytest pass.
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
    REPO_ROOT / "docs" / "H-026_GRAPH_COMMERCIAL_INTELLIGENCE.md",
    REPO_ROOT / "docs" / "H-026_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "commercial_graph" / "__init__.py",
    BACKEND / "src" / "commercial_graph" / "entity_schema.py",
    BACKEND / "src" / "commercial_graph" / "relationship_registry.py",
    BACKEND / "src" / "commercial_graph" / "graph_traversal_service.py",
    BACKEND / "src" / "commercial_graph" / "commercial_graph_builder.py",
    BACKEND / "src" / "commercial_graph" / "graph_reasoning_service.py",
    BACKEND / "src" / "commercial_graph" / "graph_confidence_service.py",
    BACKEND / "src" / "http" / "v1" / "commercial_graph_router.py",
    BACKEND / "tests" / "test_commercial_graph.py",
    BACKEND / "src" / "ui" / "en" / "commercial_graph_demo.html",
    BACKEND / "src" / "ui" / "tr" / "commercial_graph_demo.html",
]

SECRET_PATTERNS = [
    (re.compile(r"(?i)sk_live_[0-9a-zA-Z]{16,}"), "Stripe-like"),
]

FORBIDDEN_DB = re.compile(r"(?i)(neo4j|falkordb|neo4j-driver)")


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


def scan_secrets(paths: list[Path]) -> list[str]:
    bad: list[str] = []
    for p in paths:
        if not p.exists() or p.suffix not in {".py", ".md"}:
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        for rx, label in SECRET_PATTERNS:
            if rx.search(txt):
                bad.append(f"{p.relative_to(REPO_ROOT)} ({label})")
    return bad


def router_is_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    if "<section" in txt or "_ADJ_OUT" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-026 verification...", flush=True)

    for p in REQUIRED_FILES:
        if p.exists():
            ok(f"exists: {p.relative_to(REPO_ROOT)}")
        else:
            rc |= fail(f"missing {p.relative_to(REPO_ROOT)}")

    scanned = REQUIRED_FILES + [
        BACKEND / "src" / "app.py",
        BACKEND / "src" / "semantic_capabilities" / "capability_registry.py",
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
    if "commercial_graph_router" in app_txt and "include_router(commercial_graph_router" in app_txt:
        ok("app.py registers commercial_graph_router")
    else:
        rc |= fail("app.py missing commercial_graph_router")

    kr = BACKEND / "src" / "http" / "v1" / "commercial_graph_router.py"
    if kr.exists():
        rt = kr.read_text(encoding="utf-8")
        if "deterministic_graph" not in rt:
            rc |= fail("router missing deterministic_graph envelope")
        else:
            ok("router defines deterministic_graph envelope")
        if not router_is_thin(kr):
            rc |= fail("router appears to embed graph storage logic")
        else:
            ok("commercial graph router delegates to services")

    cg = BACKEND / "src" / "commercial_graph"
    if cg.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in cg.glob("*.py"))
        if FORBIDDEN_DB.search(combined):
            rc |= fail("unexpected dedicated graph DB driver references in commercial_graph")
        ok("no Neo4j/FalkorDB driver markers in commercial_graph")

    reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if reg.exists():
        rtxt = reg.read_text(encoding="utf-8")
        for cid in (
            "graph.create_entity",
            "graph.create_relationship",
            "graph.traverse",
            "graph.list_relationships",
        ):
            if cid not in rtxt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("semantic registry lists graph capabilities")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-026 Graph-Centric" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-026 section")
    else:
        rc |= fail("MainBook missing H-026")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-026 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-026 verification")
    else:
        rc |= fail("LiveBook missing H-026 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "H-026" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-026")
    else:
        rc |= fail("Master backlog missing H-026")

    for h in scan_secrets([p for p in scanned if p.exists() and p.suffix == ".py"]):
        rc |= fail(f"secret heuristic: {h}")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        try:
            ent = {
                "entity_type": "company",
                "name": "VerifyCo",
                "authority_score": 0.82,
                "freshness_days": 4,
            }
            req_e = Request(
                root + "/api/v1/system/graph/entity",
                data=json.dumps(ent).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "verify-h026/1"},
                method="POST",
            )
            with urlopen(req_e, timeout=15) as resp:
                status_e = resp.status
                body_e = json.loads(resp.read().decode("utf-8"))
            if status_e != 200:
                rc |= fail(f"live POST entity status {status_e}")
            eid = body_e["entity"]["entity_id"]
            req_t = Request(root + f"/api/v1/system/graph/traverse?entity_id={eid}&depth=1")
            with urlopen(req_t, timeout=15) as resp_t:
                status_t = resp_t.status
                body_t = json.loads(resp_t.read().decode("utf-8"))
            if status_t != 200:
                rc |= fail(f"live GET traverse status {status_t}")
            if body_t.get("deterministic_graph") is not True:
                rc |= fail("live traverse envelope")
            ok("live VERIFY_BASE_URL smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h026-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h026-key")
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(BACKEND / "tests" / "test_commercial_graph.py"), "-q"],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_commercial_graph.py passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-026 verification complete." if rc == 0 else "FAIL: H-026 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
