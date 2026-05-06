***REMOVED***!/usr/bin/env python3
"""
H-034 verification: semantic capability graph foundation.
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
    REPO_ROOT / "docs" / "H-034_SEMANTIC_CAPABILITY_GRAPH.md",
    REPO_ROOT / "docs" / "H-034_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "semantic_capability_graph" / "__init__.py",
    BACKEND / "src" / "semantic_capability_graph" / "capability_graph_registry.py",
    BACKEND / "src" / "semantic_capability_graph" / "capability_relationship_service.py",
    BACKEND / "src" / "semantic_capability_graph" / "capability_topology_service.py",
    BACKEND / "src" / "semantic_capability_graph" / "semantic_contract_service.py",
    BACKEND / "src" / "semantic_capability_graph" / "cross_capability_awareness_service.py",
    BACKEND / "src" / "semantic_capability_graph" / "capability_context_service.py",
    BACKEND / "src" / "semantic_capability_graph" / "capability_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "semantic_capability_graph_router.py",
    BACKEND / "tests" / "test_semantic_capability_graph.py",
    BACKEND / "src" / "ui" / "en" / "semantic_capability_graph_demo.html",
    BACKEND / "src" / "ui" / "tr" / "semantic_capability_graph_demo.html",
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


def graph_router_is_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    if "export_entity_registry" not in txt:
        return False
    if "from src.semantic_capability_graph.capability_graph_registry import export_entity_registry" not in txt:
        return False
    if "def summarize_topology" in txt or "def get_capability_graph" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-034 verification...", flush=True)

    for p in REQUIRED_FILES:
        if p.exists():
            ok(f"exists: {p.relative_to(REPO_ROOT)}")
        else:
            rc |= fail(f"missing {p.relative_to(REPO_ROOT)}")

    scanned = REQUIRED_FILES + [
        BACKEND / "src" / "semantic_capabilities" / "capability_export_service.py",
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
    if "semantic_capability_graph_router" in app_txt and "include_router(semantic_capability_graph_router" in app_txt:
        ok("app.py registers semantic_capability_graph_router")
    else:
        rc |= fail("app.py missing semantic_capability_graph_router")

    gr = BACKEND / "src" / "http" / "v1" / "semantic_capability_graph_router.py"
    if gr.exists():
        rt = gr.read_text(encoding="utf-8")
        if "semantic_capability_graph_foundation" not in rt:
            rc |= fail("router missing semantic_capability_graph_foundation envelope")
        else:
            ok("router defines governance envelope")
        if rt.count("autonomous_capability_discovery") < 1:
            rc |= fail("router missing autonomous_capability_discovery declaration")
        if not graph_router_is_thin(gr):
            rc |= fail("semantic graph router must delegate to services")
        else:
            ok("semantic graph router delegates to services")

    pkg = BACKEND / "src" / "semantic_capability_graph"
    if pkg.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in pkg.glob("*.py"))
        if UNSAFE_MARKERS.search(combined):
            rc |= fail("unsafe execution markers in semantic_capability_graph package")
        else:
            ok("no unsafe execution markers in semantic_capability_graph package")

    exp = BACKEND / "src" / "semantic_capabilities" / "capability_export_service.py"
    if exp.exists() and "build_h020_semantic_graph_extension" in exp.read_text(encoding="utf-8"):
        ok("capability_export_service integrates semantic graph extension")
    else:
        rc |= fail("capability_export_service missing H-034 integration")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-034 Semantic Capability Graph" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-034 section")
    else:
        rc |= fail("MainBook missing H-034")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-034 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-034 verification")
    else:
        rc |= fail("LiveBook missing H-034 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "H-034" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-034")
    else:
        rc |= fail("Master backlog missing H-034")

    for h in scan_secrets([p for p in scanned if p.exists() and p.suffix == ".py"]):
        rc |= fail(f"secret heuristic: {h}")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        try:
            for path in (
                "/api/v1/system/capabilities/graph",
                "/api/v1/system/capabilities/topology",
                "/api/v1/system/capabilities/contracts",
                "/api/v1/system/capabilities/runtime-context",
            ):
                req = Request(root + path, headers={"User-Agent": "verify-h034/1"})
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live GET {path} status {resp.status}")
                    body = json.loads(resp.read().decode("utf-8"))
                    if body.get("recursive_capability_mutation") is not False:
                        rc |= fail(f"live envelope invalid for {path}")
            cat_req = Request(root + "/api/v1/system/capabilities", headers={"User-Agent": "verify-h034/1"})
            with urlopen(cat_req, timeout=15) as cat_resp:
                cat_body = json.loads(cat_resp.read().decode("utf-8"))
                if cat_body.get("semantic_capability_graph", {}).get("schema_version") != "h034_v1":
                    rc |= fail("live catalog missing semantic_capability_graph extension")
            ok("live VERIFY_BASE_URL semantic graph smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h034-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h034-key")
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(BACKEND / "tests" / "test_semantic_capability_graph.py"), "-q"],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_semantic_capability_graph.py passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-034 verification complete." if rc == 0 else "FAIL: H-034 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
