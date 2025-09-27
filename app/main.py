"""
API Astrológica usando FastAPI e Kerykeion.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from .api.v1.routers import astrology_router, health_router
from .core.config import settings
from .core.middleware import (
    PerformanceMiddleware,
    CompressionMiddleware,
    logging_middleware,
    setup_cors_middleware
)
from .core.rate_limiter import RateLimitMiddleware
from .core.metrics import MetricsMiddleware, get_metrics_manager
from .core.exceptions import (
    AstrologyAPIException,
    http_exception_handler,
    validation_exception_handler,
    astrology_exception_handler,
    general_exception_handler
)
from .core.logging import configure_logging

try:
    from prometheus_client import make_asgi_app
except ImportError:  # pragma: no cover - dependência opcional
    make_asgi_app = None  # type: ignore[assignment]

# Configurar logging
configure_logging(settings.log_level, settings.log_format)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager para startup e shutdown da aplicação.
    """
    # Startup
    logger.info(
        "Iniciando %s v%s | host=%s | porta=%s | base_path=%s | metrics=%s",
        settings.app_name,
        settings.version,
        settings.host,
        settings.port,
        settings.api_base_path or "/",
        "habilitado" if settings.enable_metrics else "desabilitado"
    )
    yield
    # Shutdown
    logger.info("Encerrando aplicação")


def create_app() -> FastAPI:
    """
    Factory function para criar a aplicação FastAPI.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="API para cálculos astrológicos usando a biblioteca Kerykeion",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None
    )

    # Configurar CORS
    setup_cors_middleware(app)

    # Add performance optimization middlewares
    metrics_manager = get_metrics_manager()

    # Order matters: metrics -> rate limiting -> compression -> performance
    if settings.enable_metrics:
        app.add_middleware(MetricsMiddleware, metrics_manager=metrics_manager)

    if settings.rate_limit_enabled:
        app.add_middleware(RateLimitMiddleware)

    if settings.enable_compression:
        app.add_middleware(CompressionMiddleware, minimum_size=1000)

    app.add_middleware(PerformanceMiddleware)

    # Registrar exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(AstrologyAPIException, astrology_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Incluir routers
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(astrology_router, prefix="/api/v1")

    # Add metrics endpoint
    if settings.enable_metrics:
        from fastapi import Response

        @app.get(settings.metrics_path)
        async def get_metrics():
            """Endpoint for Prometheus metrics."""
            metrics_data, content_type = metrics_manager.get_metrics()
            if content_type == "application/json":
                return metrics_data
            else:
                return Response(content=metrics_data, media_type=content_type)

        # Also mount Prometheus WSGI app if available
        if make_asgi_app:
            app.mount("/prometheus", make_asgi_app())

    return app


# Criar instância da aplicação
app = create_app()
