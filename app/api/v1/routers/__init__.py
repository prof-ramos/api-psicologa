"""Routers for API v1."""

from .astrology import router as astrology_router
from .health import router as health_router

__all__ = ["astrology_router", "health_router"]