"""
Plants serializers.
"""
from rest_framework import serializers
from .models import Plant, UserPlant, CareTask


class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = [
            'id', 'name', 'scientific_name',
            'climate_zones', 'sun_exposure', 'soil_types',
            'water_conservation', 'water_frequency',
            'tags', 'care_tips', 'impact_label', 'image_url',
        ]


class UserPlantSerializer(serializers.ModelSerializer):
    plant = PlantSerializer(read_only=True)
    plant_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = UserPlant
        fields = ['id', 'plant', 'plant_id', 'nickname', 'added_at']
        read_only_fields = ['id', 'added_at']

    def create(self, validated_data):
        plant_id = validated_data.pop('plant_id')
        return UserPlant.objects.create(
            user=self.context['request'].user,
            plant_id=plant_id,
            **validated_data,
        )


class CareTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareTask
        fields = [
            'id', 'task_type', 'description', 'due_date',
            'completed', 'user_plant', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
