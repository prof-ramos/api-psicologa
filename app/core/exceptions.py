"""
Exception handlers personalizados para a API.
"""

import logging
from typing import Dict, Any

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from ..schemas import APIResponse

logger = logging.getLogger(__name__)


class AstrologyAPIException(Exception):
    """Exceção base para erros da API astrológica."""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class KerykeionCalculationError(AstrologyAPIException):
    """Erro nos cálculos usando Kerykeion."""
    pass


class InvalidBirthDataError(AstrologyAPIException):
    """Erro em dados de nascimento inválidos."""
    pass


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handler para exceções HTTP padrão.
    """
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            status="KO",
            message=str(exc.detail)
        ).dict()
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    """
    Handler para erros de validação do Pydantic.
    """
    logger.warning(f"Validation Error: {exc.errors()}")

    errors = []
    for error in exc.errors():
        field = " -> ".join(str(x) for x in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    return JSONResponse(
        status_code=422,
        content=APIResponse(
            status="KO",
            message="Dados inválidos",
            data={"errors": errors}
        ).dict()
    )


async def astrology_exception_handler(request: Request, exc: AstrologyAPIException):
    """
    Handler para exceções específicas da API astrológica.
    """
    logger.error(f"Astrology Exception: {exc.message} - Details: {exc.details}")

    status_code = 400
    if isinstance(exc, KerykeionCalculationError):
        status_code = 500
    elif isinstance(exc, InvalidBirthDataError):
        status_code = 400

    return JSONResponse(
        status_code=status_code,
        content=APIResponse(
            status="KO",
            message=exc.message,
            data=exc.details
        ).dict()
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handler para exceções gerais não tratadas.
    """
    logger.error(f"Unhandled Exception: {type(exc).__name__} - {str(exc)}")

    return JSONResponse(
        status_code=500,
        content=APIResponse(
            status="KO",
            message="Erro interno do servidor"
        ).dict()
    )