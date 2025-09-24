"""
Endpoints de health check e status da API.
"""

from fastapi import APIRouter
from ....schemas import APIResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=APIResponse)
def health_check():
    """Endpoint de health check da API."""
    return APIResponse(
        status="OK",
        data={"service": "Astrologer API", "version": "1.0.0"},
        message="Serviço funcionando corretamente"
    )


@router.get("/status", response_model=APIResponse)
def status():
    """Status detalhado da API."""
    return APIResponse(
        status="OK",
        data={
            "service": "Astrologer API",
            "version": "1.0.0",
            "features": [
                "Mapas natais",
                "Cálculos astrológicos",
                "Trânsitos",
                "Aspectos planetários"
            ]
        },
        message="API astrológica usando Kerykeion"
    )