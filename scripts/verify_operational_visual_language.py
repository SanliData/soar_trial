#!/usr/bin/env python3
"""
SCRIPT: verify_operational_visual_language
PURPOSE: Verify SOAR B2B Operational Visual Language System deliverables exist and are wired
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    details: str = ""


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _exists(rel: str) -> Check:
    p = ROOT / rel
    return Check(name=f"exists:{rel}", ok=p.exists(), details=str(p))


def _contains(rel: str, needle: str) -> Check:
    p = ROOT / rel
    if not p.exists():
        return Check(name=f"contains:{rel}", ok=False, details="missing file")
    txt = _read_text(p)
    ok = needle in txt
    return Check(name=f"contains:{rel}", ok=ok, details=f"needle={needle!r}")


def _not_contains(rel: str, needle: str) -> Check:
    p = ROOT / rel
    if not p.exists():
        return Check(name=f"not_contains:{rel}", ok=False, details="missing file")
    txt = _read_text(p)
    ok = needle not in txt
    return Check(name=f"not_contains:{rel}", ok=ok, details=f"needle={needle!r}")


def main() -> int:
    checks: list[Check] = []

    # Shared CSS foundations
    for rel in [
        "backend/src/ui/shared/operational_tokens.css",
        "backend/src/ui/shared/operational_typography.css",
        "backend/src/ui/shared/operational_spacing.css",
        "backend/src/ui/shared/operational_panels.css",
        "backend/src/ui/shared/operational_states.css",
        "backend/src/ui/shared/operational_timeline.css",
        "backend/src/ui/shared/operational_components.css",
    ]:
        checks.append(_exists(rel))

    # Typography rules: medium/regular only (guardrail via tokens and no 650/700 in typography file)
    checks.append(_contains("backend/src/ui/shared/operational_tokens.css", "--op-weight-regular: 400"))
    checks.append(_contains("backend/src/ui/shared/operational_tokens.css", "--op-weight-medium: 500"))
    checks.append(_not_contains("backend/src/ui/shared/operational_typography.css", "font-weight: 650"))
    checks.append(_not_contains("backend/src/ui/shared/operational_typography.css", "font-weight: 700"))

    # AI text treatment exists
    checks.append(_contains("backend/src/ui/shared/operational_components.css", ".op-ai-block"))
    checks.append(_contains("backend/src/ui/shared/operational_components.css", ".op-ai-attrib"))

    # Docs deliverables
    for rel in [
        "docs/SOARB2B_OPERATIONAL_DENSITY_GUIDE.md",
        "docs/SOARB2B_VISUAL_ANTI_PATTERNS.md",
        "backend/src/ui/shared/operational_motion_rules.md",
        "docs/OPERATIONAL_VISUAL_LANGUAGE_REPORT.md",
        "docs/OPERATIONAL_VISUAL_LANGUAGE_IMPLEMENTATION_PROOF.md",
    ]:
        checks.append(_exists(rel))

    # MainBook / LiveBook sections
    checks.append(_contains("backend/docs/main_book/FinderOS_MainBook_v0.1.html", "48E. Operational Visual Language System"))
    checks.append(_contains("backend/docs/live_book/FinderOS_LiveBook_2025-12-13.html", "48E. Verification — Operational Visual System"))

    # Print
    failures = 0
    for c in checks:
        tag = "OK " if c.ok else "BAD"
        print(f"{tag} {c.name} {c.details}".rstrip())
        if not c.ok:
            failures += 1

    if failures:
        print(f"\nOperational visual language verification: FAIL ({failures} failing checks)")
        return 1

    print("\nOperational visual language verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

