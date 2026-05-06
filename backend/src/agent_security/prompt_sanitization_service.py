"""
MODULE: prompt_sanitization_service
PURPOSE: Deterministic prompt hygiene — detect injections / overrides (H-029)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import re
from typing import Any

# Suspicious instruction patterns (case-insensitive)
_INJECTION_RX = [
    re.compile(r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+(instructions|rules)\b"),
    re.compile(r"(?i)\[?\s*system\s*\]?\s*:\s*"),
    re.compile(r"(?i)\b(system|developer)\s*:\s*"),
    re.compile(r"(?i)\byou\s+are\s+now\b"),
    re.compile(r"(?i)\bdisregard\s+(the\s+)?(policy|rules)\b"),
    re.compile(r"(?i)<\s*/?\s*system\s*>"),
    re.compile(r"(?i)\[\s*INST\s*\]"),
]

_ZW_RE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")


def sanitize_prompt(text: str) -> dict[str, Any]:
    findings: list[str] = []
    original = text
    t = _ZW_RE.sub("", text)

    for rx in _INJECTION_RX:
        if rx.search(t):
            findings.append(f"matched_pattern:{rx.pattern[:48]}")

    # Neutralize obvious delimiter abuse (deterministic strip, not semantic rewriting)
    if "</system>" in t.lower() or "<system>" in t.lower():
        findings.append("xml_style_role_tags")
        t = re.sub(r"(?i)</?system>", "", t)

    modified = t != original or bool(findings)
    return {
        "sanitized_text": t.strip(),
        "findings": findings,
        "modified": modified,
        "hidden_markup_removed": original != _ZW_RE.sub("", original),
    }
