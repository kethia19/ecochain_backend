"""
EcoChain Housing — EcoScore Views
===================================
File: apps/ecoscore/views.py
"""

import hashlib
import json
import logging

from django.core.cache import cache
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .service import calculate_ecoscore

logger = logging.getLogger(__name__)


def _cache_key(data: dict) -> str:
    h = hashlib.md5(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()
    return f"ecoscore:{h}"


class EcoScoreInputSerializer(serializers.Serializer):
    plants               = serializers.ListField(child=serializers.CharField(), default=list)
    materials            = serializers.ListField(child=serializers.CharField(), default=list)
    renewable_systems    = serializers.DictField(child=serializers.IntegerField(), default=dict)
    water_actions        = serializers.ListField(child=serializers.CharField(), default=list)
    waste_actions        = serializers.ListField(child=serializers.CharField(), default=list)
    maintenance_actions  = serializers.ListField(child=serializers.CharField(), default=list)
    trees_planted          = serializers.IntegerField(default=0, required=False)
    water_savings_percent  = serializers.FloatField(default=0.0, required=False)
    waste_recycled_percent = serializers.FloatField(default=0.0, required=False)


class EcoScoreCalculateView(APIView):
    """
    POST /api/v1/ecoscore/calculate

    Calculates a property's EcoScore (0–100) from its sustainability
    inputs — plants, materials, energy systems, water/waste actions, and
    maintenance practices. Reads weights and lookup values from the
    EcoScore_WestAfrica_Hackathon_Master.xlsx master dataset.

    Returns ecoScore, ratingBand, estimated annual carbonReductionKg,
    earnedBadges, and a per-category breakdown.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["EcoScore"], request=EcoScoreInputSerializer)
    def post(self, request):
        ser = EcoScoreInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        key    = _cache_key(data)
        cached = cache.get(key)
        if cached:
            return Response(cached)

        try:
            result = calculate_ecoscore(data)
        except RuntimeError as exc:
            logger.error("EcoScore dataset unavailable: %s", exc)
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:
            logger.error("EcoScore calculation error: %s", exc)
            return Response(
                {"detail": "EcoScore calculation failed. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        cache.set(key, result, timeout=3600)
        return Response(result)
