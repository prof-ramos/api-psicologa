# Etapa de build: instala dependencias em um ambiente isolado
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY . .

RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir .

# Etapa final: imagem enxuta apenas com runtime
FROM python:3.11-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system app \
    && adduser --system --ingroup app app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY app ./app
COPY uv.lock ./uv.lock
COPY docker-entrypoint.sh ./docker-entrypoint.sh
COPY API_DOCUMENTATION.md README.md ./

RUN chmod +x docker-entrypoint.sh

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD curl -f "http://127.0.0.1:${PORT:-8000}${API_BASE_PATH:-/api}/v1/health/" || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]
