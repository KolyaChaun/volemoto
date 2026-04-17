import time
from collections import defaultdict, deque
from functools import wraps

from fastapi import HTTPException, Request

_buckets: dict[str, deque] = defaultdict(deque)


def _get_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(max_calls: int, period: int):

    def decorator(func):
        @wraps(func)
        async def async_wrapper(request: Request, *args, **kwargs):
            _check(request, max_calls, period)
            return await func(request=request, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(request: Request, *args, **kwargs):
            _check(request, max_calls, period)
            return func(request=request, *args, **kwargs)

        import asyncio

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def _check(request: Request, max_calls: int, period: int):
    ip = _get_ip(request)
    now = time.monotonic()
    bucket = _buckets[ip]
    while bucket and bucket[0] < now - period:
        bucket.popleft()
    if len(bucket) >= max_calls:
        raise HTTPException(
            status_code=429, detail="Забагато запитів. Спробуйте пізніше."
        )
    bucket.append(now)
