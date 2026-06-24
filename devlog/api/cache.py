import os
import json
import redis

_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_TTL = 30  # seconds
_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    try:
        c = redis.from_url(_REDIS_URL, decode_responses=True, socket_connect_timeout=1)
        c.ping()
        _client = c
        return _client
    except Exception:
        return None


def get(key: str):
    global _client
    client = _get_client()
    if not client:
        return None
    try:
        raw = client.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        _client = None
        return None


def set(key: str, value):
    global _client
    client = _get_client()
    if not client:
        return
    try:
        client.set(key, json.dumps(value), ex=_TTL)
    except Exception:
        _client = None


def delete(key: str):
    global _client
    client = _get_client()
    if not client:
        return
    try:
        client.delete(key)
    except Exception:
        _client = None
