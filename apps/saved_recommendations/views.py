from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import SavedRecommendation
from .serializers import (
    SavedRecommendationSerializer,
    SavedRecommendationListSerializer,
)


class SavedRecommendationListCreateView(APIView):
    """GET = list mine, POST = save new."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Saved Recommendations'],
        summary='List my saved recommendations',
        parameters=[
            OpenApiParameter(
                'type', OpenApiTypes.STR, OpenApiParameter.QUERY,
                description='Filter by type: "layout" or "cost_estimate". Omit to get all.',
                required=False,
            ),
        ],
        responses={200: SavedRecommendationListSerializer(many=True)},
    )
    def get(self, request):
        qs = SavedRecommendation.objects.filter(user=request.user)
        type_filter = request.query_params.get('type')
        if type_filter:
            qs = qs.filter(recommendation_type=type_filter)
        return Response(SavedRecommendationListSerializer(qs, many=True).data)

    @extend_schema(
        tags=['Saved Recommendations'],
        summary='Save a recommendation to my profile',
        request=SavedRecommendationSerializer,
        responses={201: SavedRecommendationSerializer},
    )
    def post(self, request):
        ser = SavedRecommendationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        rec = ser.save(user=request.user)
        return Response(
            SavedRecommendationSerializer(rec).data,
            status=status.HTTP_201_CREATED,
        )


class SavedRecommendationDetailView(APIView):
    """GET one, DELETE one. Only owner can access."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Saved Recommendations'],
        summary='Get a saved recommendation by ID',
        responses={200: SavedRecommendationSerializer},
    )
    def get(self, request, recommendation_id):
        rec = get_object_or_404(
            SavedRecommendation, id=recommendation_id, user=request.user,
        )
        return Response(SavedRecommendationSerializer(rec).data)

    @extend_schema(
        tags=['Saved Recommendations'],
        summary='Delete a saved recommendation',
        responses={204: None},
    )
    def delete(self, request, recommendation_id):
        rec = get_object_or_404(
            SavedRecommendation, id=recommendation_id, user=request.user,
        )
        rec.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)