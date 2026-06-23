import os
import json
import redis

_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_TTL = 30  # seconds

try:
    _client = redis.from_url(_REDIS_URL, decode_responses=True, socket_connect_timeout=1)
    _client.ping()
    _available = True
except Exception:
    _client = None
    _available = False


def get(key: str):
    if not _available:
        return None
    try:
        raw = _client.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None


def set(key: str, value):
    if not _available:
        return
    try:
        _client.set(key, json.dumps(value), ex=_TTL)
    except Exception:
        pass


def delete(key: str):
    if not _available:
        return
    try:
        _client.delete(key)
    except Exception:
        pass
