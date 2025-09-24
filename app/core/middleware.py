"""
Middleware personalizado para a API astrológica.
"""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware


logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware para logging de requisições.
    """
    start_time = time.time()

    # Log da requisição
    logger.info(
        f"Iniciando {request.method} {request.url.path} "
        f"- IP: {request.client.host if request.client else 'unknown'}"
    )

    try:
        response = await call_next(request)

        # Log da resposta
        process_time = time.time() - start_time
        logger.info(
            f"Completado {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Tempo: {process_time:.3f}s"
        )

        # Adicionar header de tempo de processamento
        response.headers["X-Process-Time"] = str(process_time)

        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Erro em {request.method} {request.url.path} "
            f"- Tempo: {process_time:.3f}s - Erro: {e}"
        )
        raise


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