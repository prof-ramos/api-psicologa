"""
Endpoints para cálculos astrológicos usando Kerykeion.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from ....schemas import (
    APIResponse,
    AstrologicalSubjectRequest,
    AstrologicalSubjectResponse,
    ChartRequest,
    ChartResponse,
    TransitRequest,
    TransitResponse
)
from ....services import AstrologyService
from ....services.async_astrology_service import AsyncAstrologyService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/astrology", tags=["astrology"])


@router.post("/subject", response_model=APIResponse)
async def create_astrological_subject(request: AstrologicalSubjectRequest):
    """
    Cria um sujeito astrológico com dados de nascimento.

    Retorna informações astrológicas básicas incluindo:
    - Posições planetárias
    - Casas astrológicas
    - Aspectos entre planetas
    """
    try:
        subject_data = await AsyncAstrologyService.get_astrological_data(request)

        return APIResponse(
            status="OK",
            data=subject_data.dict(),
            message="Dados astrológicos calculados com sucesso"
        )

    except ValueError as e:
        logger.error(f"Erro de validação: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/natal-chart", response_model=APIResponse)
async def generate_natal_chart(request: ChartRequest):
    """
    Gera mapa natal em formato SVG.

    Parâmetros:
    - subject: Dados de nascimento
    - chart_type: Tipo do mapa (default: natal)
    - format: Formato de saída (default: svg)
    - include_aspects: Incluir aspectos no mapa
    - house_system: Sistema de casas (default: Placidus)
    """
    try:
        chart_data = await AsyncAstrologyService.generate_natal_chart(
            request.subject,
            chart_type=request.chart_type,
            include_aspects=request.include_aspects
        )

        return APIResponse(
            status="OK",
            data=chart_data.dict(),
            message="Mapa natal gerado com sucesso"
        )

    except ValueError as e:
        logger.error(f"Erro de validação: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/natal-chart/{name}/svg")
def get_natal_chart_svg(name: str):
    """
    Retorna o SVG do mapa natal diretamente.

    NOTA: Este é um endpoint simplificado. Em produção,
    seria melhor implementar cache e armazenamento de mapas gerados.
    """
    # Esta implementação é simplificada para demonstração
    # Em produção, você salvaria os mapas e os recuperaria por ID/nome
    raise HTTPException(
        status_code=501,
        detail="Endpoint não implementado - use POST /natal-chart para gerar mapas"
    )


@router.post("/transits", response_model=APIResponse)
async def calculate_transits(request: TransitRequest):
    """
    Calcula trânsitos planetários para uma data específica.

    Compara posições dos planetas na data especificada
    com o mapa natal do sujeito.
    """
    try:
        transit_data = await AsyncAstrologyService.calculate_transits(
            request.natal_subject,
            request.transit_date,
            request.orb_limit
        )

        return APIResponse(
            status="OK",
            data=transit_data.dict(),
            message="Trânsitos calculados com sucesso"
        )

    except ValueError as e:
        logger.error(f"Erro de validação: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/current-transits/{name}", response_model=APIResponse)
async def get_current_transits(
    name: str,
    year: int = Query(..., description="Ano de nascimento"),
    month: int = Query(..., ge=1, le=12, description="Mês de nascimento"),
    day: int = Query(..., ge=1, le=31, description="Dia de nascimento"),
    hour: int = Query(..., ge=0, le=23, description="Hora de nascimento"),
    minute: int = Query(..., ge=0, le=59, description="Minuto de nascimento"),
    city: str = Query(..., description="Cidade de nascimento"),
    nation: str = Query(..., description="País (código ISO)"),
    timezone: Optional[str] = Query(None, description="Timezone"),
    orb_limit: float = Query(5.0, ge=0.0, le=15.0, description="Limite do orbe")
):
    """
    Obtém trânsitos atuais para uma pessoa.

    Endpoint simplificado que calcula trânsitos para a data atual.
    """
    try:
        natal_request = AstrologicalSubjectRequest(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            city=city,
            nation=nation,
            timezone=timezone
        )

        current_date = datetime.now()

        transit_data = await AsyncAstrologyService.calculate_transits(
            natal_request,
            current_date,
            orb_limit
        )

        return APIResponse(
            status="OK",
            data=transit_data.dict(),
            message="Trânsitos atuais calculados com sucesso"
        )

    except ValueError as e:
        logger.error(f"Erro de validação: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")