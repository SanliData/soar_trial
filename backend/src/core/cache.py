"""
CACHE: cache
PURPOSE: Redis-based caching layer for enterprise scale
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import json
import logging
from typing import Optional, Any
from functools import wraps

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
        
        # Parse Redis URL
        if redis_url.startswith("redis://") or redis_url.startswith("rediss://"):
            # Use Redis URL format
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
            # Fallback: direct connection
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
        logger.info("Redis connection established")
        
        return _redis_client
        
    except ImportError:
        logger.warning("Redis not installed - caching disabled")
        return None
    except Exception as e:
        logger.warning(f"Redis connection failed: {e} - caching disabled")
        return None


def get_cache(key: str, default: Optional[Any] = None) -> Optional[Any]:
    """
    Get value from cache.
    
    Args:
        key: Cache key
        default: Default value if key not found
        
    Returns:
        Cached value or default
    """
    try:
        redis_client = get_redis_client()
        if redis_client is None:
            return default
        
        value = redis_client.get(key)
        if value is None:
            logger.debug(f"CACHE MISS: {key}")
            return default
        
        # Try to parse as JSON
        try:
            parsed_value = json.loads(value)
            logger.debug(f"CACHE HIT: {key}")
            return parsed_value
        except (json.JSONDecodeError, TypeError):
            # Return as-is if not JSON
            logger.debug(f"CACHE HIT: {key} (non-JSON)")
            return value
            
    except Exception as e:
        logger.warning(f"Cache get error for key {key}: {e}")
        return default


def set_cache(key: str, value: Any, ttl: int = 300) -> bool:
    """
    Set value in cache with TTL.
    
    Args:
        key: Cache key
        value: Value to cache (will be JSON-encoded if dict/list)
        ttl: Time to live in seconds (default: 5 minutes)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        redis_client = get_redis_client()
        if redis_client is None:
            return False
        
        # Serialize value
        if isinstance(value, (dict, list)):
            serialized = json.dumps(value, ensure_ascii=False)
        else:
            serialized = str(value)
        
        # Set with TTL
        result = redis_client.setex(key, ttl, serialized)
        
        if result:
            logger.debug(f"CACHE SET: {key} (TTL: {ttl}s)")
        
        return result
        
    except Exception as e:
        logger.warning(f"Cache set error for key {key}: {e}")
        return False


def delete_cache(key: str) -> bool:
    """
    Delete key from cache.
    
    Args:
        key: Cache key to delete
        
    Returns:
        True if deleted, False otherwise
    """
    try:
        redis_client = get_redis_client()
        if redis_client is None:
            return False
        
        result = redis_client.delete(key)
        return result > 0
        
    except Exception as e:
        logger.warning(f"Cache delete error for key {key}: {e}")
        return False


def cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate cache key from prefix and arguments.
    
    Example:
        cache_key("hotels", country="USA") -> "hotels:country:USA"
        cache_key("plan", plan_id="123") -> "plan:plan_id:123"
    
    Args:
        prefix: Key prefix
        *args: Positional arguments (will be joined with colons)
        **kwargs: Keyword arguments (will be formatted as key:value)
        
    Returns:
        Formatted cache key
    """
    parts = [prefix]
    
    # Add positional args
    if args:
        parts.extend(str(arg) for arg in args)
    
    # Add keyword args (sorted for consistency)
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        for k, v in sorted_kwargs:
            parts.append(f"{k}:{v}")
    
    return ":".join(parts)


def cached(ttl: int = 300, key_prefix: Optional[str] = None):
    """
    Decorator to cache function results.
    
    Usage:
        @cached(ttl=600, key_prefix="hotels")
        async def get_hotels(country: str):
            # Function logic
            return hotels
    
    Args:
        ttl: Cache TTL in seconds
        key_prefix: Cache key prefix (defaults to function name)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key_str = cache_key(prefix, *args, **kwargs)
            
            # Try cache
            cached_value = get_cache(cache_key_str)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key_str}")
                return cached_value
            
            # Cache miss - call function
            logger.debug(f"Cache miss: {cache_key_str}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            set_cache(cache_key_str, result, ttl)
            
            return result
        
        return wrapper
    return decorator
