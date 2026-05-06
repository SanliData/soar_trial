"""
MODULE: semantic_chunk_service
PURPOSE: Deterministic semantic chunking without LLMs (H-024)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import re
from typing import Iterable


def create_semantic_chunks(
    text: str,
    *,
    max_chunk_chars: int = 1800,
    min_paragraph_chars: int = 1,
) -> list[str]:
    """
    Split on paragraph boundaries first, then on single line breaks if a paragraph still exceeds max.
    Avoids naive fixed-size-only splitting.
    """
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", normalized) if p.strip()]
    chunks: list[str] = []
    for para in paragraphs:
        if len(para) <= max_chunk_chars:
            chunks.append(para)
            continue
        lines = [ln.strip() for ln in para.split("\n") if ln.strip()]
        buf: list[str] = []
        size = 0
        for ln in lines:
            add_len = len(ln) if not buf else len(ln) + 1
            if size + add_len > max_chunk_chars and buf:
                chunks.append("\n".join(buf))
                buf = [ln]
                size = len(ln)
            else:
                buf.append(ln)
                size += add_len
        if buf:
            chunks.append("\n".join(buf))
    # Drop trivial fragments when merging is possible later
    return [c for c in chunks if len(c) >= min_paragraph_chars or len(chunks) == 1]


def merge_related_chunks(chunks: Iterable[str], *, max_merge_chars: int = 2200) -> list[str]:
    """Merge consecutive small chunks to preserve section context within a size bound."""
    merged: list[str] = []
    buf: list[str] = []
    size = 0
    for c in chunks:
        c = c.strip()
        if not c:
            continue
        add = len(c) if not buf else len(c) + 2
        if size + add > max_merge_chars and buf:
            merged.append("\n\n".join(buf))
            buf = [c]
            size = len(c)
        else:
            buf.append(c)
            size += add
    if buf:
        merged.append("\n\n".join(buf))
    return merged


def summarize_chunk_structure(chunks: list[str]) -> dict[str, object]:
    """Structural summary only — no content generation."""
    lengths = [len(c) for c in chunks]
    return {
        "chunk_count": len(chunks),
        "total_chars": sum(lengths),
        "min_chunk_chars": min(lengths) if lengths else 0,
        "max_chunk_chars": max(lengths) if lengths else 0,
    }
