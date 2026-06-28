"""
Simple in-memory rate limiter middleware.
Limits requests per IP per minute.
"""
from __future__ import annotations
import time
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import get_settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._window: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        # Only rate-limit chat endpoint
        if not request.url.path.startswith("/chat"):
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60.0
        limit = settings.RATE_LIMIT_PER_MINUTE

        self._window[ip] = [t for t in self._window[ip] if now - t < window]
        if len(self._window[ip]) >= limit:
            return JSONResponse(
                {"detail": f"Rate limit exceeded. Max {limit} requests per minute."},
                status_code=429,
            )
        self._window[ip].append(now)
        return await call_next(request)
