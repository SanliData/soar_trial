"""
MODULE: knowledge_repository
PURPOSE: In-memory append-only store for foundation ingestion (H-024)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from src.knowledge_ingestion.knowledge_block_schema import KnowledgeBlock

_STORE: list[KnowledgeBlock] = []


def clear_blocks_for_tests() -> None:
    _STORE.clear()


def append_block(block: KnowledgeBlock) -> None:
    _STORE.append(block)


def list_blocks(*, limit: int = 50) -> list[KnowledgeBlock]:
    if limit < 1:
        limit = 1
    return _STORE[-limit:]


def all_blocks() -> list[KnowledgeBlock]:
    return list(_STORE)
