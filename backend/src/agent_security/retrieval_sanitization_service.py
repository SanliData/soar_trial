"""
MODULE: retrieval_sanitization_service
PURPOSE: Deterministic retrieval/HTML hygiene — poisoning indicators (H-029)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import re
from typing import Any

_SCRIPT_RX = re.compile(r"(?is)<script\b[^>]*>.*?</script>")
_STYLE_HIDING_RX = re.compile(r"(?i)display\s*:\s*none")
_TOOL_DIRECTIVE_RX = re.compile(r"(?i)\b(invoke_tool|call_mcp|execute_tool)\s*\(")
_BIDI_RX = re.compile(r"[\u202a-\u202e]")


def sanitize_retrieval(content: str, content_type: str = "html") -> dict[str, Any]:
    findings: list[str] = []
    text = content

    if _SCRIPT_RX.search(text):
        findings.append("script_tag_removed")
        text = _SCRIPT_RX.sub("", text)

    if _STYLE_HIDING_RX.search(text):
        findings.append("css_hidden_content_detected")

    if _TOOL_DIRECTIVE_RX.search(text):
        findings.append("suspicious_tool_directive")

    if _BIDI_RX.search(text):
        findings.append("bidi_override_characters_stripped")
        text = _BIDI_RX.sub("", text)

    meta_noise = re.findall(r"(?i)<meta\b[^>]*>", text)
    if len(meta_noise) > 12:
        findings.append("excessive_meta_tags")

    modified = text != content or bool(findings)
    return {
        "sanitized_content": text.strip(),
        "content_type": content_type,
        "findings": findings,
        "modified": modified,
    }
