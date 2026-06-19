from functools import lru_cache

import httpx


@lru_cache(maxsize=1)
def get_http_client() -> httpx.Client:
    return httpx.Client(
        timeout=30,
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
    )
