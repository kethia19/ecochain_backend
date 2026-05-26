from rest_framework import serializers
from .models import SavedRecommendation


class SavedRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedRecommendation
        fields = ['id', 'recommendation_type', 'title', 'data', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SavedRecommendationListSerializer(serializers.ModelSerializer):
    """Lightweight version for the list view — doesn't include the full data blob."""
    class Meta:
        model = SavedRecommendation
        fields = ['id', 'recommendation_type', 'title', 'created_at']
        read_only_fields = fields