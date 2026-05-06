***REMOVED***!/usr/bin/env python3
"""
H-024 verification: structured knowledge ingestion foundation.
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
    REPO_ROOT / "docs" / "H-024_KNOWLEDGE_INGESTION_LAYER.md",
    REPO_ROOT / "docs" / "H-024_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "knowledge_ingestion" / "__init__.py",
    BACKEND / "src" / "knowledge_ingestion" / "knowledge_block_schema.py",
    BACKEND / "src" / "knowledge_ingestion" / "semantic_chunk_service.py",
    BACKEND / "src" / "knowledge_ingestion" / "authority_scoring_service.py",
    BACKEND / "src" / "knowledge_ingestion" / "freshness_scoring_service.py",
    BACKEND / "src" / "knowledge_ingestion" / "source_registry.py",
    BACKEND / "src" / "knowledge_ingestion" / "retrieval_policy_service.py",
    BACKEND / "src" / "knowledge_ingestion" / "ingestion_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "knowledge_ingestion_router.py",
    BACKEND / "tests" / "test_knowledge_ingestion.py",
    BACKEND / "src" / "ui" / "en" / "knowledge_ingestion_demo.html",
    BACKEND / "src" / "ui" / "tr" / "knowledge_ingestion_demo.html",
]

SCRAPING_FORBIDDEN = re.compile(
    r"(?i)(scrapy|playwright|bright\s*data|brightdata|apify|crawl4ai)"
)
SECRET_PATTERNS = [
    (re.compile(r"(?i)sk_live_[0-9a-zA-Z]{16,}"), "Stripe-like"),
]


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
    ***REMOVED*** Router should delegate; forbid heavy branching / scoring loops in router module.
    if re.search(r"\bfor\s+\w+\s+in\s+", txt):
        return False
    if "rank_blocks" in txt or "compute_authority" in txt or "create_semantic_chunks" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-024 verification...", flush=True)

    for p in REQUIRED_FILES:
        if p.exists():
            ok(f"exists: {p.relative_to(REPO_ROOT)}")
        else:
            rc |= fail(f"missing {p.relative_to(REPO_ROOT)}")

    scanned = REQUIRED_FILES + [
        BACKEND / "src" / "knowledge_ingestion" / "knowledge_repository.py",
        BACKEND / "src" / "knowledge_ingestion" / "knowledge_ingestion_service.py",
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
    if "knowledge_ingestion_router" in app_txt and "include_router(knowledge_ingestion_router" in app_txt:
        ok("app.py registers knowledge_ingestion_router")
    else:
        rc |= fail("app.py missing knowledge_ingestion_router")

    kr = BACKEND / "src" / "http" / "v1" / "knowledge_ingestion_router.py"
    if kr.exists():
        rt = kr.read_text(encoding="utf-8")
        if "deterministic_ingestion" not in rt:
            rc |= fail("router missing deterministic_ingestion envelope")
        else:
            ok("router defines deterministic_ingestion envelope")
        if not router_is_thin(kr):
            rc |= fail("router appears to contain business logic (keep delegation only)")
        else:
            ok("knowledge router delegates to services")

    pkg = BACKEND / "src" / "knowledge_ingestion"
    if pkg.is_dir():
        combined = ""
        for py in sorted(pkg.glob("*.py")):
            combined += py.read_text(encoding="utf-8", errors="replace")
        if SCRAPING_FORBIDDEN.search(combined):
            rc |= fail("forbidden scraping/crawl infra reference in knowledge_ingestion package")
        else:
            ok("no scraping infra markers in knowledge_ingestion")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-024 Context Acquisition" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-024 section")
    else:
        rc |= fail("MainBook missing H-024")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    lb_txt = lb.read_text(encoding="utf-8") if lb.exists() else ""
    if lb.exists() and "H-024 Verification" in lb_txt and "Knowledge Ingestion" in lb_txt:
        ok("LiveBook contains H-024 verification")
    else:
        rc |= fail("LiveBook missing H-024 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "H-024" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-024")
    else:
        rc |= fail("Master backlog missing H-024")

    reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if reg.exists():
        rtxt = reg.read_text(encoding="utf-8")
        for cid in ("knowledge.create_block", "knowledge.list_blocks", "knowledge.get_policies"):
            if cid not in rtxt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("semantic registry lists knowledge capabilities")

    for h in scan_secrets([p for p in scanned if p.exists() and p.suffix == ".py"]):
        rc |= fail(f"secret heuristic: {h}")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        try:
            payload = {
                "block_type": "market_signal",
                "title": "Live verify",
                "content": "Deterministic content.",
                "source_lineage": {"source_type": "uploaded_documents", "source_record_id": "live-1"},
                "freshness_days": 5,
            }
            req_b = Request(
                root + "/api/v1/system/knowledge/block",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "verify-h024/1"},
                method="POST",
            )
            with urlopen(req_b, timeout=15) as resp:
                status_b = resp.status
                body_b = json.loads(resp.read().decode("utf-8"))
            if status_b != 200:
                rc |= fail(f"live POST block status {status_b}")
            if body_b.get("deterministic_ingestion") is not True:
                rc |= fail("live block missing deterministic_ingestion")
            req_l = Request(root + "/api/v1/system/knowledge/blocks?limit=10", headers={"User-Agent": "verify-h024/1"})
            with urlopen(req_l, timeout=15) as resp_l:
                status_l = resp_l.status
                body_l = json.loads(resp_l.read().decode("utf-8"))
            if status_l != 200:
                rc |= fail(f"live GET blocks status {status_l}")
            req_p = Request(root + "/api/v1/system/knowledge/policies", headers={"User-Agent": "verify-h024/1"})
            with urlopen(req_p, timeout=15) as resp_p:
                status_p = resp_p.status
                body_p = json.loads(resp_p.read().decode("utf-8"))
            if status_p != 200:
                rc |= fail(f"live GET policies status {status_p}")
            if "weights" not in body_p.get("policies", {}):
                rc |= fail("live policies missing weights")
            ok("live VERIFY_BASE_URL smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h024-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h024-key")
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(BACKEND / "tests" / "test_knowledge_ingestion.py"), "-q"],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_knowledge_ingestion.py passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-024 verification complete." if rc == 0 else "FAIL: H-024 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
