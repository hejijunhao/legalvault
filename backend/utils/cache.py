# cache.py
from functools import lru_cache
from typing import Any, Optional
import time

def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a unique cache key based on arguments"""
    args_str = '-'.join(str(arg) for arg in args)
    kwargs_str = '-'.join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return f"{prefix}:{args_str}:{kwargs_str}"

@lru_cache(maxsize=100)
def cache_ai_response(input_text: str) -> str:
    """Cache AI responses for identical inputs"""
    # In a real implementation, this would call your AI model
    return f"Cached response for: {input_text}"

class TTLCache:
    """Simple time-based cache implementation"""
    def __init__(self, ttl_seconds: int = 3600):
        self._cache = {}
        self._ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp <= self._ttl:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any):
        self._cache[key] = (value, time.time())
