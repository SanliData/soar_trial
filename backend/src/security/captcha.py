"""
SECURITY: captcha
PURPOSE: CAPTCHA token validation — reCAPTCHA v3 or simple challenge token.
ENCODING: UTF-8 WITHOUT BOM

Used only when bot defense flags require_captcha. No CAPTCHA on first interaction.
"""

import os
import logging
import hmac
import hashlib
import time
import json
from typing import Optional, Tuple

from src.config.settings import get_int_env

logger = logging.getLogger(__name__)

RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET_KEY") or os.getenv("GOOGLE_RECAPTCHA_SECRET")
CAPTCHA_CHALLENGE_SECRET = os.getenv("CAPTCHA_CHALLENGE_SECRET") or os.getenv("JWT_SECRET") or "dev-secret"
CAPTCHA_CHALLENGE_TTL_SEC = get_int_env("CAPTCHA_CHALLENGE_TTL_SEC", 300)


def verify_recaptcha_v3(token: str, expected_action: Optional[str] = None) -> Tuple[bool, Optional[float]]:
    """
    Verify Google reCAPTCHA v3 token.
    Returns (success, score). Score in [0, 1]; typically >= 0.5 is human.
    """
    if not RECAPTCHA_SECRET or not token:
        return False, None
    try:
        import urllib.request
        import urllib.parse
        data = urllib.parse.urlencode({
            "secret": RECAPTCHA_SECRET,
            "response": token,
        }).encode()
        req = urllib.request.Request(
            "https://www.google.com/recaptcha/api/siteverify",
            data=data,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read().decode())
        ok = body.get("success") is True
        score = body.get("score")
        if expected_action and body.get("action") != expected_action:
            ok = False
        return ok, float(score) if score is not None else None
    except Exception as e:
        logger.warning("reCAPTCHA verify failed: %s", e)
        return False, None


def create_simple_challenge_token(client_ip: str, nonce: str) -> str:
    """
    Create a self-hosted challenge token (no Google). Frontend shows image challenge,
    user solves, frontend sends nonce; we sign nonce+ip+expiry.
    """
    expiry = int(time.time()) + CAPTCHA_CHALLENGE_TTL_SEC
    payload = f"{client_ip}|{nonce}|{expiry}"
    sig = hmac.new(
        CAPTCHA_CHALLENGE_SECRET.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()[:16]
    return f"{expiry}.{sig}.{nonce}"


def verify_simple_challenge_token(token: str, client_ip: str) -> bool:
    """Verify self-hosted challenge token."""
    if not token or "." not in token:
        return False
    try:
        parts = token.split(".", 2)
        expiry = int(parts[0])
        if time.time() > expiry:
            return False
        nonce = parts[2] if len(parts) > 2 else ""
        expected = create_simple_challenge_token(client_ip, nonce)
        return hmac.compare_digest(token, expected)
    except Exception:
        return False


def verify_captcha_token(
    token: Optional[str],
    client_ip: str,
    prefer_recaptcha: bool = True,
) -> bool:
    """
    Verify CAPTCHA: if reCAPTCHA secret is set, use reCAPTCHA v3; else accept simple challenge token.
    """
    if not token:
        return False
    if prefer_recaptcha and RECAPTCHA_SECRET:
        ok, _ = verify_recaptcha_v3(token)
        return ok
    return verify_simple_challenge_token(token, client_ip)
