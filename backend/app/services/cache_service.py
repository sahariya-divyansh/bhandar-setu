"""Thread-safe time-based TTL in-memory caching service for API endpoints.

Cache Invalidation Strategy:
-----------------------------
1. Time-To-Live (TTL) Auto-Expiration:
   - Risk Summary & Redistribution Recommendations: 300s (5 minutes) TTL.
   - Gemini LLM Briefings & Alert Explanations: 180s (3 minutes) TTL.
2. Explicit Purge Invalidation:
   - Call `clear_cache()` whenever inventory logs or facility master data are updated.
"""

import time
import threading
from functools import wraps
from typing import Any, Dict, Tuple, Optional, Callable


class TTLCache:
    """Thread-safe TTL in-memory key-value cache."""

    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value if key exists and has not expired."""
        with self._lock:
            if key not in self._cache:
                return None
            value, expiry = self._cache[key]
            if time.time() > expiry:
                del self._cache[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value with specified or default TTL in seconds."""
        ttl_seconds = ttl if ttl is not None else self.default_ttl
        expiry = time.time() + ttl_seconds
        with self._lock:
            self._cache[key] = (value, expiry)

    def clear(self) -> None:
        """Purge all cached entries."""
        with self._lock:
            self._cache.clear()

    def invalidate_prefix(self, prefix: str) -> None:
        """Purge cached keys matching a specific prefix."""
        with self._lock:
            keys_to_del = [k for k in self._cache if k.startswith(prefix)]
            for k in keys_to_del:
                del self._cache[k]


# Global cache instances
api_cache = TTLCache(default_ttl=300)
gemini_cache = TTLCache(default_ttl=180)


def ttl_cache(ttl_seconds: int = 300, cache_instance: Optional[TTLCache] = None):
    """Decorator to cache endpoint or function results by arguments for specified TTL."""
    target_cache = cache_instance or api_cache

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Exclude non-hashable arguments like DB Session from cache key
            filtered_kwargs = {k: v for k, v in kwargs.items() if not k.endswith('db') and k != 'db'}
            cache_key = f"{func.__module__}.{func.__name__}:{args}:{sorted(filtered_kwargs.items())}"

            cached_val = target_cache.get(cache_key)
            if cached_val is not None:
                return cached_val

            result = func(*args, **kwargs)
            target_cache.set(cache_key, result, ttl=ttl_seconds)
            return result

        return wrapper

    return decorator
