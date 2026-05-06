"""
MODULE: chunk_compression_service
PURPOSE: Chunk-level deterministic compression metadata (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.selective_context_runtime.selective_context_validation_service import validate_chunk_record


def compress_chunk_deterministically(
    *,
    chunk_id: str,
    text: str,
    source_lineage: dict[str, Any],
    expansion_allowed: bool = True,
    max_chars: int = 600,
) -> dict[str, Any]:
    cid = (chunk_id or "").strip()
    if not cid:
        raise ValueError("invalid chunk_id")
    if not isinstance(source_lineage, dict) or not source_lineage:
        raise ValueError("source_lineage required")

    original_tokens = max(0, int(len(text or "") / 4))
    compact = (text or "").strip().replace("\n", " ")
    if len(compact) > max_chars:
        compact = compact[: max_chars - 40].rstrip() + " …[chunk truncated]"
    compressed_tokens = max(0, int(len(compact) / 4))
    ratio = 1.0 if original_tokens <= 0 else round(compressed_tokens / float(original_tokens), 4)

    out = {
        "chunk_id": cid,
        "original_token_estimate": original_tokens,
        "compressed_token_estimate": compressed_tokens,
        "compression_ratio": ratio,
        "source_lineage": dict(source_lineage),
        "expansion_allowed": bool(expansion_allowed),
        "deterministic": True,
        "llm_invoked": False,
    }
    validate_chunk_record(out)
    return out

