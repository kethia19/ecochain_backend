from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.cache import cache

from drf_spectacular.utils import extend_schema, OpenApiExample

from .models import ClimateZone, Layout
from .serializers import (
    LayoutGenerateInputSerializer,
    LayoutSerializer,
    LayoutUpdateSerializer,
    MaterialSuggestInputSerializer,
    MaterialSuggestResponseSerializer,
    ClimateZoneSerializer,
)
from .services import generate_layout, suggest_eco_materials


class GenerateLayoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Build Assistant'],
        summary='Generate an optimised building layout',
        description=(
            'Accepts user preferences and returns a layout JSON with rooms, '
            'ventilation paths, passive features, and an eco score. '
            'The layout is persisted and its ID can be passed to the Cost Estimator.'
        ),
        request=LayoutGenerateInputSerializer,
        responses={201: LayoutSerializer},
        examples=[
            OpenApiExample(
                'Sahel 3-bedroom modern',
                value={'bedrooms': 3, 'climate_zone': 'sahel', 'style': 'modern', 'orientation': 'south'},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        ser = LayoutGenerateInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        layout_data = generate_layout(data)
        layout = Layout.objects.create(
            user=request.user,
            bedrooms=data['bedrooms'],
            climate_zone=data['climate_zone'],
            style=data['style'],
            orientation=data['orientation'],
            layout_json=layout_data['layout_json'],
            eco_score=layout_data['eco_score'],
            total_area_sqm=layout_data['total_area_sqm'],
        )
        return Response(LayoutSerializer(layout).data, status=status.HTTP_201_CREATED)


class SuggestMaterialsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Build Assistant'],
        summary='Suggest eco-friendly materials for a building element',
        description=(
            'Returns up to 4 eco material alternatives for the given element type '
            'and climate zone, each with a cost delta, carbon score, and a '
            'contextual prompt the frontend can surface to the user.'
        ),
        request=MaterialSuggestInputSerializer,
        responses={200: MaterialSuggestResponseSerializer},
        examples=[
            OpenApiExample(
                'Wall materials for Sahel',
                value={'element_type': 'wall', 'climate_zone': 'sahel'},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        ser = MaterialSuggestInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        cache_key = f'mat_suggest:{data["element_type"]}:{data["climate_zone"]}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        suggestions = suggest_eco_materials(data['element_type'], data['climate_zone'])
        payload = {'suggestions': suggestions}
        cache.set(cache_key, payload, timeout=3600)
        return Response(payload)


class LayoutDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Build Assistant'], summary='Retrieve a saved layout by ID')
    def get(self, request, layout_id):
        layout = get_object_or_404(Layout, id=layout_id, user=request.user)
        return Response(LayoutSerializer(layout).data)

    @extend_schema(
        tags=['Build Assistant'],
        summary='Update a layout (rename or swap materials)',
        request=LayoutUpdateSerializer,
        responses={200: LayoutSerializer},
    )
    def put(self, request, layout_id):
        layout = get_object_or_404(Layout, id=layout_id, user=request.user)
        ser = LayoutUpdateSerializer(layout, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(LayoutSerializer(layout).data)


class ClimateZonesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Build Assistant'],
        summary='List available African climate zone presets',
        responses={200: ClimateZoneSerializer(many=True)},
    )
    def get(self, request):
        zones = ClimateZone.objects.all()
        return Response(ClimateZoneSerializer(zones, many=True).data)
