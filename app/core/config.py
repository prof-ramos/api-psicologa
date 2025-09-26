"""
Configuração da aplicação FastAPI para cálculos astrológicos.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class LoggingFormats:
    """Constantes com formatos de logging aceitos."""

    TEXT = "text"
    JSON = "json"


class Settings(BaseSettings):
    """Configurações da aplicação."""

    app_name: str = Field(default="API Astrológica", description="Nome da aplicação")
    version: str = Field(default="1.0.0", description="Versão da API")
    debug: bool = Field(default=False, description="Modo debug")
    env_type: str = Field(default="dev", description="Tipo do ambiente")
    host: str = Field(default="0.0.0.0", description="Host para bind do servidor")
    port: int = Field(default=8000, description="Porta padrão do servidor")
    workers: int = Field(default=1, description="Número de workers do servidor")
    api_base_path: str = Field(
        default="",
        description="Base path quando publicado atrás de proxy (usar Traefik strip-prefix)"
    )
    ui_base_path: str = Field(default="/ui", description="Base path da interface web")
    enable_metrics: bool = Field(default=False, description="Habilita endpoint de métricas Prometheus")
    metrics_path: str = Field(default="/metrics", description="Caminho para métricas Prometheus")
    traefik_entrypoint: str = Field(default="websecure", description="Entrypoint padrão do Traefik")
    traefik_domain: str = Field(default="", description="Domínio público usado pelo Traefik")
    log_level: str = Field(default="INFO", description="Nível de logging")
    log_format: str = Field(default=LoggingFormats.TEXT, description="Formato de logging: text ou json")

    # Configurações de localização padrão
    default_timezone: str = Field(default="America/Sao_Paulo", description="Timezone padrão")
    geonames_username: str = Field(default="", description="Username para GeoNames (opcional)")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
