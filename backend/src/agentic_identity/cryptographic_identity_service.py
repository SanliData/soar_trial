"""
MODULE: cryptographic_identity_service
PURPOSE: Cryptographic-style identity metadata (deterministic; no real keys) (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import hashlib
from typing import Any

from src.agentic_identity.agent_identity_registry import export_identity_registry


def _fingerprint(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def export_cryptographic_identities() -> dict[str, Any]:
    reg = export_identity_registry()
    rows = []
    for ident in reg["identities"]:
        base = f"{ident['identity_id']}|{ident['agent_id']}|{ident['workflow_scope']}|{','.join(ident['capability_scope'])}"
        fp = _fingerprint(base)
        rows.append(
            {
                "identity_id": ident["identity_id"],
                "identity_fingerprint": fp,
                "signature_algorithm": "sha256-metadata-only",
                "identity_hash": _fingerprint(fp + "|hash"),
                "attribution_chain": [
                    {"issued_by": ident["identity_lineage"]["issued_by"], "issued_at": ident["issued_at"], "deterministic": True},
                    {"workflow_scope": ident["workflow_scope"], "deterministic": True},
                ],
                "validation_status": "valid" if ident["trust_level"] in {"moderate", "elevated"} else "review",
                "deterministic": True,
            }
        )
    rows.sort(key=lambda r: r["identity_id"])
    return {"cryptographic_identities": rows, "deterministic": True, "no_real_key_management": True}

