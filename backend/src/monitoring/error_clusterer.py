"""
MONITORING: error_clusterer
PURPOSE: Group similar errors; dedupe; cluster by normalized error signature and semantic similarity
"""
import hashlib
import logging
import re
from collections import defaultdict
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _normalize_message_for_signature(msg: str) -> str:
    """First line of message, strip numbers and variable parts to group similar errors."""
    if not msg:
        return ""
    first = msg.split("\n")[0].strip()[:150]
    first = re.sub(r"\d+", "N", first)
    first = re.sub(r"0x[0-9a-fA-F]+", "0xN", first)
    return first


def _signature(event: Dict[str, Any]) -> str:
    """Normalized signature: error_type + module/workflow_step + normalized message."""
    msg = _normalize_message_for_signature(event.get("error_message") or event.get("raw") or "")
    mod = event.get("module") or event.get("workflow_step") or ""
    endpoint = event.get("endpoint") or ""
    exc = event.get("exception_type") or ""
    key = f"{event.get('error_type', 'unknown')}|{mod}|{endpoint}|{exc}|{msg}"
    return hashlib.sha256(key.encode("utf-8", errors="replace")).hexdigest()[:16]


def _affected_components(events: List[Dict[str, Any]]) -> List[str]:
    comps = set()
    for e in events:
        if e.get("workflow_step"):
            comps.add(e["workflow_step"])
        if e.get("module"):
            name = e["module"].split("/")[-1].replace(".py", "")
            if name:
                comps.add(name)
        if e.get("endpoint"):
            comps.add(e["endpoint"])
    return sorted(comps)[:20]


async def cluster_errors(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Group similar errors. Dedupe identical; cluster by error_type + normalized signature.
    Returns list of clusters: cluster_id, error_type, count, sample_errors, affected_components.
    """
    if not events:
        return []
    by_sig = defaultdict(list)
    for ev in events:
        sig = _signature(ev)
        by_sig[sig].append(ev)
    clusters = []
    for i, (sig, group) in enumerate(by_sig.items()):
        sample = group[0]
        error_type = sample.get("error_type", "unknown_error")
        cluster_id = f"cluster_{sig}"
        samples = group[:5]
        endpoints = list({e.get("endpoint") for e in group if e.get("endpoint")})[:3]
        workflows = list({e.get("workflow_step") for e in group if e.get("workflow_step")})[:3]
        clusters.append({
            "cluster_id": cluster_id,
            "error_type": error_type,
            "count": len(group),
            "sample_errors": samples,
            "affected_components": _affected_components(group),
            "affected_endpoint": endpoints[0] if endpoints else None,
            "affected_workflow": workflows[0] if workflows else None,
            "signature": sig,
        })
    # Merge by error_type if many tiny clusters
    by_type = defaultdict(list)
    for c in clusters:
        by_type[c["error_type"]].append(c)
    out = []
    for etype, clist in by_type.items():
        if len(clist) == 1:
            out.append(clist[0])
        else:
            total = sum(c["count"] for c in clist)
            all_samples = []
            all_components = set()
            for c in clist:
                all_samples.extend(c["sample_errors"][:2])
                all_components.update(c.get("affected_components", []))
            ep = next((c.get("affected_endpoint") for c in clist if c.get("affected_endpoint")), None)
            wf = next((c.get("affected_workflow") for c in clist if c.get("affected_workflow")), None)
            out.append({
                "cluster_id": clist[0]["cluster_id"],
                "error_type": etype,
                "count": total,
                "sample_errors": all_samples[:5],
                "affected_components": sorted(all_components)[:20],
                "affected_endpoint": ep,
                "affected_workflow": wf,
                "signature": clist[0]["signature"],
            })
    logger.info("error_clusterer: %s events -> %s clusters", len(events), len(out))
    return out
