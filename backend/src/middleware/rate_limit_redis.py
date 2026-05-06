"""
MIDDLEWARE: rate_limit_redis
PURPOSE: Redis-based rate limiting for enterprise scale
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import time
import logging
from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from src.config.settings import get_int_env

logger = logging.getLogger(__name__)

# Redis connection (lazy initialization)
_redis_client = None


def get_redis_client():
    """Get Redis client (singleton pattern)"""
    global _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    try:
        import redis
        
        # Redis connection URL from environment
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_password = os.getenv("REDIS_PASSWORD", None)
        
        if redis_url.startswith("redis://") or redis_url.startswith("rediss://"):
            _redis_client = redis.from_url(
                redis_url,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
        else:
            redis_host = os.getenv("REDIS_HOST") or "localhost"
            redis_port = get_int_env("REDIS_PORT", 6379)
            redis_db = get_int_env("REDIS_DB", 0)
            
            _redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
        
        # Test connection
        _redis_client.ping()
        logger.info("Redis connection established for rate limiting")
        
        return _redis_client
        
    except ImportError:
        logger.warning("Redis not installed - rate limiting disabled")
        return None
    except Exception as e:
        logger.warning(f"Redis connection failed: {e} - rate limiting disabled")
        return None


# Rate limits (requests per minute)
RATE_LIMITS = {
    "default": (100, 60),   # 100 requests per 60 seconds per IP
    "api_key": (100, 60),   # 100 requests per 60 seconds per API key (enterprise requirement)
}


class RateLimitRedisMiddleware(BaseHTTPMiddleware):
    """
    Redis-based rate limiting middleware.
    
    Supports:
    - Per-API-key rate limiting
    - Per-IP rate limiting
    - Distributed rate limiting (works across multiple instances)
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/healthz", "/readyz", "/metrics"]:
            return await call_next(request)
        
        # Only apply to /api/v1/* endpoints
        if not request.url.path.startswith("/api/v1/"):
            return await call_next(request)
        
        # Get identifier (API key or IP)
        api_key = request.headers.get("X-API-Key")
        if api_key:
            identifier = f"api_key:{api_key.strip()}"
            limit_type = "api_key"
        else:
            identifier = f"ip:{request.client.host if request.client else 'unknown'}"
            limit_type = "default"
        
        # Get rate limit config
        limit, window = RATE_LIMITS[limit_type]
        
        # Check rate limit using Redis
        redis_client = get_redis_client()
        
        if redis_client is None:
            # Fallback: no rate limiting if Redis unavailable
            logger.warning("Redis unavailable - rate limiting disabled")
            return await call_next(request)
        
        try:
            # Redis key for rate limit
            redis_key = f"rate_limit:{identifier}"
            
            # Get current count
            current_count = redis_client.get(redis_key)
            
            if current_count is None:
                # First request - set initial count
                redis_client.setex(redis_key, window, 1)
                remaining = limit - 1
            else:
                current_count = int(current_count)
                
                if current_count >= limit:
                    # Rate limit exceeded
                    ttl = redis_client.ttl(redis_key)
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded: {limit} requests per {window} seconds. Retry after {ttl} seconds.",
                        headers={
                            "X-RateLimit-Limit": str(limit),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Reset": str(int(time.time()) + ttl)
                        }
                    )
                
                # Increment counter
                redis_client.incr(redis_key)
                remaining = limit - (current_count + 1)
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers to response
            ttl = redis_client.ttl(redis_key)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + ttl)
            
            return response
            
        except HTTPException:
            # Re-raise HTTP exceptions (rate limit exceeded)
            raise
        except Exception as e:
            # If Redis error, allow request but log warning
            logger.warning(f"Rate limit check failed: {e} - allowing request")
            try:
                response = await call_next(request)
                return response
            except Exception:
                raise
