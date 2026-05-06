***REMOVED***!/usr/bin/env python3
"""
SOAR B2B / FinderOS strategic hardening verification.

Goals:
- Verify required files exist
- Verify MainBook/LiveBook contain required new sections
- Scan changed text files for UTF-8 BOM
- Scan changed docs/code for obvious secret patterns (exclude placeholders/examples)
- Optionally hit local or live URLs if VERIFY_BASE_URL is set

Exit codes:
  0 = PASS
  1 = FAIL
"""

from __future__ import annotations

import os
import re
import sys
import subprocess
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


REPO_ROOT = Path(__file__).resolve().parent.parent


REQUIRED_FILES = [
    REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md",
    REPO_ROOT / "backend" / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html",
    REPO_ROOT / "backend" / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html",
]


SECTION_CHECKS = [
    (
        REPO_ROOT / "backend" / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html",
        "16. Strategic Hardening Backlog",
    ),
    (
        REPO_ROOT / "backend" / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html",
        "16. Verification Protocol for Strategic Hardening",
    ),
]


SECRET_PATTERNS = [
    (re.compile(r"(?i)aws_access_key_id\s*=\s*['\"][A-Z0-9]{16,}['\"]"), "AWS access key id assignment"),
    (re.compile(r"(?i)aws_secret_access_key\s*=\s*['\"][A-Za-z0-9/+=]{20,}['\"]"), "AWS secret access key assignment"),
    (re.compile(r"(?i)sk_live_[0-9a-zA-Z]{16,}"), "Stripe live secret key"),
    (re.compile(r"(?i)rk_live_[0-9a-zA-Z]{16,}"), "Stripe live restricted key"),
    (re.compile(r"(?i)xox[baprs]-[0-9A-Za-z-]{10,}"), "Slack token"),
    (re.compile(r"(?i)-----BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY-----"), "Private key block"),
    (re.compile(r"(?i)password\\s*[:=]\\s*['\"][^'\"]{8,}['\"]"), "Hardcoded password assignment"),
    (re.compile(r"(?i)api[_-]?key\\s*[:=]\\s*['\"][^'\"]{16,}['\"]"), "Hardcoded API key assignment"),
    (re.compile(r"(?i)client_secret\\s*[:=]\\s*['\"][^'\"]{12,}['\"]"), "OAuth client secret assignment"),
]

***REMOVED*** Allowlist for placeholders/examples
SECRET_ALLOWLIST = [
    re.compile(r"your-"),  ***REMOVED*** docs placeholders
    re.compile(r"example", re.IGNORECASE),
    re.compile(r"placeholder", re.IGNORECASE),
    re.compile(r"test", re.IGNORECASE),
    re.compile(r"dummy", re.IGNORECASE),
    re.compile(r"admin-dev-key-12345"),  ***REMOVED*** explicit dev default (not secret)
]


def _print(msg: str) -> None:
    print(msg, flush=True)


def fail(msg: str) -> int:
    _print(f"FAIL: {msg}")
    return 1


def ok(msg: str) -> None:
    _print(f"PASS: {msg}")


def run_git_diff_name_only() -> list[Path]:
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=str(REPO_ROOT),
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except Exception as e:
        _print(f"INFO: Could not run git diff --name-only: {e}")
        return []

    if not out:
        return []
    paths: list[Path] = []
    for line in out.splitlines():
        p = (REPO_ROOT / line.strip()).resolve()
        if p.exists():
            paths.append(p)
    return paths


def is_text_file(path: Path) -> bool:
    ***REMOVED*** Keep it simple and safe.
    text_ext = {
        ".py", ".md", ".txt", ".html", ".js", ".css", ".json", ".yml", ".yaml", ".sh", ".ps1", ".toml", ".ini",
    }
    return path.suffix.lower() in text_ext


def has_utf8_bom(path: Path) -> bool:
    try:
        b = path.read_bytes()
    except Exception:
        return False
    return b.startswith(b"\xef\xbb\xbf")


