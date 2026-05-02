"""
Dashboard view — aggregates user data from multiple apps into a single payload.
Cached per-user in Redis with a 5-minute TTL.
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.core.cache import cache
from django.db.models import Sum

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.authentication.serializers import UserSerializer
from apps.plants.models import UserPlant, CareTask
from apps.plants.serializers import UserPlantSerializer, CareTaskSerializer
from apps.impact.models import ImpactLog


CACHE_TTL_SECONDS = 300  # 5 minutes


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Dashboard'],
        summary="Aggregated home-screen payload for the authenticated user",
        responses={200: OpenApiResponse(description='Dashboard payload')},
    )
    def get(self, request):
        user = request.user
        cache_key = f'dashboard:{user.id}'

        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        plants_qs = (
            UserPlant.objects
            .filter(user=user)
            .select_related('plant')
        )
        tasks_qs = (
            CareTask.objects
            .filter(user=user, completed=False)
            .order_by('due_date')[:5]
        )
        stats = ImpactLog.objects.filter(user=user).aggregate(
            water=Sum('water_saved_litres'),
            co2=Sum('co2_offset_kg'),
        )

        payload = {
            'user': UserSerializer(user).data,
            'plants': UserPlantSerializer(plants_qs, many=True).data,
            'upcomingTasks': CareTaskSerializer(tasks_qs, many=True).data,
            'impactStats': {
                'waterSavedLitres': float(stats['water'] or 0),
                'co2OffsetKg': float(stats['co2'] or 0),
            },
        }

        cache.set(cache_key, payload, timeout=CACHE_TTL_SECONDS)
        return Response(payload)
