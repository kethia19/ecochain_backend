"""
EcoChain Housing — All AI/ML Django Views
==========================================
Team:    AI/ML (Group 15)
File:    apps/ai_engine/views.py

Wires all AI/ML functions to DRF endpoints.
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

from .ml_service import predict_plants, model_is_ready
from .ai_service import generate_layout, suggest_materials, generate_tco_projection, estimate_cost_standalone
logger = logging.getLogger(__name__)

CLIMATE_ZONES = [
    "Sahel", "Equatorial", "Subtropical Coastal", "Highland",
    "Semi-arid", "Arid", "Tropical Humid",
]
COUNTRIES = ["Kenya", "Nigeria", "Ghana", "Ethiopia", "South Africa", "Senegal"]


# ============================================================================
# Input serializers
# ============================================================================

class GreenMatchSerializer(serializers.Serializer):
    climate_zone      = serializers.CharField(max_length=100)
    sun_exposure      = serializers.ChoiceField(choices=["Full Sun", "Partial Shade"])
    soil_type         = serializers.CharField(max_length=100)
    water_need        = serializers.ChoiceField(
        choices=["Very Low", "Low", "Moderate", "High", "Very High"]
    )
    drought_tolerance = serializers.ChoiceField(
        choices=["Low", "Medium", "High", "Very High"], default="Medium"
    )
    growth_rate       = serializers.ChoiceField(
        choices=["Very Slow", "Slow", "Moderate", "Fast", "Very Fast"], default="Moderate"
    )
    maintenance_level = serializers.ChoiceField(
        choices=["Very Low", "Low", "Medium", "High"], default="Low"
    )
    plant_type        = serializers.CharField(max_length=100, default="Unknown")
    top_n             = serializers.IntegerField(min_value=1, max_value=20, default=10)


class LayoutSerializer(serializers.Serializer):
    bedrooms     = serializers.IntegerField(min_value=1, max_value=6)
    climate_zone = serializers.ChoiceField(choices=CLIMATE_ZONES)
    style        = serializers.ChoiceField(choices=["modern", "traditional"])
    orientation  = serializers.ChoiceField(choices=["north", "south", "east", "west"])
    lot_size_sqm = serializers.FloatField(min_value=40, max_value=2000, default=120)
    budget_usd   = serializers.FloatField(required=False, allow_null=True)


class MaterialSerializer(serializers.Serializer):
    element_type     = serializers.CharField(max_length=50)
    climate_zone     = serializers.ChoiceField(choices=CLIMATE_ZONES)
    country          = serializers.ChoiceField(choices=COUNTRIES, default="Kenya")
    current_material = serializers.CharField(max_length=100, required=False, allow_null=True)
    budget_level     = serializers.ChoiceField(
        choices=["low", "medium", "high"], default="medium"
    )


class TCOSerializer(serializers.Serializer):
    layout_id        = serializers.CharField(max_length=100)
    climate_zone     = serializers.ChoiceField(choices=CLIMATE_ZONES)
    country          = serializers.ChoiceField(choices=COUNTRIES)
    house_size_sqm   = serializers.FloatField(min_value=20, max_value=2000)
    materials_chosen = serializers.ListField(
        child=serializers.DictField(), allow_empty=True, default=list
    )
    upfront_cost_usd = serializers.FloatField(min_value=0)
    household_size   = serializers.IntegerField(min_value=1, max_value=20, default=4)


# ============================================================================
# Helper — cache key from request data
# ============================================================================

def _cache_key(prefix: str, data: dict) -> str:
    h = hashlib.md5(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()
    return f"{prefix}:{h}"


# ============================================================================
# Views
# ============================================================================

class GreenMatchView(APIView):
    """POST /api/v1/green-match/ — plant prediction using ML model."""
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Green Match'], request=GreenMatchSerializer)
    def post(self, request):
        s = GreenMatchSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        key    = _cache_key("gm", data)
        cached = cache.get(key)
        if cached:
            return Response(cached)

        try:
            matches = predict_plants(**data)
        except RuntimeError as exc:
            logger.error("Green Match ML error: %s", exc)
            return Response(
                {"detail": "Plant prediction model not ready. Check server logs."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        payload = {"matches": matches, "ml_active": model_is_ready()}
        cache.set(key, payload, timeout=86400)
        return Response(payload)


class GreenMatchStatusView(APIView):
    """GET /api/v1/green-match/status/ — check if ML model is loaded."""
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Green Match'])
    def get(self, request):
        ready = model_is_ready()
        return Response({
            "ml_model_ready": ready,
            "status": "ok" if ready else "model_not_loaded",
        })


class LayoutGenerateView(APIView):
    """POST /api/v1/layout/generate — AI eco-layout generation."""
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Build Assistant'], request=LayoutSerializer)
    def post(self, request):
        s = LayoutSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        key    = _cache_key("layout", data)
        cached = cache.get(key)
        if cached:
            return Response(cached)

        try:
            result = generate_layout(**data)
        except (ValueError, Exception) as exc:
            logger.error("Layout generation error: %s", exc)
            return Response(
                {"detail": "Layout generation failed. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        cache.set(key, result, timeout=3600)
        return Response(result)


class MaterialSuggestView(APIView):
    """POST /api/v1/materials/suggest — AI eco material suggestions."""
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Build Assistant'], request=MaterialSerializer)
    def post(self, request):
        s = MaterialSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        key    = _cache_key("mats", data)
        cached = cache.get(key)
        if cached:
            return Response(cached)

        try:
            result = suggest_materials(**data)
        except (ValueError, Exception) as exc:
            logger.error("Material suggestion error: %s", exc)
            return Response(
                {"detail": "Material suggestion failed. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        cache.set(key, result, timeout=3600)
        return Response(result)


class TCOProjectionView(APIView):
    """POST /api/v1/cost/tco-projection — 5-year savings projection."""
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Cost Estimator'], request=TCOSerializer)
    def post(self, request):
        s = TCOSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        key    = _cache_key("tco", data)
        cached = cache.get(key)
        if cached:
            return Response(cached)

        try:
            result = generate_tco_projection(**data)
        except (ValueError, Exception) as exc:
            logger.error("TCO projection error: %s", exc)
            return Response(
                {"detail": "TCO projection failed. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        cache.set(key, result, timeout=7200)
        return Response(result)


# ============================================================================
# Standalone cost estimate — no layout_id, driven by the form fields directly
# POST /api/v1/cost/estimate
# ============================================================================

class StandaloneEstimateSerializer(serializers.Serializer):
    houseType        = serializers.CharField(max_length=100)
    country          = serializers.ChoiceField(choices=COUNTRIES)
    city             = serializers.CharField(max_length=100, default="")
    size             = serializers.FloatField(min_value=10, max_value=5000)
    rooms            = serializers.IntegerField(min_value=1, max_value=20, default=3)
    ecoLevel         = serializers.ChoiceField(
        choices=["Low", "Medium", "High"], default="Medium"
    )
    powerPreference  = serializers.CharField(max_length=100, default="Grid")
    budget           = serializers.FloatField(required=False, allow_null=True, default=None)
    materials        = serializers.DictField(
        child=serializers.CharField(), required=False, allow_null=True, default=None
    )
    features         = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True, default=list
    )
    # Also accept camelCase alias "budgetRange" as [min, max]; we use the midpoint
    budgetRange      = serializers.ListField(
        child=serializers.FloatField(), required=False, allow_null=True, default=None
    )


class StandaloneEstimateView(APIView):
    """
    POST /api/v1/cost/estimate

    Accepts the Build Assistant / Cost Estimator form fields and returns a
    full construction cost breakdown + 5-year eco savings in one call.
    No layout_id or prior Build Assistant step required.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Cost Estimator'], request=StandaloneEstimateSerializer)
    def post(self, request):
        s = StandaloneEstimateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        # Resolve budget: prefer explicit "budget", fall back to midpoint of "budgetRange"
        budget = data.get("budget")
        if not budget and data.get("budgetRange"):
            rng = data["budgetRange"]
            budget = sum(rng) / len(rng) if rng else None

        key    = _cache_key("ce_standalone", {**data, "budget": budget})
        cached = cache.get(key)
        if cached:
            return Response(cached)

        try:
            result = estimate_cost_standalone(
                house_type=data["houseType"],
                country=data["country"],
                city=data["city"],
                size_sqm=data["size"],
                rooms=data["rooms"],
                eco_level=data["ecoLevel"],
                power_preference=data["powerPreference"],
                budget=budget,
                materials=data.get("materials"),
                features=data.get("features") or [],
            )
        except (ValueError, Exception) as exc:
            logger.error("Standalone cost estimate error: %s", exc)
            return Response(
                {"detail": "Cost estimation failed. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        cache.set(key, result, timeout=3600)
        return Response(result)
