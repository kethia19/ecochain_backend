from rest_framework import serializers
from .models import MaterialPrice, LabourRate, CostEstimate, TCOProjection

COUNTRY_CODES = ['NG', 'KE', 'GH', 'ET', 'ZA', 'SN']
CATEGORY_CHOICES = ['wall', 'foundation', 'roof', 'floor', 'window', 'insulation', 'finishing']


# ── Pricing ─────────────────────────────────────────────────────────────────

class MaterialPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialPrice
        fields = [
            'id', 'name', 'category', 'unit', 'price_per_unit',
            'currency', 'country', 'city', 'carbon_score', 'is_eco', 'last_updated',
        ]


class LabourRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabourRate
        fields = [
            'id', 'skill_type', 'country', 'city',
            'rate_per_day', 'currency', 'last_updated',
        ]


# ── Cost Estimate ────────────────────────────────────────────────────────────

class CostEstimateInputSerializer(serializers.Serializer):
    layout_id = serializers.UUIDField()
    country = serializers.ChoiceField(choices=COUNTRY_CODES)
    city = serializers.CharField(max_length=100, required=False, default='')
    labour_zone = serializers.ChoiceField(choices=COUNTRY_CODES, required=False)

    def validate(self, data):
        if 'labour_zone' not in data or not data.get('labour_zone'):
            data['labour_zone'] = data['country']
        return data


class CostBreakdownItemSerializer(serializers.Serializer):
    category = serializers.CharField()
    description = serializers.CharField()
    unit_cost = serializers.FloatField()
    quantity = serializers.FloatField()
    total = serializers.FloatField()
    currency = serializers.CharField()


class CostEstimateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostEstimate
        fields = [
            'id', 'layout_id', 'country', 'city',
            'total_cost', 'currency', 'breakdown', 'created_at',
        ]


# ── TCO Projection ───────────────────────────────────────────────────────────

class TCOInputSerializer(serializers.Serializer):
    layout_id = serializers.UUIDField()
    country = serializers.ChoiceField(choices=COUNTRY_CODES)
    projection_years = serializers.IntegerField(min_value=1, max_value=30, default=5)


class SavingsBreakdownSerializer(serializers.Serializer):
    category = serializers.CharField()
    annual_saving = serializers.FloatField()
    description = serializers.CharField()


class TCOProjectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TCOProjection
        fields = [
            'id', 'layout_id', 'upfront_cost', 'currency',
            'projection_years', 'annual_savings', 'total_savings',
            'payback_months', 'savings_breakdown', 'created_at',
        ]
