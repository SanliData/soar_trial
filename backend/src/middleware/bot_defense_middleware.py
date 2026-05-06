"""
MIDDLEWARE: bot_defense_middleware
PURPOSE: Set bot risk and require_captcha on request.state for public routes.
ENCODING: UTF-8 WITHOUT BOM

Does not block; endpoints check request.state.require_captcha and return 403 + captcha message
when CAPTCHA is required but missing or invalid.
"""

import asyncio
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.security.bot_defense import (
    compute_bot_risk,
    should_silent_throttle,
    get_silent_delay_ms,
)

logger = logging.getLogger(__name__)


class BotDefenseMiddleware(BaseHTTPMiddleware):
    """Runs only on /api/v1/public; sets request.state.bot_risk_score and require_captcha."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not path.startswith("/api/v1/public"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        headers = dict(request.headers) if request.headers else {}
        # Do not read body here (would consume stream); use headers-only for fingerprint
        risk, require_captcha = compute_bot_risk(client_ip, path, method, headers, body_hash=None)
        request.state.bot_risk_score = risk
        request.state.require_captcha = require_captcha

        if should_silent_throttle(risk):
            delay_ms = get_silent_delay_ms(risk)
            if delay_ms > 0:
                await asyncio.sleep(delay_ms / 1000.0)

        return await call_next(request)