def contains_section(path: Path, needle: str) -> bool:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        ***REMOVED*** Try with BOM-sig to avoid false negatives
        content = path.read_text(encoding="utf-8-sig")
    return needle in content


def scan_for_secrets(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for p in paths:
        if not is_text_file(p):
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        ***REMOVED*** Skip allowlisted files that are expected to contain example env-like text.
        ***REMOVED*** We still scan, but we will ignore allowlisted matches.
        for rx, label in SECRET_PATTERNS:
            for m in rx.finditer(content):
                snippet = content[max(0, m.start() - 40) : min(len(content), m.end() + 40)]
                if any(a.search(snippet) for a in SECRET_ALLOWLIST):
                    continue
                findings.append(f"{p.relative_to(REPO_ROOT)}: {label}")
                break
    return findings


def http_get(url: str, timeout_s: int = 8) -> tuple[bool, str]:
    req = Request(url, headers={"User-Agent": "verify_soarb2b_hardening/1.0"})
    try:
        with urlopen(req, timeout=timeout_s) as resp:
            status = getattr(resp, "status", 200)
            return (200 <= status < 300), f"HTTP {status}"
    except HTTPError as e:
        return False, f"HTTP {e.code}"
    except URLError as e:
        return False, f"URL error: {e.reason}"
    except Exception as e:
        return False, f"Error: {e}"


def main() -> int:
    rc = 0
    _print("SOAR B2B hardening verification starting...")

    ***REMOVED*** 1) Required files
    for f in REQUIRED_FILES:
        if not f.exists():
            rc = 1
            _print(f"FAIL: Missing required file: {f.relative_to(REPO_ROOT)}")
        else:
            ok(f"Required file exists: {f.relative_to(REPO_ROOT)}")

    ***REMOVED*** 2) Section checks
    for path, needle in SECTION_CHECKS:
        if not path.exists():
            rc = 1
            _print(f"FAIL: Section check skipped (file missing): {path.relative_to(REPO_ROOT)}")
            continue
        if contains_section(path, needle):
            ok(f"Section present in {path.relative_to(REPO_ROOT)}: {needle}")
        else:
            rc = 1
            _print(f"FAIL: Missing section in {path.relative_to(REPO_ROOT)}: {needle}")

    ***REMOVED*** 3) Changed files (BOM + secrets)
    changed = run_git_diff_name_only()
    if not changed:
        _print("INFO: No changed files detected via git diff --name-only HEAD. Scanning required files only.")
        changed = list(set(REQUIRED_FILES + [p for p, _ in SECTION_CHECKS]))

    bom_hits = [p for p in changed if is_text_file(p) and has_utf8_bom(p)]
    if bom_hits:
        rc = 1
        for p in bom_hits:
            _print(f"FAIL: UTF-8 BOM detected: {p.relative_to(REPO_ROOT)}")
    else:
        ok("UTF-8 BOM scan: no BOM detected in scanned files")

    secret_hits = scan_for_secrets(changed)
    if secret_hits:
        rc = 1
        for h in secret_hits:
            _print(f"FAIL: Secret pattern match: {h}")
    else:
        ok("Secret scan: no obvious secrets detected in scanned files")

    ***REMOVED*** 4) Optional URL checks
    base = os.getenv("VERIFY_BASE_URL") or os.getenv("BASE_URL")
    if base:
        base = base.rstrip("/")
        _print(f"INFO: Running URL checks against: {base}")
        urls = [
            f"{base}/health",
            f"{base}/healthz",
            f"{base}/readyz",
            f"{base}/ui/tr/soarb2b_home.html",
            f"{base}/ui/en/soarb2b_home.html",
        ]
        for u in urls:
            ok_flag, msg = http_get(u)
            if ok_flag:
                ok(f"URL reachable: {u} ({msg})")
            else:
                rc = 1
                _print(f"FAIL: URL check failed: {u} ({msg})")
    else:
        _print("INFO: VERIFY_BASE_URL not set. Skipping URL checks.")

    if rc == 0:
        _print("PASS: All checks passed.")
    else:
        _print("FAIL: One or more checks failed.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

