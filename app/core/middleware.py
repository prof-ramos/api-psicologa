"""
Middleware personalizado para a API astrológica.
"""

import gzip
import json
import logging
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Enhanced middleware for performance monitoring and optimization."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Get client IP for logging
        client_ip = self.get_client_ip(request)

        # Log request start
        logger.info(
            f"Starting {request.method} {request.url.path} "
            f"- IP: {client_ip} - Size: {request.headers.get('content-length', 'unknown')}"
        )

        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Add performance headers
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            response.headers["X-Server-Time"] = str(int(time.time()))

            # Log response
            response_size = response.headers.get("content-length", "unknown")
            logger.info(
                f"Completed {request.method} {request.url.path} "
                f"- Status: {response.status_code} "
                f"- Time: {process_time:.3f}s "
                f"- Size: {response_size}"
            )

            # Log slow requests
            if process_time > 1.0:
                logger.warning(
                    f"Slow request detected: {request.method} {request.url.path} "
                    f"took {process_time:.3f}s"
                )

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error in {request.method} {request.url.path} "
                f"- Time: {process_time:.3f}s - Error: {e}"
            )
            raise

    def get_client_ip(self, request: Request) -> str:
        """Get real client IP considering reverse proxies."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct connection
        return request.client.host if request.client else "unknown"


class CompressionMiddleware(BaseHTTPMiddleware):
    """Custom compression middleware with better control."""

    def __init__(self, app, minimum_size: int = 1000):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compressible_types = {
            "application/json",
            "application/xml",
            "text/html",
            "text/plain",
            "text/css",
            "text/javascript",
            "image/svg+xml",
        }

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if not settings.enable_compression:
            return response

        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response

        # Check content type
        content_type = response.headers.get("content-type", "").split(";")[0]
        if content_type not in self.compressible_types:
            return response

        # Check content length
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) < self.minimum_size:
            return response

        # Check if already compressed
        if response.headers.get("content-encoding"):
            return response

        # Compress response body
        if hasattr(response, 'body'):
            try:
                original_body = response.body
                if len(original_body) >= self.minimum_size:
                    compressed_body = gzip.compress(original_body)

                    # Only use compression if it actually reduces size
                    if len(compressed_body) < len(original_body):
                        response.headers["content-encoding"] = "gzip"
                        response.headers["content-length"] = str(len(compressed_body))
                        response.body = compressed_body
            except Exception as e:
                logger.warning(f"Compression failed: {e}")

        return response


# Legacy function for backward compatibility
async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """Legacy logging middleware - use PerformanceMiddleware instead."""
    middleware = PerformanceMiddleware(None)
    return await middleware.dispatch(request, call_next)


def setup_cors_middleware(app):
    """
    Configura middleware CORS para a aplicação.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # React dev server
            "http://localhost:8080",  # Vue.js dev server
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )