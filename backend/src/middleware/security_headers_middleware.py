"""
MIDDLEWARE: security_headers_middleware
PURPOSE: Add security headers to all responses
ENCODING: UTF-8 WITHOUT BOM
"""

import os
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Only add CSP, HSTS and COOP in production
        if os.getenv("ENV") == "production":
            # CSP: Production-safe, Google OAuth compatible (no iframe for Google login – use popup/redirect)
            csp_policy = (
                "default-src 'self'; "
                "script-src 'self' https://accounts.google.com https://apis.google.com https://unpkg.com 'unsafe-inline' 'unsafe-eval'; "
                "connect-src 'self' https://accounts.google.com https://oauth2.googleapis.com https://soarb2b.com https://unpkg.com; "
                "frame-src https://accounts.google.com; "
                "frame-ancestors 'self'; "
                "style-src 'self' https://fonts.googleapis.com https://api.fontshare.com https://unpkg.com https://accounts.google.com 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://fonts.gstatic.com https://api.fontshare.com https://cdn.fontshare.com data:;"
            )
            response.headers["Content-Security-Policy"] = csp_policy
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            # Google GSI popup: allow postMessage between opener and popup
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
            response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"
        
        return response
