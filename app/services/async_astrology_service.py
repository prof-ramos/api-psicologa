"""
Async version of astrological calculations service.
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

# Dedicated thread pool for astrological calculations
astro_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="astro")


class AsyncAstrologyService:
    """Async service for astrological operations using Kerykeion."""

    @staticmethod
    def create_astrological_subject(request: AstrologicalSubjectRequest) -> AstrologicalSubject:
        """Create AstrologicalSubject from request - CPU intensive, runs in thread."""
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
            logger.error(f"Error creating AstrologicalSubject: {e}")
            raise ValueError(f"Invalid data for astrological subject: {e}")

    @staticmethod
    def _extract_planet_positions(subject: AstrologicalSubject) -> List[PlanetPosition]:
        """Extract planet positions from astrological subject."""
        planets = []

        try:
            planet_data = subject.planets_degrees_ut()

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
            logger.warning(f"Error extracting planet positions: {e}")

        return planets

    @staticmethod
    def _extract_house_positions(subject: AstrologicalSubject) -> List[HousePosition]:
        """Extract house positions from astrological subject."""
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
            logger.warning(f"Error extracting house positions: {e}")

        return houses

    @staticmethod
    def _extract_aspects(subject: AstrologicalSubject) -> List[AspectData]:
        """Extract aspects from astrological subject."""
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
            logger.warning(f"Error extracting aspects: {e}")

        return aspects

    @classmethod
    def _get_astrological_data_sync(cls, request: AstrologicalSubjectRequest) -> AstrologicalSubjectResponse:
        """Synchronous version for thread execution."""
        try:
            subject = cls.create_astrological_subject(request)

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
            logger.error(f"Error getting astrological data: {e}")
            raise ValueError(f"Error in astrological calculations: {e}")

    @classmethod
    @cache_astrological_subject()
    async def get_astrological_data(cls, request: AstrologicalSubjectRequest) -> AstrologicalSubjectResponse:
        """Get complete astrological data for a subject (async)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            astro_executor,
            cls._get_astrological_data_sync,
            request
        )

    @classmethod
    def _generate_natal_chart_sync(
        cls,
        request: AstrologicalSubjectRequest,
        chart_type: str = "natal",
        include_aspects: bool = True
    ) -> ChartResponse:
        """Synchronous natal chart generation for thread execution."""
        try:
            subject = cls.create_astrological_subject(request)

            # Generate chart using Kerykeion
            chart = KerykeionChartSVG(subject)

            # Configure chart options
            if hasattr(chart, 'chart_type'):
                chart.chart_type = chart_type

            # Generate SVG
            svg_content = chart.makeSVG()

            # Get chart data
            chart_data = subject.json(dump=False) if hasattr(subject, 'json') else {}

            return ChartResponse(
                chart_data=chart_data,
                svg_content=svg_content,
                chart_type=chart_type,
                house_system="Placidus",
                calculation_date=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error generating natal chart: {e}")
            raise ValueError(f"Error in chart generation: {e}")

    @classmethod
    @cache_natal_chart()
    async def generate_natal_chart(
        cls,
        request: AstrologicalSubjectRequest,
        chart_type: str = "natal",
        include_aspects: bool = True
    ) -> ChartResponse:
        """Generate natal chart in SVG format (async)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            astro_executor,
            cls._generate_natal_chart_sync,
            request,
            chart_type,
            include_aspects
        )

    @classmethod
    def _calculate_transits_sync(
        cls,
        natal_request: AstrologicalSubjectRequest,
        transit_date: datetime,
        orb_limit: float = 5.0
    ) -> TransitResponse:
        """Synchronous transit calculation for thread execution."""
        try:
            # Create natal subject
            natal_subject = cls.create_astrological_subject(natal_request)

            # Create subject for transit date
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

            # Calculate transits (simplified - can be expanded)
            transits = []
            active_aspects = []

            # TODO: Implement detailed transit logic
            # This is a basic implementation that can be expanded

            return TransitResponse(
                natal_subject=natal_subject.name,
                transit_date=transit_date,
                transits=transits,
                active_aspects=active_aspects
            )

        except Exception as e:
            logger.error(f"Error calculating transits: {e}")
            raise ValueError(f"Error in transit calculations: {e}")

    @classmethod
    @cache_transits()
    async def calculate_transits(
        cls,
        natal_request: AstrologicalSubjectRequest,
        transit_date: datetime,
        orb_limit: float = 5.0
    ) -> TransitResponse:
        """Calculate transits for a specific date (async)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            astro_executor,
            cls._calculate_transits_sync,
            natal_request,
            transit_date,
            orb_limit
        )

    @classmethod
    async def batch_calculate(cls, requests: List[AstrologicalSubjectRequest]) -> List[AstrologicalSubjectResponse]:
        """Calculate multiple astrological subjects in parallel."""
        tasks = [cls.get_astrological_data(request) for request in requests]
        return await asyncio.gather(*tasks)

    @classmethod
    async def health_check(cls) -> Dict[str, Any]:
        """Perform health check on astrological calculations."""
        try:
            # Quick test calculation
            test_request = AstrologicalSubjectRequest(
                name="health_check",
                year=2000,
                month=1,
                day=1,
                hour=12,
                minute=0,
                city="London",
                nation="GB"
            )

            start_time = asyncio.get_event_loop().time()
            await cls.get_astrological_data(test_request)
            end_time = asyncio.get_event_loop().time()

            return {
                "status": "healthy",
                "calculation_time": f"{(end_time - start_time) * 1000:.2f}ms",
                "executor_active_threads": astro_executor._threads,
                "executor_max_workers": astro_executor._max_workers
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }