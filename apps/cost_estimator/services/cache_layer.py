"""
Redis-backed caching helpers for the Cost Estimator.
All keys use the 'ce:' namespace. TTLs are short (60 s) for cost data
since material prices can be updated by the data pipeline.
"""
import hashlib
import json
from django.core.cache import cache

ESTIMATE_TTL = 60       # seconds — cost estimate result
TCO_TTL = 300           # seconds — TCO projections change less frequently
PRICING_TTL = 600       # seconds — pricing list responses


def _hash(data: dict) -> str:
    return hashlib.md5(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()


def get_estimate(layout_id: str, country: str, city: str, labour_zone: str):
    key = f'ce:estimate:{_hash({"l": layout_id, "c": country, "ci": city, "lz": labour_zone})}'
    return cache.get(key)


def set_estimate(layout_id: str, country: str, city: str, labour_zone: str, value: dict):
    key = f'ce:estimate:{_hash({"l": layout_id, "c": country, "ci": city, "lz": labour_zone})}'
    cache.set(key, value, timeout=ESTIMATE_TTL)


def get_tco(layout_id: str, country: str, years: int):
    key = f'ce:tco:{_hash({"l": layout_id, "c": country, "y": years})}'
    return cache.get(key)


def set_tco(layout_id: str, country: str, years: int, value: dict):
    key = f'ce:tco:{_hash({"l": layout_id, "c": country, "y": years})}'
    cache.set(key, value, timeout=TCO_TTL)


def invalidate_layout(layout_id: str):
    """Bust all cached calculations for a layout (called after material swap)."""
    pattern = f'ce:*{layout_id}*'
    try:
        from django_redis import get_redis_connection
        conn = get_redis_connection('default')
        keys = conn.keys(pattern)
        if keys:
            conn.delete(*keys)
    except Exception:
        pass
