"""
Redis service for caching.
Use this to cache product listings, user sessions, rate limiting etc.
"""
import json
import redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def set_cache(key: str, value: dict, ttl_seconds: int = 300):
    """Store a value in Redis with expiry (default 5 minutes)."""
    redis_client.setex(key, ttl_seconds, json.dumps(value))

def get_cache(key: str) -> dict | None:
    """Retrieve a cached value. Returns None if not found or expired."""
    data = redis_client.get(key)
    return json.loads(data) if data else None

def delete_cache(key: str):
    """Delete a cached value."""
    redis_client.delete(key)

def clear_pattern(pattern: str):
    """Delete all keys matching a pattern (e.g., 'products:*')."""
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)
