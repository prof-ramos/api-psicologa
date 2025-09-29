"""
Rate limiting middleware for API performance and abuse prevention.
"""

import time
import logging
from typing import Dict, Tuple
from collections import defaultdict, deque

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings

logger = logging.getLogger(__name__)


class TokenBucket:
    """Token bucket algorithm for rate limiting."""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from bucket."""
        now = time.time()

        # Refill tokens based on time passed
        time_passed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + time_passed * self.refill_rate
        )
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class InMemoryRateLimiter:
    """In-memory rate limiter using sliding window."""

    def __init__(self, requests_per_minute: int = 60, window_size: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_size = window_size
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.buckets: Dict[str, TokenBucket] = {}

    def is_allowed(self, identifier: str) -> Tuple[bool, Dict[str, any]]:
        """Check if request is allowed."""
        now = time.time()

        # Get or create token bucket for identifier
        if identifier not in self.buckets:
            self.buckets[identifier] = TokenBucket(
                capacity=self.requests_per_minute,
                refill_rate=self.requests_per_minute / 60.0  # per second
            )

        bucket = self.buckets[identifier]
        allowed = bucket.consume()

        # Calculate remaining requests and reset time
        requests_made = self.requests_per_minute - int(bucket.tokens)
        reset_time = int(now + 60)  # Reset every minute

        headers = {
            'X-RateLimit-Limit': str(self.requests_per_minute),
            'X-RateLimit-Remaining': str(max(0, int(bucket.tokens))),
            'X-RateLimit-Reset': str(reset_time)
        }

        return allowed, headers

    def cleanup_old_entries(self):
        """Remove old entries to prevent memory leaks."""
        current_time = time.time()
        # Remove buckets that haven't been used in the last hour
        to_remove = [
            identifier for identifier, bucket in self.buckets.items()
            if current_time - bucket.last_refill > 3600
        ]
        for identifier in to_remove:
            del self.buckets[identifier]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    def __init__(self, app, requests_per_minute: int = None, window_size: int = None):
        super().__init__(app)
        self.enabled = settings.rate_limit_enabled
        self.requests_per_minute = requests_per_minute or settings.rate_limit_requests
        self.window_size = window_size or settings.rate_limit_window

        if self.enabled:
            self.limiter = InMemoryRateLimiter(
                requests_per_minute=self.requests_per_minute,
                window_size=self.window_size
            )
            logger.info(f"Rate limiting enabled: {self.requests_per_minute} requests per minute")
        else:
            logger.info("Rate limiting disabled")

    def get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get real IP from headers (for reverse proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            # Fallback to direct connection IP
            client_ip = request.client.host if request.client else "unknown"

        return client_ip

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        if not self.enabled:
            return await call_next(request)

        # Skip rate limiting for health checks
        if request.url.path.startswith("/api/v1/health"):
            return await call_next(request)

        client_id = self.get_client_identifier(request)
        allowed, headers = self.limiter.is_allowed(client_id)

        if not allowed:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute allowed",
                    "retry_after": 60
                },
                headers=headers
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value

        return response


# Global rate limiter instance
rate_limiter = None

def get_rate_limiter() -> InMemoryRateLimiter:
    """Get global rate limiter instance."""
    global rate_limiter
    if rate_limiter is None and settings.rate_limit_enabled:
        rate_limiter = InMemoryRateLimiter(
            requests_per_minute=settings.rate_limit_requests,
            window_size=settings.rate_limit_window
        )
    return rate_limiter