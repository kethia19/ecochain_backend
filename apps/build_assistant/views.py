from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from .models import ClimateZone, Layout
from .serializers import (
    LayoutSerializer,
    LayoutUpdateSerializer,
    ClimateZoneSerializer,
)
from .image_service import generate_house_images, VALID_STYLES


class LayoutDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Build Assistant'], summary='Retrieve a saved layout by ID', responses={200: LayoutSerializer})
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


class GenerateImagesInputSerializer(serializers.Serializer):
    style    = serializers.ChoiceField(choices=VALID_STYLES)
    country  = serializers.CharField(max_length=100)
    bedrooms = serializers.IntegerField(min_value=1, max_value=10)


class GenerateImagesView(APIView):
    """
    POST /api/v1/layout/generate-images

    Generates ONE exterior and ONE interior render for the requested house
    via Pollinations AI (no API key required, free service).

    Response time: 1–2 minutes on cache miss (2 image API calls).
    Results are cached for 6 hours — identical inputs return instantly.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Build Assistant'],
        summary='Generate exterior + interior house renders',
        request=GenerateImagesInputSerializer,
    )
    def post(self, request):
        ser = GenerateImagesInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            result = generate_house_images(**ser.validated_data)
        except RuntimeError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(result)
