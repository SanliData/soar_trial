"""
EXPERIMENT_ENGINE: variant_allocator
PURPOSE: Distribute campaign traffic across experiment variants (consistent per campaign/contact)
"""
import hashlib
import logging
from typing import Any, Dict, List, Optional

from src.experiment_engine.experiment_manager import get_experiment

logger = logging.getLogger(__name__)


def _hash_to_float(s: str) -> float:
    """Deterministic 0.0-1.0 from string."""
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:12], 16) / (16 ** 12)


def allocate_variant(
    experiment_id: str,
    campaign_id: Optional[str] = None,
    contact_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Allocate a variant for this request. Uses campaign_id/contact_id/user_id for stable assignment.
    Returns variant dict { "id": "A", "config": {...} } or None.
    """
    ex = get_experiment(experiment_id)
    if not ex:
        return None
    variants = ex.get("variants", [])
    traffic_split = ex.get("traffic_split", {})
    if not variants:
        return None
    seed = f"{experiment_id}:{campaign_id or ''}:{contact_id or ''}:{user_id or ''}"
    r = _hash_to_float(seed)
    cumul = 0.0
    for vid in list(traffic_split.keys()):
        cumul += traffic_split.get(vid, 0)
        if r < cumul:
            for v in variants:
                if v.get("id") == vid:
                    return v
            break
    return variants[0] if variants else None


def get_variant_for_campaign(
    experiment_id: str,
    campaign_id: str,
    contact_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Convenience: allocate variant for a campaign (distributes campaign traffic)."""
    return allocate_variant(
        experiment_id=experiment_id,
        campaign_id=campaign_id,
        contact_id=contact_id,
    )
