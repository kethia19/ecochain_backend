"""
Green Match view.
"""
import hashlib
import json

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.core.cache import cache

from drf_spectacular.utils import extend_schema, OpenApiExample

from apps.plants.models import Plant
from apps.plants.serializers import PlantSerializer

from .models import MatchSession
from .serializers import (
    GreenMatchInputSerializer,
    GreenMatchResponseSerializer,
)
from .services import enrich_location, score_plants


CACHE_TTL_SECONDS = 60 * 60 * 24  # 24 hours
TOP_N = 10
# Plants below this score are filtered out — keeps the response focused on
# genuinely relevant recommendations rather than padding with weak matches.
MIN_SCORE = 50


class GreenMatchView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Green Match'],
        summary='Recommend native African plants for a user plot',
        request=GreenMatchInputSerializer,
        responses={200: GreenMatchResponseSerializer},
        examples=[
            OpenApiExample(
                'Nairobi loamy garden',
                value={
                    'location': 'Nairobi, Kenya',
                    'sun_exposure': 'full_sun',
                    'soil_condition': 'loamy',
                    'water_conservation': 'low',
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = GreenMatchInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Cache key = hash of inputs. Same inputs → same payload for 24h.
        cache_key = 'gm:' + hashlib.md5(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()

        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        geo = enrich_location(data['location'])

        plants = list(Plant.objects.filter(sun_exposure__contains=[data['sun_exposure']]))
        ranked = score_plants(
            plants,
            climate_zone=geo['climate_zone'],
            sun_exposure=data['sun_exposure'],
            soil_condition=data['soil_condition'],
            water_conservation=data['water_conservation'],
        )

        # Filter weak matches, then take the top N. If the threshold filters
        # everything out (e.g. very specific input + small catalogue), fall
        # back to the top 3 so the user always sees something.
        strong = [r for r in ranked if r['score'] >= MIN_SCORE][:TOP_N]
        if not strong:
            strong = ranked[:3]

        payload = {
            'climate_zone': geo['climate_zone'],
            'matches': [
                {**PlantSerializer(r['plant']).data, 'match_score': r['score']}
                for r in strong
            ],
        }

        cache.set(cache_key, payload, timeout=CACHE_TTL_SECONDS)

        # Persist a session so we can show match history on the dashboard.
        MatchSession.objects.create(
            user=request.user,
            location=data['location'],
            sun_exposure=data['sun_exposure'],
            soil_condition=data['soil_condition'],
            water_conservation=data['water_conservation'],
            climate_zone=geo['climate_zone'],
            top_match_count=len(payload['matches']),
        )

        return Response(payload)
