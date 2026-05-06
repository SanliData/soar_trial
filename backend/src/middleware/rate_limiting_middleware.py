"""
MIDDLEWARE: rate_limiting_middleware
PURPOSE: Basic in-memory rate limiting per IP and API key
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

***REMOVED*** In-memory rate limit storage (for P0; use Redis in production)
_rate_limit_store = defaultdict(list)

***REMOVED*** Check if rate limiting is disabled in development
DISABLE_RATE_LIMIT = os.getenv("DISABLE_RATE_LIMIT", "false").lower() == "true"
ENV = os.getenv("ENV", "development")

***REMOVED*** Rate limits (requests per window)
RATE_LIMITS = {
    "default": (100, 60),  ***REMOVED*** 100 requests per 60 seconds
    "api_key": (1000, 60),  ***REMOVED*** 1000 requests per 60 seconds for API key
}


class RateLimitingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ***REMOVED*** Skip rate limiting in development mode or if explicitly disabled
        if ENV != "production" or DISABLE_RATE_LIMIT:
            return await call_next(request)
        
        ***REMOVED*** Skip rate limiting for health checks and static UI files
        path = request.url.path
        if path in ["/healthz", "/readyz", "/metrics"] or path.startswith("/ui/"):
            return await call_next(request)
        
        ***REMOVED*** Get identifier (API key or IP)
        api_key = request.headers.get("X-API-Key")
        identifier = api_key if api_key else request.client.host if request.client else "unknown"
        limit_type = "api_key" if api_key else "default"
        
        limit, window = RATE_LIMITS[limit_type]
        now = time.time()
        
        ***REMOVED*** Clean old entries
        key_requests = _rate_limit_store[identifier]
        key_requests[:] = [ts for ts in key_requests if now - ts < window]
        
        ***REMOVED*** Check limit
        if len(key_requests) >= limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {limit} requests per {window} seconds"
            )
        
        ***REMOVED*** Record request
        key_requests.append(now)
        
        return await call_next(request)
