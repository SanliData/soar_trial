***REMOVED***!/usr/bin/env python3
"""
H-021 verification: inference-aware AI runtime foundation.
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
    REPO_ROOT / "docs" / "H-021_AI_RUNTIME_OPTIMIZATION_LAYER.md",
    BACKEND / "src" / "ai_runtime" / "__init__.py",
    BACKEND / "src" / "ai_runtime" / "runtime_schema.py",
    BACKEND / "src" / "ai_runtime" / "token_budget_service.py",
    BACKEND / "src" / "ai_runtime" / "prompt_compaction_service.py",
    BACKEND / "src" / "ai_runtime" / "model_routing_service.py",
    BACKEND / "src" / "ai_runtime" / "inference_profile_service.py",
    BACKEND / "src" / "ai_runtime" / "runtime_telemetry_service.py",
    BACKEND / "src" / "http" / "v1" / "ai_runtime_router.py",
    BACKEND / "tests" / "test_ai_runtime.py",
]

FORBIDDEN_IMPORT_SNIPPETS = ("vllm", "tensorrt", "triton", "deepspeed")
REQ_FILES_TO_SCAN = [
    BACKEND / "requirements.txt",
    BACKEND / "requirements_b2b.txt",
    BACKEND / "requirements-optional.txt",
]

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


def scan_ai_runtime_py(paths: list[Path]) -> list[str]:
    hits: list[str] = []
    for p in paths:
        if not p.exists() or p.suffix != ".py":
            continue
        txt = p.read_text(encoding="utf-8", errors="replace").lower()
        for needle in FORBIDDEN_IMPORT_SNIPPETS:
            if needle in txt:
                hits.append(f"{p.relative_to(REPO_ROOT)} contains forbidden token '{needle}'")
    return hits


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


def main() -> int:
    rc = 0
    print("H-021 verification...", flush=True)

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
        REPO_ROOT / "docs" / "H-021_IMPLEMENTATION_PROOF.md",
        Path(__file__).resolve(),
    ]

    for p in scanned:
        if p.exists() and p.is_file():
            if has_bom(p):
                rc |= fail(f"BOM: {p.relative_to(REPO_ROOT)}")
            else:
                ok(f"No BOM: {p.relative_to(REPO_ROOT)}")

    app_txt = (BACKEND / "src" / "app.py").read_text(encoding="utf-8")
    if "ai_runtime_router" in app_txt and "include_router(ai_runtime_router" in app_txt:
        ok("app.py registers ai_runtime_router under /api/v1")
    else:
        rc |= fail("app.py missing ai_runtime_router")

    rt = (BACKEND / "src" / "http" / "v1" / "ai_runtime_router.py").read_text(encoding="utf-8")
    if '"/profile"' in rt or "'/profile'" in rt:
        ok("ai_runtime router exposes POST /profile")
    else:
        rc |= fail("ai_runtime_router missing /profile")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-021 Inference-Aware AI Runtime" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-021 section heading")
    else:
        rc |= fail("MainBook missing H-021")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-021 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-021 verification heading")
    else:
        rc |= fail("LiveBook missing H-021 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "H-021" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-021")
    else:
        rc |= fail("Master backlog missing H-021")

    reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if reg.exists():
        rtxt = reg.read_text(encoding="utf-8")
        if "ai_runtime.profile" in rtxt and "ai_runtime.list_profiles" in rtxt:
            ok("semantic capability registry lists ai_runtime endpoints")
        else:
            rc |= fail("capability_registry missing ai_runtime rows")

    tb = BACKEND / "src" / "ai_runtime" / "token_budget_service.py"
    if tb.exists() and "estimate_tokens" in tb.read_text(encoding="utf-8"):
        ok("token_budget_service exports estimator")

    pc = BACKEND / "src" / "ai_runtime" / "prompt_compaction_service.py"
    if pc.exists() and "Context compacted deterministically" in pc.read_text(encoding="utf-8"):
        ok("prompt compaction marker present")

    mr = BACKEND / "src" / "ai_runtime" / "model_routing_service.py"
    if mr.exists() and "economy-reasoner" in mr.read_text(encoding="utf-8"):
        ok("model routing placeholders present")

    _ai_dir = BACKEND / "src" / "ai_runtime"
    _py_paths = [_ai_dir / n for n in (
        "__init__.py",
        "runtime_schema.py",
        "token_budget_service.py",
        "prompt_compaction_service.py",
        "model_routing_service.py",
        "inference_profile_service.py",
        "runtime_telemetry_service.py",
    )] + [BACKEND / "src" / "http" / "v1" / "ai_runtime_router.py"]
    for h in scan_ai_runtime_py(_py_paths):
        rc |= fail(f"Forbidden dependency hint: {h}")

    for req in REQ_FILES_TO_SCAN:
        if req.exists():
            low = req.read_text(encoding="utf-8", errors="replace").lower()
            for needle in ("vllm", "tensorrt", "cuda", "triton", "deepspeed"):
                if needle in low:
                    rc |= fail(f"{req.relative_to(REPO_ROOT)} contains forbidden token '{needle}'")

    for h in scan_secrets([p for p in scanned if p.exists() and p.suffix == ".py"]):
        rc |= fail(f"secret heuristic: {h}")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        url = base_url.rstrip("/") + "/api/v1/system/ai-runtime/profile"
        payload = {
            "task": {
                "task_id": "demo-h021",
                "task_type": "executive_briefing",
                "requested_quality_tier": "standard",
                "max_input_tokens": 500,
                "max_output_tokens": 300,
                "latency_target_ms": 3000,
                "allow_compaction": True,
                "preferred_model": None,
            },
            "input_context": "Long sample commercial intelligence context " * 120,
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = Request(
                url,
                data=data,
                headers={"Content-Type": "application/json", "User-Agent": "verify-h021/1"},
                method="POST",
            )
            with urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8")
                body = json.loads(raw)
            if resp.status != 200:
                rc |= fail(f"live POST status {resp.status}")
            if body.get("llm_invoked") is not False:
                rc |= fail("live response llm_invoked must be false")
            prof = body.get("profile") or {}
            if not prof.get("selected_model"):
                rc |= fail("live profile missing selected_model")
            if prof.get("estimated_total_tokens") is None:
                rc |= fail("live profile missing estimated_total_tokens")
            ok("live POST /ai-runtime/profile smoke passed")
        except HTTPError as exc:
            rc |= fail(f"live POST HTTPError {exc.code}")
        except URLError as exc:
            rc |= fail(f"live POST URLError {exc.reason}")
        except json.JSONDecodeError:
            rc |= fail("live POST not JSON")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h021-jwt-secret-32characters!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h021-key")
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(BACKEND / "tests" / "test_ai_runtime.py"), "-q"],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest test_ai_runtime failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_ai_runtime.py passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher error: {exc}")

    print("PASS: H-021 verification complete." if rc == 0 else "FAIL: H-021 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
