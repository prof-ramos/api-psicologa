"""Utilitários para configuração de logging."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from .config import LoggingFormats


class JsonLogFormatter(logging.Formatter):
    """Formata logs no padrão JSON simples compatível com agregadores."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        log_record: Dict[str, Any] = {
            "level": record.levelname,
            "time": self.formatTime(record, self.datefmt),
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=True)


def configure_logging(level: str, fmt: str) -> None:
    """Configura logging global considerando nível e formato."""
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    try:
        log_level = getattr(logging, level.upper())
    except AttributeError:
        log_level = logging.INFO

    if fmt == LoggingFormats.JSON:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonLogFormatter(datefmt="%Y-%m-%dT%H:%M:%S%z"))
        root_logger.setLevel(log_level)
        root_logger.addHandler(handler)
    else:
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s %(levelname)s %(name)s - %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )


__all__ = ["configure_logging"]
