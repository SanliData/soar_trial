"""
MODULE: drift_monitoring_service
PURPOSE: Deterministic drift heuristics — explainable scores (H-033)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

DRIFT_TYPES: tuple[str, ...] = (
    "retrieval_drift",
    "graph_drift",
    "prompt_drift",
    "workflow_drift",
    "embedding_drift",
    "context_drift",
)


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def detect_drift(metrics: dict[str, float]) -> dict[str, Any]:
    """Per-type drift signals in [0,1] from named metric keys."""
    out: dict[str, float] = {}
    for dt in DRIFT_TYPES:
        key = f"{dt}_signal"
        out[dt] = _clamp01(float(metrics.get(key, 0.0)))
    return {
        "drift_signals": out,
        "heuristic": "named_metric_map_v1",
        "hidden_evaluation": False,
    }


def summarize_drift(metrics: dict[str, float]) -> dict[str, Any]:
    det = detect_drift(metrics)
    signals = det["drift_signals"]
    avg = round(sum(signals.values()) / max(1, len(signals)), 4)
    hottest = max(signals, key=lambda k: signals[k]) if signals else None
    return {
        "mean_signal": avg,
        "hottest_type": hottest,
        "types_monitored": list(DRIFT_TYPES),
        "summary_rule": "mean_and_argmax_v1",
    }


def compute_drift_risk(metrics: dict[str, float]) -> dict[str, Any]:
    det = detect_drift(metrics)
    vals = list(det["drift_signals"].values())
    risk = round(max(vals) if vals else 0.0, 4)
    band = "low" if risk < 0.35 else ("medium" if risk < 0.65 else "high")
    return {"drift_risk_score": risk, "risk_band": band, "scoring_rule": "max_signal_v1"}


def export_drift_report(metrics: dict[str, float]) -> dict[str, Any]:
    return {
        "detection": detect_drift(metrics),
        "summary": summarize_drift(metrics),
        "risk": compute_drift_risk(metrics),
    }
