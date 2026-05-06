"""
SECURITY: bot_defense
PURPOSE: Adaptive bot defense — throttle, risk score, optional CAPTCHA only for suspicious traffic.
ENCODING: UTF-8 WITHOUT BOM

Principles:
- CAPTCHA is not shown everywhere; only on suspicious behavior.
- Silent throttle first; then rate-limit hardening; then visual verification.
- UX remains intact for normal users.
"""

import os
import time
import re
import hashlib
import logging
from collections import defaultdict
from typing import Optional, Tuple, Dict, Any

from src.config.settings import get_int_env, get_float_env, get_bool_env

logger = logging.getLogger(__name__)

***REMOVED*** In-memory store (use Redis in production for multi-instance)
_ip_timestamps: Dict[str, list] = defaultdict(list)
_fingerprint_timestamps: Dict[str, list] = defaultdict(list)
_ip_form_submits: Dict[str, list] = defaultdict(list)

***REMOVED*** Config from env (safe parsing to prevent empty-string crash)
BOT_DEFENSE_ENABLED = get_bool_env("BOT_DEFENSE_ENABLED", True)
BOT_FORM_SUBMIT_WINDOW = get_int_env("BOT_FORM_SUBMIT_WINDOW_SEC", 60)
BOT_FORM_SUBMIT_MAX = get_int_env("BOT_FORM_SUBMIT_MAX", 10)
BOT_SAME_IP_BURST_MAX = get_int_env("BOT_SAME_IP_BURST_MAX", 30)
BOT_SAME_IP_BURST_WINDOW = get_int_env("BOT_SAME_IP_BURST_WINDOW_SEC", 60)
BOT_RISK_CAPTCHA_THRESHOLD = get_float_env("BOT_RISK_CAPTCHA_THRESHOLD", 0.7)
BOT_SILENT_DELAY_MAX_MS = get_int_env("BOT_SILENT_DELAY_MS", 500)


def _fingerprint_from_headers(headers: dict, body_hash: Optional[str] = None) -> Optional[str]:
    """Build a best-effort fingerprint from headers (no PII)."""
    parts = []
    ua = headers.get("user-agent") or headers.get("User-Agent")
    if ua:
        parts.append(ua[:200])
    accept_lang = headers.get("accept-language") or headers.get("Accept-Language")
    if accept_lang:
        parts.append(accept_lang[:100])
    if body_hash:
        parts.append(body_hash)
    if not parts:
        return None
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:32]


def _is_headless_or_automation(user_agent: Optional[str]) -> bool:
    """Detect common headless/automation patterns."""
    if not user_agent:
        return True
    ua_lower = user_agent.lower()
    patterns = [
        "headless",
        "phantom",
        "selenium",
        "puppeteer",
        "playwright",
        "bot",
        "crawler",
        "spider",
        "curl",
        "python-requests",
        "go-http-client",
        "java/",
        "wget",
    ]
    return any(p in ua_lower for p in patterns)


def compute_bot_risk(
    client_ip: str,
    path: str,
    method: str,
    headers: dict,
    body_hash: Optional[str] = None,
) -> Tuple[float, bool]:
    """
    Compute bot risk score in [0, 1] and whether to require CAPTCHA.
    Returns (risk_score, require_captcha).
    """
    if not BOT_DEFENSE_ENABLED:
        return 0.0, False

    risk = 0.0
    now = time.time()
    ua = headers.get("user-agent") or headers.get("User-Agent")

    ***REMOVED*** 1) Headless / automation User-Agent
    if _is_headless_or_automation(ua):
        risk += 0.4

    ***REMOVED*** 2) Same IP burst (many requests in short window)
    _ip_timestamps[client_ip][:] = [t for t in _ip_timestamps[client_ip] if now - t < BOT_SAME_IP_BURST_WINDOW]
    _ip_timestamps[client_ip].append(now)
    if len(_ip_timestamps[client_ip]) > BOT_SAME_IP_BURST_MAX:
        risk += 0.35

    ***REMOVED*** 3) Same fingerprint serial attempts
    fp = _fingerprint_from_headers(headers, body_hash)
    if fp:
        _fingerprint_timestamps[fp][:] = [t for t in _fingerprint_timestamps[fp] if now - t < BOT_FORM_SUBMIT_WINDOW]
        _fingerprint_timestamps[fp].append(now)
        if len(_fingerprint_timestamps[fp]) > BOT_FORM_SUBMIT_MAX:
            risk += 0.35

    ***REMOVED*** 4) Very fast form submit (POST to sensitive paths in quick succession)
    if method == "POST" and _is_form_path(path):
        _ip_form_submits[client_ip][:] = [t for t in _ip_form_submits[client_ip] if now - t < BOT_FORM_SUBMIT_WINDOW]
        _ip_form_submits[client_ip].append(now)
        if len(_ip_form_submits[client_ip]) > BOT_FORM_SUBMIT_MAX:
            risk += 0.3

    risk = min(1.0, risk)
    require_captcha = risk >= BOT_RISK_CAPTCHA_THRESHOLD
    return risk, require_captcha


def _is_form_path(path: str) -> bool:
    """Paths that count as form submit for bot detection."""
    form_paths = (
        "/api/v1/public/onboarding-intake",
        "/api/v1/public/upload/",
        "/api/v1/public/",
    )
    return any(path.rstrip("/").startswith(p.rstrip("/")) for p in form_paths)


def should_silent_throttle(risk: float) -> bool:
    """Whether to add a small delay (silent throttle)."""
    return risk >= 0.3 and BOT_DEFENSE_ENABLED


def get_silent_delay_ms(risk: float) -> int:
    """Delay in ms for silent throttle (capped)."""
    if risk <= 0.3:
        return 0
    ***REMOVED*** Scale delay with risk, cap at BOT_SILENT_DELAY_MAX_MS
    delay = int(risk * BOT_SILENT_DELAY_MAX_MS)
    return min(delay, BOT_SILENT_DELAY_MAX_MS)


def get_captcha_required_response() -> Dict[str, Any]:
    """Standard response when CAPTCHA is required (abuse prevention, GDPR-safe)."""
    return {
        "require_captcha": True,
        "message": "We detected unusual activity. Please verify to continue.",
        "message_tr": "Alışılmadık aktivite tespit ettik. Devam etmek için doğrulama yapın.",
    }
