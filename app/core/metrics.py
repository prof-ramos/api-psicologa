"""
Performance metrics and monitoring for the API.
"""

import time
import logging
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta

try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings

logger = logging.getLogger(__name__)


class SimpleMetrics:
    """Simple metrics collection without Prometheus."""

    def __init__(self):
        self.request_count = defaultdict(int)
        self.request_duration = defaultdict(list)
        self.error_count = defaultdict(int)
        self.active_requests = 0
        self.start_time = time.time()

    def record_request(self, method: str, path: str, status_code: int, duration: float):
        """Record request metrics."""
        key = f"{method}:{path}"
        self.request_count[key] += 1
        self.request_duration[key].append(duration)

        if status_code >= 400:
            self.error_count[key] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        uptime = time.time() - self.start_time

        # Calculate averages and percentiles
        avg_durations = {}
        p95_durations = {}

        for key, durations in self.request_duration.items():
            if durations:
                avg_durations[key] = sum(durations) / len(durations)
                sorted_durations = sorted(durations)
                p95_index = int(len(sorted_durations) * 0.95)
                p95_durations[key] = sorted_durations[p95_index] if sorted_durations else 0

        return {
            "uptime_seconds": uptime,
            "active_requests": self.active_requests,
            "total_requests": dict(self.request_count),
            "error_counts": dict(self.error_count),
            "average_duration_seconds": avg_durations,
            "p95_duration_seconds": p95_durations,
        }


class PrometheusMetrics:
    """Prometheus metrics collection."""

    def __init__(self):
        if not PROMETHEUS_AVAILABLE:
            raise ImportError("Prometheus client not available")

        # Define metrics
        self.request_count = Counter(
            'api_requests_total',
            'Total number of API requests',
            ['method', 'endpoint', 'status_code']
        )

        self.request_duration = Histogram(
            'api_request_duration_seconds',
            'API request duration in seconds',
            ['method', 'endpoint']
        )

        self.active_requests = Gauge(
            'api_active_requests',
            'Number of active API requests'
        )

        self.cache_hits = Counter(
            'api_cache_hits_total',
            'Total number of cache hits',
            ['cache_type']
        )

        self.cache_misses = Counter(
            'api_cache_misses_total',
            'Total number of cache misses',
            ['cache_type']
        )

        self.astrological_calculations = Counter(
            'api_astro_calculations_total',
            'Total number of astrological calculations',
            ['calculation_type']
        )

        self.calculation_duration = Histogram(
            'api_astro_calculation_duration_seconds',
            'Astrological calculation duration in seconds',
            ['calculation_type']
        )

    def record_request(self, method: str, path: str, status_code: int, duration: float):
        """Record request metrics."""
        # Normalize path to remove IDs and parameters
        normalized_path = self._normalize_path(path)

        self.request_count.labels(
            method=method,
            endpoint=normalized_path,
            status_code=str(status_code)
        ).inc()

        self.request_duration.labels(
            method=method,
            endpoint=normalized_path
        ).observe(duration)

    def record_cache_hit(self, cache_type: str):
        """Record cache hit."""
        self.cache_hits.labels(cache_type=cache_type).inc()

    def record_cache_miss(self, cache_type: str):
        """Record cache miss."""
        self.cache_misses.labels(cache_type=cache_type).inc()

    def record_calculation(self, calculation_type: str, duration: float):
        """Record astrological calculation."""
        self.astrological_calculations.labels(calculation_type=calculation_type).inc()
        self.calculation_duration.labels(calculation_type=calculation_type).observe(duration)

    def start_request(self):
        """Increment active requests."""
        self.active_requests.inc()

    def end_request(self):
        """Decrement active requests."""
        self.active_requests.dec()

    def _normalize_path(self, path: str) -> str:
        """Normalize API path for metrics."""
        # Remove query parameters
        path = path.split('?')[0]

        # Replace common dynamic segments
        parts = path.split('/')
        normalized_parts = []

        for part in parts:
            # Replace UUIDs, numbers, and other dynamic parts
            if part.isdigit() or len(part) == 36 or part in ['current-transits']:
                normalized_parts.append('{id}')
            else:
                normalized_parts.append(part)

        return '/'.join(normalized_parts)

    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        return generate_latest()


class MetricsManager:
    """Unified metrics manager."""

    def __init__(self):
        self.metrics = None
        self._init_metrics()

    def _init_metrics(self):
        """Initialize metrics backend."""
        if settings.enable_metrics and PROMETHEUS_AVAILABLE:
            try:
                self.metrics = PrometheusMetrics()
                logger.info("Using Prometheus metrics")
            except Exception as e:
                logger.warning(f"Prometheus unavailable, using simple metrics: {e}")
                self.metrics = SimpleMetrics()
        else:
            self.metrics = SimpleMetrics()
            logger.info("Using simple metrics")

    def record_request(self, method: str, path: str, status_code: int, duration: float):
        """Record request metrics."""
        self.metrics.record_request(method, path, status_code, duration)

    def start_request(self):
        """Start request tracking."""
        if hasattr(self.metrics, 'start_request'):
            self.metrics.start_request()
        else:
            self.metrics.active_requests += 1

    def end_request(self):
        """End request tracking."""
        if hasattr(self.metrics, 'end_request'):
            self.metrics.end_request()
        else:
            self.metrics.active_requests -= 1

    def record_cache_hit(self, cache_type: str):
        """Record cache hit."""
        if hasattr(self.metrics, 'record_cache_hit'):
            self.metrics.record_cache_hit(cache_type)

    def record_cache_miss(self, cache_type: str):
        """Record cache miss."""
        if hasattr(self.metrics, 'record_cache_miss'):
            self.metrics.record_cache_miss(cache_type)

    def record_calculation(self, calculation_type: str, duration: float):
        """Record calculation metrics."""
        if hasattr(self.metrics, 'record_calculation'):
            self.metrics.record_calculation(calculation_type, duration)

    def get_metrics(self):
        """Get metrics in appropriate format."""
        if hasattr(self.metrics, 'get_metrics'):
            if isinstance(self.metrics, PrometheusMetrics):
                return self.metrics.get_metrics(), CONTENT_TYPE_LATEST
            else:
                return self.metrics.get_metrics(), "application/json"
        return {}, "application/json"


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting request metrics."""

    def __init__(self, app, metrics_manager: MetricsManager):
        super().__init__(app)
        self.metrics = metrics_manager

    async def dispatch(self, request: Request, call_next):
        """Collect metrics for each request."""
        start_time = time.time()
        self.metrics.start_request()

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            self.metrics.record_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration
            )

            return response

        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_request(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration=duration
            )
            raise

        finally:
            self.metrics.end_request()


# Global metrics manager
metrics_manager = MetricsManager()


def get_metrics_manager() -> MetricsManager:
    """Get global metrics manager."""
    return metrics_manager


def timed_calculation(calculation_type: str):
    """Decorator to time astrological calculations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                metrics_manager.record_calculation(calculation_type, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics_manager.record_calculation(f"{calculation_type}_error", duration)
                raise
        return wrapper
    return decorator