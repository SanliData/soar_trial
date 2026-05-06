***REMOVED***!/usr/bin/env python3
"""
Verify repository documentation/proof baseline (META: task implementation standard).

Exit code 0 only if canonical files exist, books reference Section 19, backlog links standard.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def bom(path: Path) -> bool:
    try:
        return path.read_bytes().startswith(b"\xef\xbb\xbf")
    except OSError:
        return False


def main() -> int:
    rc = 0
    print("TASK_STANDARD verification...", flush=True)

    canon = REPO / "docs" / "TASK_IMPLEMENTATION_AND_PROOF_STANDARD.md"
    proof = REPO / "docs" / "TASK_STANDARD_IMPLEMENTATION_PROOF.md"
    rule = REPO / ".cursor" / "rules" / "ta<REDACTED_OPENAI_API_KEY>.mdc"
    verify_self = Path(__file__).resolve()

    for p, label in (
        (canon, "canonical standard doc"),
        (proof, "TASK_STANDARD proof report"),
        (rule, "Cursor rule mdc"),
    ):
        if p.exists():
            print(f"PASS: exists {p.relative_to(REPO)}", flush=True)
            if bom(p):
                print(f"FAIL: BOM in {p}", flush=True)
                rc = 1
        else:
            print(f"FAIL: missing {label}: {p}", flush=True)
            rc = 1

    mb = REPO / "backend" / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    lb = REPO / "backend" / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    backlog = REPO / "docs" / "SOARB2B_MASTER_BACKLOG.md"

    for p in (mb, lb, backlog, verify_self):
        if not p.exists():
            print(f"FAIL: missing {p.relative_to(REPO)}", flush=True)
            rc = 1

    if mb.exists():
        txt = mb.read_text(encoding="utf-8")
        need = ("19.", "TASK_IMPLEMENTATION_AND_PROOF_STANDARD.md")
        if all(n in txt for n in need):
            print("PASS: MainBook Section 19 references standard doc", flush=True)
        else:
            print("FAIL: MainBook missing Section 19 / standard pointer", flush=True)
            rc = 1

    if lb.exists():
        txt = lb.read_text(encoding="utf-8")
        if "19." in txt and "TASK_IMPLEMENTATION_AND_PROOF_STANDARD.md" in txt:
            print("PASS: LiveBook Section 19 references verification of standard doc", flush=True)
        else:
            print("FAIL: LiveBook missing Section 19 standard verification", flush=True)
            rc = 1

    if backlog.exists():
        btxt = backlog.read_text(encoding="utf-8")
        if "TASK_IMPLEMENTATION_AND_PROOF_STANDARD.md" in btxt:
            print("PASS: Master backlog mentions canonical standard doc", flush=True)
        else:
            print("FAIL: Master backlog missing canonical standard pointer", flush=True)
            rc = 1

    for p in (canon, proof, rule):
        if p.exists() and not bom(p):
            print(f"PASS: No BOM {p.relative_to(REPO)}", flush=True)

    print("PASS: TASK_STANDARD verification complete." if rc == 0 else "FAIL: TASK_STANDARD incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
