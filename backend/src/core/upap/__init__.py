"""
CORE: upap
PURPOSE: UPAP capability layer ("kas") — quality gates enforced in SOAR backend.
ENCODING: UTF-8 WITHOUT BOM

Single entry: run_upap_gates() in gates.py.
Fail-fast on any gate FAIL; no silent fallback; evidence required for success.
"""

from src.core.upap.gates import run_upap_gates

__all__ = ["run_upap_gates"]
