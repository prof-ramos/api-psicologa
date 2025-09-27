# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
- **Development server**: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- **Production server**: Use the Docker container with `docker-entrypoint.sh`

### Testing
- **Run all tests**: `pytest`
- **Run with coverage**: `pytest --cov=app`
- **Run specific test**: `pytest tests/test_main.py::test_health`

### Code Quality
- **Linting**: `ruff check .`
- **Formatting**: `ruff format .`
- **Type checking**: `mypy app/`

### Dependencies
- **Install dev dependencies**: `pip install -e ".[dev,test]"`
- **Install with UI dependencies**: `pip install -e ".[ui]"`

## Architecture Overview

This is a **FastAPI-based astrological API** using the Kerykeion library for astronomical calculations.

### Core Structure
- **`app/main.py`**: Application factory and ASGI configuration with lifecycle management
- **`app/core/`**: Core infrastructure (config, middleware, exceptions, logging)
- **`app/api/v1/routers/`**: API endpoints (astrology calculations, health checks)
- **`app/services/`**: Business logic layer (astrology calculations)
- **`app/schemas/`**: Pydantic models for request/response validation

### Key Features
- **Automatic timezone detection** based on city names
- **SVG natal chart generation** using Kerykeion
- **Structured logging** with configurable JSON/text formats
- **Prometheus metrics** (optional) exposed on `/metrics`
- **CORS middleware** for frontend integration
- **Docker deployment** with multi-stage build and health checks

### Configuration
- Settings managed via **pydantic-settings** in `app/core/config.py`
- Environment variables loaded from `.env` file
- Key configs: `API_BASE_PATH`, `LOG_FORMAT`, `ENABLE_METRICS`, `TRAEFIK_DOMAIN`

### Deployment
- **Docker**: Multi-stage Dockerfile with non-root user and health checks
- **Traefik integration**: Labels configured for reverse proxy with strip-prefix
- **Portainer stack**: Available in `deploy/portainer-stack.yml`
- **Production entrypoint**: `docker-entrypoint.sh` with startup logging

### API Structure
- **Base URL**: `/api/v1/`
- **Health endpoints**: `/health/` and `/health/status`
- **Astrology endpoints**: `/astrology/subject`, `/astrology/natal-chart`, `/astrology/transits`
- **All endpoints** use Pydantic validation with detailed error responses

### Testing Notes
- Uses **pytest** with FastAPI's TestClient
- Current test coverage is minimal (only health check test exists)
- Tests should be expanded to cover all astrology endpoints and error cases
- Use `httpx.AsyncClient` for async endpoint testing when needed