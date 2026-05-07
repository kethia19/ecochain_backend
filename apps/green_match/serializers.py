"""
Green Match serializers — input validation for the request payload.
"""
from rest_framework import serializers


SUN_CHOICES = ['full_sun', 'partial', 'shade']
SOIL_CHOICES = ['lateritic_red_clay', 'loamy', 'sandy', 'clay', 'peat']
WATER_CHOICES = ['high', 'moderate', 'low', 'ultra_low']


class GreenMatchInputSerializer(serializers.Serializer):
    location = serializers.CharField(max_length=255)
    sun_exposure = serializers.ChoiceField(choices=SUN_CHOICES)
    soil_condition = serializers.ChoiceField(choices=SOIL_CHOICES)
    water_conservation = serializers.ChoiceField(choices=WATER_CHOICES)


class MatchedPlantSerializer(serializers.Serializer):
    """Documentation-only — the shape of one entry in `matches`."""
    id = serializers.UUIDField()
    name = serializers.CharField()
    scientific_name = serializers.CharField()
    match_score = serializers.IntegerField()
    tags = serializers.ListField(child=serializers.CharField())
    care_tips = serializers.ListField(child=serializers.CharField())
    image_url = serializers.URLField()
    impact_label = serializers.CharField()


class GreenMatchResponseSerializer(serializers.Serializer):
    matches = MatchedPlantSerializer(many=True)
    climate_zone = serializers.CharField()
