"""
API Astrológica usando FastAPI e Kerykeion.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from .api.v1.routers import astrology_router, health_router
from .core.config import settings
from .core.middleware import logging_middleware, setup_cors_middleware
from .core.exceptions import (
    AstrologyAPIException,
    http_exception_handler,
    validation_exception_handler,
    astrology_exception_handler,
    general_exception_handler
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager para startup e shutdown da aplicação.
    """
    # Startup
    logger.info(f"Iniciando {settings.app_name} v{settings.version}")
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

    # Adicionar middleware personalizado
    app.middleware("http")(logging_middleware)

    # Registrar exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(AstrologyAPIException, astrology_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Incluir routers
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(astrology_router, prefix="/api/v1")

    return app


# Criar instância da aplicação
app = create_app()