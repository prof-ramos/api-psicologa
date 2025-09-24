"""
Schemas Pydantic para dados astrológicos usando Kerykeion.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


class APIResponse(BaseModel):
    """Response padrão da API seguindo padrão RORO."""

    status: str = Field(..., description="Status da operação: OK ou KO")
    data: Optional[Any] = Field(default=None, description="Dados da resposta")
    message: Optional[str] = Field(default=None, description="Mensagem informativa")


class AstrologicalSubjectRequest(BaseModel):
    """Request para criação de sujeito astrológico."""

    name: str = Field(..., min_length=1, max_length=100, description="Nome da pessoa")
    year: int = Field(..., ge=1900, le=2100, description="Ano de nascimento")
    month: int = Field(..., ge=1, le=12, description="Mês de nascimento")
    day: int = Field(..., ge=1, le=31, description="Dia de nascimento")
    hour: int = Field(..., ge=0, le=23, description="Hora de nascimento")
    minute: int = Field(..., ge=0, le=59, description="Minuto de nascimento")
    city: str = Field(..., min_length=1, max_length=100, description="Cidade de nascimento")
    nation: str = Field(..., min_length=2, max_length=2, description="País (código ISO)")
    timezone: Optional[str] = Field(default=None, description="Timezone (ex: America/Sao_Paulo)")

    @validator('nation')
    def validate_nation_code(cls, v):
        """Valida código do país."""
        if len(v) != 2:
            raise ValueError('Código do país deve ter 2 caracteres (ISO 3166-1 alpha-2)')
        return v.upper()


class PlanetPosition(BaseModel):
    """Posição de um planeta."""

    name: str = Field(..., description="Nome do planeta")
    longitude: float = Field(..., description="Longitude eclíptica")
    latitude: float = Field(..., description="Latitude eclíptica")
    distance: Optional[float] = Field(default=None, description="Distância da Terra")
    speed: Optional[float] = Field(default=None, description="Velocidade do planeta")
    sign: str = Field(..., description="Signo zodiacal")
    house: int = Field(..., ge=1, le=12, description="Casa astrológica")
    retrograde: bool = Field(default=False, description="Se o planeta está retrógrado")


class HousePosition(BaseModel):
    """Posição de uma casa astrológica."""

    house_number: int = Field(..., ge=1, le=12, description="Número da casa")
    longitude: float = Field(..., description="Longitude da cúspide")
    sign: str = Field(..., description="Signo na cúspide")


class AspectData(BaseModel):
    """Dados de um aspecto entre planetas."""

    planet1: str = Field(..., description="Primeiro planeta")
    planet2: str = Field(..., description="Segundo planeta")
    aspect: str = Field(..., description="Tipo do aspecto")
    orb: float = Field(..., description="Orbe do aspecto")
    applying: bool = Field(default=False, description="Se o aspecto está se aplicando")


class AstrologicalSubjectResponse(BaseModel):
    """Response com dados do sujeito astrológico."""

    name: str
    birth_date: datetime
    city: str
    nation: str
    latitude: float
    longitude: float
    timezone: str
    planets: List[PlanetPosition]
    houses: List[HousePosition]
    aspects: List[AspectData]
    lunar_phase: Optional[Dict[str, Any]] = None


class ChartRequest(BaseModel):
    """Request para geração de mapa astrológico."""

    subject: AstrologicalSubjectRequest
    chart_type: str = Field(default="natal", description="Tipo do mapa: natal, transit, etc.")
    format: str = Field(default="svg", description="Formato de saída: svg, json")
    include_aspects: bool = Field(default=True, description="Incluir aspectos no mapa")
    house_system: str = Field(default="Placidus", description="Sistema de casas")


class ChartResponse(BaseModel):
    """Response com dados do mapa astrológico."""

    chart_data: Dict[str, Any]
    svg_content: Optional[str] = Field(default=None, description="Conteúdo SVG do mapa")
    chart_type: str
    house_system: str
    calculation_date: datetime


class TransitRequest(BaseModel):
    """Request para cálculo de trânsitos."""

    natal_subject: AstrologicalSubjectRequest
    transit_date: datetime = Field(..., description="Data para calcular trânsitos")
    transit_planets: Optional[List[str]] = Field(
        default=None,
        description="Planetas específicos para trânsito"
    )
    orb_limit: float = Field(default=5.0, ge=0.0, le=15.0, description="Limite do orbe")


class TransitResponse(BaseModel):
    """Response com dados de trânsitos."""

    natal_subject: str
    transit_date: datetime
    transits: List[Dict[str, Any]]
    active_aspects: List[AspectData]