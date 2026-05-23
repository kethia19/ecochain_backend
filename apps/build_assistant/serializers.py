from rest_framework import serializers
from .models import ClimateZone, EcoMaterial, Layout

CLIMATE_ZONE_CODES = [
    'sahel', 'equatorial', 'subtropical_coastal',
    'semi_arid', 'highland', 'tropical_wet',
]
STYLE_CHOICES = ['modern', 'traditional', 'hybrid']
ORIENTATION_CHOICES = ['north', 'south', 'east', 'west']
ELEMENT_CHOICES = ['wall', 'foundation', 'roof', 'floor', 'window', 'insulation']


class LayoutGenerateInputSerializer(serializers.Serializer):
    bedrooms = serializers.IntegerField(min_value=1, max_value=10)
    climate_zone = serializers.ChoiceField(choices=CLIMATE_ZONE_CODES)
    style = serializers.ChoiceField(choices=STYLE_CHOICES, default='modern')
    orientation = serializers.ChoiceField(choices=ORIENTATION_CHOICES, default='south')


class LayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layout
        fields = [
            'id', 'name', 'bedrooms', 'climate_zone', 'style', 'orientation',
            'layout_json', 'eco_score', 'selected_materials', 'total_area_sqm',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'eco_score', 'layout_json', 'total_area_sqm', 'created_at', 'updated_at']


class LayoutUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layout
        fields = ['name', 'selected_materials']


class EcoMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcoMaterial
        fields = [
            'id', 'name', 'element_type', 'description',
            'sustainability_rationale', 'carbon_score', 'cost_delta_pct',
        ]


class MaterialSuggestInputSerializer(serializers.Serializer):
    element_type = serializers.ChoiceField(choices=ELEMENT_CHOICES)
    climate_zone = serializers.ChoiceField(choices=CLIMATE_ZONE_CODES)


class MaterialSuggestionItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    element_type = serializers.CharField()
    description = serializers.CharField()
    sustainability_rationale = serializers.CharField()
    carbon_score = serializers.FloatField()
    cost_delta_pct = serializers.FloatField()
    prompt = serializers.CharField()


class MaterialSuggestResponseSerializer(serializers.Serializer):
    suggestions = MaterialSuggestionItemSerializer(many=True)


class ClimateZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClimateZone
        fields = [
            'id', 'code', 'name', 'description',
            'typical_countries', 'cooling_strategy', 'passive_features',
        ]
