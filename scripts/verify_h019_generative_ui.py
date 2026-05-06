***REMOVED***!/usr/bin/env python3
"""
H-019 verification: controlled Generative UI foundation.
Exit code 0 only if all checks pass.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND = REPO_ROOT / "backend"


REQUIRED_FILES = [
    REPO_ROOT / "docs" / "H-019_GENERATIVE_UI_FOUNDATION.md",
    BACKEND / "src" / "services" / "generative_ui" / "__init__.py",
    BACKEND / "src" / "services" / "generative_ui" / "schemas.py",
    BACKEND / "src" / "services" / "generative_ui" / "widget_registry.py",
    BACKEND / "src" / "services" / "generative_ui" / "validation_service.py",
    BACKEND / "src" / "services" / "generative_ui" / "generation_service.py",
    BACKEND / "src" / "http" / "v1" / "generative_ui_router.py",
    BACKEND / "src" / "ui" / "en" / "soarb2b_generative_ui_demo.html",
    BACKEND / "src" / "ui" / "tr" / "soarb2b_generative_ui_demo.html",
    BACKEND / "tests" / "test_generative_ui.py",
]

SECRET_PATTERNS = [
    (re.compile(r"(?i)sk_live_[0-9a-zA-Z]{16,}"), "Stripe live key"),
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
    hits = []
    for p in paths:
        if not p.exists() or p.suffix not in {".py", ".html", ".md"}:
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        for rx, label in SECRET_PATTERNS:
            if rx.search(txt):
                hits.append(f"{p.relative_to(REPO_ROOT)} ({label})")
    return hits


def app_contains_router() -> bool:
    txt = (BACKEND / "src" / "app.py").read_text(encoding="utf-8")
    return "generative_ui_router" in txt and '/api/v1/b2b' in txt and 'include_router(generative_ui_router' in txt


def router_registers_path() -> bool:
    txt = (BACKEND / "src" / "http" / "v1" / "generative_ui_router.py").read_text(encoding="utf-8")
    return '"/generative-ui/render"' in txt or "'/generative-ui/render'" in txt


def main() -> int:
    rc = 0
    print("H-019 verification...", flush=True)

    for p in REQUIRED_FILES:
        if not p.exists():
            rc |= fail(f"Missing file: {p.relative_to(REPO_ROOT)}")
        else:
            ok(f"exists: {p.relative_to(REPO_ROOT)}")

    scanned = REQUIRED_FILES + [
        BACKEND / "src" / "app.py",
        BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html",
        BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html",
        REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md",
    ]

    for p in scanned:
        if p.exists() and p.is_file():
            if has_bom(p):
                rc |= fail(f"UTF-8 BOM in {p.relative_to(REPO_ROOT)}")
            else:
                ok(f"No BOM: {p.relative_to(REPO_ROOT)}")

    for h in scan_secrets([p for p in scanned if p.exists()]):
        rc |= fail(f"Secret pattern?: {h}")

    if app_contains_router():
        ok("app.py registers generative_ui_router under /api/v1/b2b")
    else:
        rc |= fail("app.py missing generative_ui_router include")

    if router_registers_path():
        ok("Router defines POST /generative-ui/render")
    else:
        rc |= fail("generative_ui_router.py missing route path")

    wr = BACKEND / "src" / "services" / "generative_ui" / "widget_registry.py"
    wtxt = wr.read_text(encoding="utf-8")
    _wt_missing = False
    for wt in ("executive_briefing", "graph_summary", "market_signal_cockpit", "opportunity_cluster"):
        if wt not in wtxt:
            rc |= fail(f"Missing widget_type in registry file: {wt}")
            _wt_missing = True
    if not _wt_missing:
        ok("Allowed widget types listed in widget_registry.py")

    demo_en = BACKEND / "src" / "ui" / "en" / "soarb2b_generative_ui_demo.html"
    demo_txt = demo_en.read_text(encoding="utf-8")
    if 'sandbox=""' not in demo_txt and 'sandbox="' not in demo_txt:
        rc |= fail("EN demo missing iframe sandbox attribute")
    else:
        ok("EN demo includes iframe sandbox")

    mb = (BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html").read_text(encoding="utf-8")
    if "H-019 Controlled Generative UI Foundation" not in mb:
        rc |= fail("MainBook missing H-019 section heading")
    else:
        ok("MainBook contains H-019 section heading")

    lb = (BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html").read_text(encoding="utf-8")
    if "17. H-019 Verification" not in lb and "H-019 Verification — Controlled Generative UI" not in lb:
        rc |= fail("LiveBook missing H-019 verification section")
    else:
        ok("LiveBook contains H-019 verification")

    ml = (REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md").read_text(encoding="utf-8")
    if "***REMOVED******REMOVED*** H-019" not in ml:
        rc |= fail("Master backlog missing H-019")
    else:
        ok("Master backlog contains H-019")

    gs = BACKEND / "src" / "services" / "generative_ui" / "generation_service.py"
    gs_txt = gs.read_text(encoding="utf-8")
    ast.parse(gs_txt)
    if "sandbox_required=True" not in gs_txt or "runtime_js_allowed=False" not in gs_txt:
        rc |= fail("generation_service.py must set sandbox_required=True and runtime_js_allowed=False")
    else:
        ok("generation_service hard-codes sandbox/runtime flags")

    try:
        from pydantic import TypeAdapter

        sys.path.insert(0, str(BACKEND))

        os.environ.setdefault("JWT_SECRET", "verify-h019-jwt")
        os.environ.setdefault("QUOTE_SECRET", "verify-h019-quote-verify-h019-quote")
        from src.services.generative_ui.schemas import GenerativeUiRenderRequest
        from src.services.generative_ui.validation_service import validate_render_request

        try:
            TypeAdapter(GenerativeUiRenderRequest).validate_python(
                {"widget_type": "__invalid__", "title": "t"}
            )
            rc |= fail("Pydantic should reject invalid widget_type")
        except Exception:
            ok("validation rejects unknown widget_type at schema layer")

        v = validate_render_request(
            GenerativeUiRenderRequest.model_validate(
                {
                    "widget_type": "executive_briefing",
                    "title": "Demo",
                    "summary": "S",
                    "metrics": [],
                    "recommendations": [],
                }
            )
        )
        assert v.widget_type == "executive_briefing"
        ok("validate_render_request accepts executive_briefing")
    except Exception as e:
        rc |= fail(f"Service import/validation check failed: {e}")

    base = os.getenv("VERIFY_BASE_URL", "").strip().rstrip("/")
    if base:
        url = f"{base}/api/v1/b2b/generative-ui/render"
        key = os.getenv("VERIFY_API_KEY", "").strip()
        if not key:
            print("INFO: VERIFY_BASE_URL set but VERIFY_API_KEY empty; skipping live POST", flush=True)
        else:
            import json

            body = json.dumps(
                {
                    "widget_type": "executive_briefing",
                    "title": "Live check",
                    "summary": "Test",
                    "metrics": [],
                    "recommendations": [],
                }
            ).encode("utf-8")
            req = Request(
                url,
                data=body,
                headers={"Content-Type": "application/json", "X-API-Key": key, "User-Agent": "verify_h019/1.0"},
                method="POST",
            )
            try:
                with urlopen(req, timeout=12) as resp:
                    raw = resp.read().decode("utf-8")
                data = __import__("json").loads(raw)
                if resp.status != 200:
                    rc |= fail(f"Live POST status {resp.status}")
                if not data.get("sandbox_required"):
                    rc |= fail("Live response sandbox_required not true")
                if data.get("runtime_js_allowed"):
                    rc |= fail("Live response runtime_js_allowed must be false")
                if "<script" in (data.get("html") or "").lower():
                    rc |= fail("Live HTML must not contain script tag")
                ok("Live POST render check passed")
            except HTTPError as e:
                rc |= fail(f"Live POST HTTPError: {e.code}")
            except URLError as e:
                rc |= fail(f"Live POST URLError: {e.reason}")

    try:
        env = os.environ.copy()
        ***REMOVED*** Force deterministic key for subprocess; `.env` is still overridden by tests after import.
        env["SOARB2B_API_KEYS"] = "test-genui-api-key"
        env.setdefault("JWT_SECRET", "verify-h019-pytest-jwt-secret-32chars!!")
        env.setdefault("QUOTE_SECRET", "verify-h019-quote-verify-h019-quote-32")
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(BACKEND / "tests" / "test_generative_ui.py"), "-q"],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest generative_ui failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_generative_ui.py passed")
    except Exception as e:
        rc |= fail(f"Could not run pytest: {e}")

    if rc == 0:
        print("PASS: H-019 verification complete.", flush=True)
    else:
        print("FAIL: H-019 verification incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
