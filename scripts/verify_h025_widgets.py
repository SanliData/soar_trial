***REMOVED***!/usr/bin/env python3
"""
H-025 verification: interactive intelligence widget layer foundation.
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
    REPO_ROOT / "docs" / "H-025_INTERACTIVE_WIDGET_LAYER.md",
    REPO_ROOT / "docs" / "H-025_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "intelligence_widgets" / "__init__.py",
    BACKEND / "src" / "intelligence_widgets" / "widget_contracts.py",
    BACKEND / "src" / "intelligence_widgets" / "widget_registry.py",
    BACKEND / "src" / "intelligence_widgets" / "widget_render_service.py",
    BACKEND / "src" / "intelligence_widgets" / "widget_validation_service.py",
    BACKEND / "src" / "intelligence_widgets" / "widget_state_service.py",
    BACKEND / "src" / "http" / "v1" / "intelligence_widget_router.py",
    BACKEND / "tests" / "test_intelligence_widgets.py",
    BACKEND / "src" / "ui" / "en" / "intelligence_widgets_demo.html",
    BACKEND / "src" / "ui" / "tr" / "intelligence_widgets_demo.html",
]

SECRET_PATTERNS = [
    (re.compile(r"(?i)sk_live_[0-9a-zA-Z]{16,}"), "Stripe-like"),
]

FORBIDDEN_ROUTER = re.compile(r"(?i)\b(model\s*context\s*protocol|\bmcp\b.*rewrite)")
SCRIPT_OPEN = re.compile(r"(?i)<\s*script\b")


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
    if "<section" in txt or "<script" in txt.lower():
        return False
    if "html.escape(" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-025 verification...", flush=True)

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
    if "intelligence_widget_router" in app_txt and "include_router(intelligence_widget_router" in app_txt:
        ok("app.py registers intelligence_widget_router")
    else:
        rc |= fail("app.py missing intelligence_widget_router")

    kr = BACKEND / "src" / "http" / "v1" / "intelligence_widget_router.py"
    if kr.exists():
        rt = kr.read_text(encoding="utf-8")
        if "deterministic_rendering" not in rt:
            rc |= fail("router missing deterministic_rendering envelope")
        else:
            ok("router defines deterministic_rendering envelope")
        if not router_is_thin(kr):
            rc |= fail("router appears to embed render logic")
        else:
            ok("widget router delegates to services")

    reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if reg.exists():
        rtxt = reg.read_text(encoding="utf-8")
        for cid in ("widgets.render", "widgets.list_types", "widgets.demo"):
            if cid not in rtxt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("semantic registry lists widget capabilities")

    rw = BACKEND / "src" / "intelligence_widgets" / "widget_render_service.py"
    if rw.exists() and "html.escape" in rw.read_text(encoding="utf-8"):
        ok("widget_render_service uses html escaping")
    else:
        rc |= fail("widget_render_service missing escape helper usage")

    if (BACKEND / "src" / "intelligence_widgets" / "widget_render_service.py").exists():
        sys.path.insert(0, str(BACKEND))
        try:
            from src.intelligence_widgets.widget_render_service import build_demo_payload

            payload = build_demo_payload()
            for frag in payload.get("html_fragments") or []:
                if SCRIPT_OPEN.search(frag):
                    rc |= fail("demo HTML fragment contains script tag")
            ok("demo fragments contain no raw script tags")
        except Exception as exc:
            rc |= fail(f"demo payload scan: {exc}")
        finally:
            try:
                sys.path.remove(str(BACKEND))
            except ValueError:
                pass

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-025 Interactive Intelligence Widget" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-025 section")
    else:
        rc |= fail("MainBook missing H-025")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-025 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-025 verification")
    else:
        rc |= fail("LiveBook missing H-025 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "H-025" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-025")
    else:
        rc |= fail("Master backlog missing H-025")

    for h in scan_secrets([p for p in scanned if p.exists() and p.suffix == ".py"]):
        rc |= fail(f"secret heuristic: {h}")

    intel_dir = BACKEND / "src" / "intelligence_widgets"
    if intel_dir.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in intel_dir.glob("*.py"))
        if FORBIDDEN_ROUTER.search(combined):
            rc |= fail("unexpected MCP migration rhetoric in intelligence_widgets")
        ok("no MCP rewrite markers in package")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        try:
            payload = {
                "widget_type": "executive_summary_card",
                "title": "Live test",
                "authority_level": "low",
                "freshness_days": 3,
                "interactive": False,
                "visualization_type": "card",
                "data": {},
            }
            req_r = Request(
                root + "/api/v1/system/widgets/render",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "verify-h025/1"},
                method="POST",
            )
            with urlopen(req_r, timeout=15) as resp:
                status_r = resp.status
                body_r = json.loads(resp.read().decode("utf-8"))
            if status_r != 200:
                rc |= fail(f"live POST render status {status_r}")
            if body_r.get("deterministic_rendering") is not True:
                rc |= fail("live render envelope missing deterministic_rendering")
            req_t = Request(root + "/api/v1/system/widgets/types", headers={"User-Agent": "verify-h025/1"})
            with urlopen(req_t, timeout=15) as resp_t:
                status_t = resp_t.status
                body_t = json.loads(resp_t.read().decode("utf-8"))
            if status_t != 200:
                rc |= fail(f"live GET types status {status_t}")
            req_d = Request(root + "/api/v1/system/widgets/demo", headers={"User-Agent": "verify-h025/1"})
            with urlopen(req_d, timeout=15) as resp_d:
                status_d = resp_d.status
                body_d = json.loads(resp_d.read().decode("utf-8"))
            if status_d != 200:
                rc |= fail(f"live GET demo status {status_d}")
            ok("live VERIFY_BASE_URL smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h025-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h025-key")
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(BACKEND / "tests" / "test_intelligence_widgets.py"), "-q"],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_intelligence_widgets.py passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-025 verification complete." if rc == 0 else "FAIL: H-025 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
