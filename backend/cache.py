import json

from flask import current_app
from redis import Redis
from redis.exceptions import RedisError


redis_client = None


def client():
    global redis_client
    if redis_client is None:
        redis_client = Redis.from_url(current_app.config["CELERY_BROKER_URL"], decode_responses=True, socket_connect_timeout=1)
    return redis_client


def get_cache(key):
    try:
        value = client().get(f"ppa:{key}")
        return json.loads(value) if value else None
    except RedisError:
        return None  # Redis band ho to API normal database se chalegi.


def set_cache(key, value):
    try:
        client().setex(f"ppa:{key}", current_app.config["CACHE_SECONDS"], json.dumps(value))
    except RedisError:
        pass


def clear_cache(*prefixes):
    try:
        for prefix in prefixes:
            keys = list(client().scan_iter(f"ppa:{prefix}*"))
            if keys:
                client().delete(*keys)
    except RedisError:
        pass
