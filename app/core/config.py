"""
Configuração da aplicação FastAPI para cálculos astrológicos.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação."""

    app_name: str = Field(default="API Astrológica", description="Nome da aplicação")
    version: str = Field(default="1.0.0", description="Versão da API")
    debug: bool = Field(default=False, description="Modo debug")
    env_type: str = Field(default="dev", description="Tipo do ambiente")

    # Configurações de localização padrão
    default_timezone: str = Field(default="America/Sao_Paulo", description="Timezone padrão")
    geonames_username: str = Field(default="", description="Username para GeoNames (opcional)")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()