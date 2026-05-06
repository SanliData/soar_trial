"""
MODULE: typed_context_projection_service
PURPOSE: Project H-045 retrieval/chunk/command artifacts into H-044 typed contexts (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.context_orchestration.knowledge_context_service import build_knowledge_context
from src.context_orchestration.memory_context_service import build_memory_context


def project_compressed_chunk_context(
    *,
    chunk_id: str,
    workflow_scope: str,
    compressed_summary: str,
    source_type: str,
    source_record_id: str,
) -> dict[str, Any]:
    ***REMOVED*** Represent chunk summaries as knowledge_context with tags (no new context_type introduced).
    return build_knowledge_context(
        context_id=f"chunk-cmpr::{chunk_id}",
        workflow_scope=workflow_scope,
        summary=compressed_summary,
        source_type=source_type,
        source_record_id=source_record_id,
        parent_document_id=None,
        priority=58,
        isolation_required=True,
        tags=["compressed_chunk_context", "selective_context_runtime"],
    )


def project_expanded_chunk_context(
    *,
    chunk_id: str,
    workflow_scope: str,
    expanded_summary: str,
    source_type: str,
    source_record_id: str,
) -> dict[str, Any]:
    return build_knowledge_context(
        context_id=f"chunk-full::{chunk_id}",
        workflow_scope=workflow_scope,
        summary=expanded_summary,
        source_type=source_type,
        source_record_id=source_record_id,
        parent_document_id=None,
        priority=62,
        isolation_required=True,
        tags=["expanded_chunk_context", "selective_context_runtime"],
    )


def project_connector_context(
    *,
    connector_name: str,
    workflow_scope: str,
    connector_summary: str,
) -> dict[str, Any]:
    return build_memory_context(
        context_id=f"connector::{connector_name}",
        workflow_scope=workflow_scope,
        summary=connector_summary,
        source_type="connector_registry",
        source_record_id=connector_name,
        priority=45,
        isolation_required=True,
        tags=["connector_context", "federated_retrieval"],
    )


def project_agent_operational_context(
    *,
    agent_id: str,
    workflow_scope: str,
    operational_summary: str,
) -> dict[str, Any]:
    return build_memory_context(
        context_id=f"agent_ops::{agent_id}",
        workflow_scope=workflow_scope,
        summary=operational_summary,
        source_type="agent_registry",
        source_record_id=agent_id,
        priority=52,
        isolation_required=True,
        tags=["agent_operational_context", "agent_os"],
    )


def project_command_audit_context(
    *,
    command_id: str,
    workflow_scope: str,
    audit_summary: str,
) -> dict[str, Any]:
    return build_memory_context(
        context_id=f"command_audit::{command_id}",
        workflow_scope=workflow_scope,
        summary=audit_summary,
        source_type="command_audit_log",
        source_record_id=command_id,
        priority=48,
        isolation_required=True,
        tags=["command_audit_context", "nl_control_plane"],
    )

