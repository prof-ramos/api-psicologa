"""
Serviço para cálculos astrológicos usando a biblioteca Kerykeion.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

from kerykeion import AstrologicalSubject, KerykeionChartSVG

from ..schemas.astrology import (
    AstrologicalSubjectRequest,
    AstrologicalSubjectResponse,
    PlanetPosition,
    HousePosition,
    AspectData,
    ChartResponse,
    TransitResponse
)
from ..core.cache import cache_astrological_subject, cache_natal_chart, cache_transits
from ..core.config import settings

logger = logging.getLogger(__name__)

# Thread pool for CPU-intensive calculations
calculation_executor = ThreadPoolExecutor(max_workers=4)


class AstrologyService:
    """Serviço para operações astrológicas usando Kerykeion."""

    @staticmethod
    def create_astrological_subject(request: AstrologicalSubjectRequest) -> AstrologicalSubject:
        """Cria um AstrologicalSubject do Kerykeion a partir do request."""
        try:
            return AstrologicalSubject(
                name=request.name,
                year=request.year,
                month=request.month,
                day=request.day,
                hour=request.hour,
                minute=request.minute,
                city=request.city,
                nation=request.nation,
                timezone=request.timezone
            )
        except Exception as e:
            logger.error(f"Erro ao criar AstrologicalSubject: {e}")
            raise ValueError(f"Dados inválidos para criar sujeito astrológico: {e}")

    @staticmethod
    def _extract_planet_positions(subject: AstrologicalSubject) -> List[PlanetPosition]:
        """Extrai posições dos planetas do sujeito astrológico."""
        planets = []

        try:
            # Kerykeion armazena planetas em diferentes atributos
            planet_data = subject.planets_degrees_ut()
            house_data = subject.houses_list()

            for planet_info in planet_data:
                if isinstance(planet_info, dict):
                    planet = PlanetPosition(
                        name=planet_info.get('name', ''),
                        longitude=planet_info.get('position', 0.0),
                        latitude=planet_info.get('latitude', 0.0),
                        distance=planet_info.get('distance'),
                        speed=planet_info.get('speed'),
                        sign=planet_info.get('sign', ''),
                        house=planet_info.get('house', 1),
                        retrograde=planet_info.get('retrograde', False)
                    )
                    planets.append(planet)

        except Exception as e:
            logger.warning(f"Erro ao extrair posições dos planetas: {e}")

        return planets

    @staticmethod
    def _extract_house_positions(subject: AstrologicalSubject) -> List[HousePosition]:
        """Extrai posições das casas do sujeito astrológico."""
        houses = []

        try:
            houses_data = subject.houses_list()

            for i, house_info in enumerate(houses_data):
                if isinstance(house_info, dict):
                    house = HousePosition(
                        house_number=i + 1,
                        longitude=house_info.get('position', 0.0),
                        sign=house_info.get('sign', '')
                    )
                    houses.append(house)

        except Exception as e:
            logger.warning(f"Erro ao extrair posições das casas: {e}")

        return houses

    @staticmethod
    def _extract_aspects(subject: AstrologicalSubject) -> List[AspectData]:
        """Extrai aspectos do sujeito astrológico."""
        aspects = []

        try:
            aspects_data = subject.aspects_list()

            for aspect_info in aspects_data:
                if isinstance(aspect_info, dict):
                    aspect = AspectData(
                        planet1=aspect_info.get('planet1', ''),
                        planet2=aspect_info.get('planet2', ''),
                        aspect=aspect_info.get('aspect', ''),
                        orb=aspect_info.get('orb', 0.0),
                        applying=aspect_info.get('applying', False)
                    )
                    aspects.append(aspect)

        except Exception as e:
            logger.warning(f"Erro ao extrair aspectos: {e}")

        return aspects

    @classmethod
    @cache_astrological_subject()
    def get_astrological_data(cls, request: AstrologicalSubjectRequest) -> AstrologicalSubjectResponse:
        """Obtém dados astrológicos completos para um sujeito."""
        try:
            subject = cls.create_astrological_subject(request)

            # Extrair dados do sujeito
            birth_date = datetime(
                year=request.year,
                month=request.month,
                day=request.day,
                hour=request.hour,
                minute=request.minute
            )

            planets = cls._extract_planet_positions(subject)
            houses = cls._extract_house_positions(subject)
            aspects = cls._extract_aspects(subject)

            return AstrologicalSubjectResponse(
                name=subject.name,
                birth_date=birth_date,
                city=subject.city,
                nation=subject.nation,
                latitude=getattr(subject, 'lat', 0.0),
                longitude=getattr(subject, 'lng', 0.0),
                timezone=getattr(subject, 'timezone', 'UTC'),
                planets=planets,
                houses=houses,
                aspects=aspects,
                lunar_phase=getattr(subject, 'lunar_phase', None)
            )

        except Exception as e:
            logger.error(f"Erro ao obter dados astrológicos: {e}")
            raise ValueError(f"Erro nos cálculos astrológicos: {e}")

    @classmethod
    @cache_natal_chart()
    def generate_natal_chart(
        cls,
        request: AstrologicalSubjectRequest,
        chart_type: str = "natal",
        include_aspects: bool = True
    ) -> ChartResponse:
        """Gera mapa natal em SVG."""
        try:
            subject = cls.create_astrological_subject(request)

            # Gerar mapa usando Kerykeion
            chart = KerykeionChartSVG(subject)

            # Configurar opções do mapa
            if hasattr(chart, 'chart_type'):
                chart.chart_type = chart_type

            # Gerar SVG
            svg_content = chart.makeSVG()

            # Obter dados do mapa
            chart_data = subject.json(dump=False) if hasattr(subject, 'json') else {}

            return ChartResponse(
                chart_data=chart_data,
                svg_content=svg_content,
                chart_type=chart_type,
                house_system="Placidus",  # Padrão do Kerykeion
                calculation_date=datetime.now()
            )

        except Exception as e:
            logger.error(f"Erro ao gerar mapa natal: {e}")
            raise ValueError(f"Erro na geração do mapa: {e}")

    @classmethod
    @cache_transits()
    def calculate_transits(
        cls,
        natal_request: AstrologicalSubjectRequest,
        transit_date: datetime,
        orb_limit: float = 5.0
    ) -> TransitResponse:
        """Calcula trânsitos para uma data específica."""
        try:
            # Criar sujeito natal
            natal_subject = cls.create_astrological_subject(natal_request)

            # Criar sujeito para data de trânsito
            transit_request = AstrologicalSubjectRequest(
                name=f"{natal_request.name}_transit",
                year=transit_date.year,
                month=transit_date.month,
                day=transit_date.day,
                hour=transit_date.hour,
                minute=transit_date.minute,
                city=natal_request.city,
                nation=natal_request.nation,
                timezone=natal_request.timezone
            )

            transit_subject = cls.create_astrological_subject(transit_request)

            # Calcular trânsitos (simplificado - pode ser expandido)
            transits = []
            active_aspects = []

            # TODO: Implementar lógica detalhada de trânsitos
            # Esta é uma implementação básica que pode ser expandida

            return TransitResponse(
                natal_subject=natal_subject.name,
                transit_date=transit_date,
                transits=transits,
                active_aspects=active_aspects
            )

        except Exception as e:
            logger.error(f"Erro ao calcular trânsitos: {e}")
            raise ValueError(f"Erro nos cálculos de trânsito: {e}")