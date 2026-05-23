"""
Seed material prices and labour rates across 6 African countries.
All prices are in local currency. Source: Q1 2025 market surveys.
The Data Team should update these via the admin or a pipeline as rates change.
"""
from django.core.management.base import BaseCommand
from apps.cost_estimator.models import MaterialPrice, LabourRate

MATERIAL_PRICES = [
    # ── Nigeria (NGN) ────────────────────────────────────────────────────────
    {'name': 'Compressed Earth Blocks (CEB)', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 6500, 'currency': 'NGN', 'country': 'NG', 'city': '', 'carbon_score': 1.2, 'is_eco': True},
    {'name': 'Sandcrete Block Wall', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 8200, 'currency': 'NGN', 'country': 'NG', 'city': '', 'carbon_score': 5.5, 'is_eco': False},
    {'name': 'Sandcrete Block Wall', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 9000, 'currency': 'NGN', 'country': 'NG', 'city': 'Lagos', 'carbon_score': 5.5, 'is_eco': False},
    {'name': 'Pozzolana Cement Foundation', 'category': 'foundation', 'unit': 'sqm', 'price_per_unit': 22000, 'currency': 'NGN', 'country': 'NG', 'city': '', 'carbon_score': 4.5, 'is_eco': True},
    {'name': 'OPC Concrete Foundation', 'category': 'foundation', 'unit': 'sqm', 'price_per_unit': 26000, 'currency': 'NGN', 'country': 'NG', 'city': '', 'carbon_score': 7.8, 'is_eco': False},
    {'name': 'Recycled Metal Sheet (Cool Roof)', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 5500, 'currency': 'NGN', 'country': 'NG', 'city': '', 'carbon_score': 3.0, 'is_eco': True},
    {'name': 'Corrugated Iron Sheet', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 6200, 'currency': 'NGN', 'country': 'NG', 'city': '', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Stabilised Earth Floor', 'category': 'floor', 'unit': 'sqm', 'price_per_unit': 3800, 'currency': 'NGN', 'country': 'NG', 'city': '', 'carbon_score': 0.6, 'is_eco': True},
    {'name': 'Ceramic Tile Floor', 'category': 'floor', 'unit': 'sqm', 'price_per_unit': 9500, 'currency': 'NGN', 'country': 'NG', 'city': '', 'carbon_score': 4.8, 'is_eco': False},
    {'name': 'Plaster & Paint Finishing', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 4200, 'currency': 'NGN', 'country': 'NG', 'city': '', 'carbon_score': 2.1, 'is_eco': False},

    # ── Kenya (KES) ──────────────────────────────────────────────────────────
    {'name': 'Compressed Earth Blocks (CEB)', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 1800, 'currency': 'KES', 'country': 'KE', 'city': '', 'carbon_score': 1.2, 'is_eco': True},
    {'name': 'Burnt Brick Wall', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 2400, 'currency': 'KES', 'country': 'KE', 'city': '', 'carbon_score': 5.8, 'is_eco': False},
    {'name': 'Burnt Brick Wall', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 2900, 'currency': 'KES', 'country': 'KE', 'city': 'Nairobi', 'carbon_score': 5.8, 'is_eco': False},
    {'name': 'Pozzolana Cement Foundation', 'category': 'foundation', 'unit': 'sqm', 'price_per_unit': 6500, 'currency': 'KES', 'country': 'KE', 'city': '', 'carbon_score': 4.5, 'is_eco': True},
    {'name': 'OPC Concrete Foundation', 'category': 'foundation', 'unit': 'sqm', 'price_per_unit': 7800, 'currency': 'KES', 'country': 'KE', 'city': '', 'carbon_score': 7.8, 'is_eco': False},
    {'name': 'Corrugated Iron Sheet', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 1600, 'currency': 'KES', 'country': 'KE', 'city': '', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Natural Thatch Roofing', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 900, 'currency': 'KES', 'country': 'KE', 'city': '', 'carbon_score': 0.5, 'is_eco': True},
    {'name': 'Ceramic Tile Floor', 'category': 'floor', 'unit': 'sqm', 'price_per_unit': 2500, 'currency': 'KES', 'country': 'KE', 'city': '', 'carbon_score': 4.8, 'is_eco': False},
    {'name': 'Stabilised Earth Floor', 'category': 'floor', 'unit': 'sqm', 'price_per_unit': 950, 'currency': 'KES', 'country': 'KE', 'city': '', 'carbon_score': 0.6, 'is_eco': True},
    {'name': 'Plaster & Paint Finishing', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 1100, 'currency': 'KES', 'country': 'KE', 'city': '', 'carbon_score': 2.1, 'is_eco': False},

    # ── Ghana (GHS) ──────────────────────────────────────────────────────────
    {'name': 'Laterite Stone Block', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 120, 'currency': 'GHS', 'country': 'GH', 'city': '', 'carbon_score': 1.0, 'is_eco': True},
    {'name': 'Sandcrete Block Wall', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 175, 'currency': 'GHS', 'country': 'GH', 'city': '', 'carbon_score': 5.5, 'is_eco': False},
    {'name': 'Pozzolana Cement Foundation', 'category': 'foundation', 'unit': 'sqm', 'price_per_unit': 480, 'currency': 'GHS', 'country': 'GH', 'city': '', 'carbon_score': 4.5, 'is_eco': True},
    {'name': 'OPC Concrete Foundation', 'category': 'foundation', 'unit': 'sqm', 'price_per_unit': 560, 'currency': 'GHS', 'country': 'GH', 'city': '', 'carbon_score': 7.8, 'is_eco': False},
    {'name': 'Natural Thatch Roofing', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 85, 'currency': 'GHS', 'country': 'GH', 'city': '', 'carbon_score': 0.5, 'is_eco': True},
    {'name': 'Corrugated Iron Sheet', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 130, 'currency': 'GHS', 'country': 'GH', 'city': '', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Stabilised Earth Floor', 'category': 'floor', 'unit': 'sqm', 'price_per_unit': 60, 'currency': 'GHS', 'country': 'GH', 'city': '', 'carbon_score': 0.6, 'is_eco': True},
    {'name': 'Plaster & Paint Finishing', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 90, 'currency': 'GHS', 'country': 'GH', 'city': '', 'carbon_score': 2.1, 'is_eco': False},

    # ── Ethiopia (ETB) ───────────────────────────────────────────────────────
    {'name': 'Compressed Earth Blocks (CEB)', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 750, 'currency': 'ETB', 'country': 'ET', 'city': '', 'carbon_score': 1.2, 'is_eco': True},
    {'name': 'Hollow Concrete Block', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 1100, 'currency': 'ETB', 'country': 'ET', 'city': '', 'carbon_score': 5.8, 'is_eco': False},
    {'name': 'Rubble Stone Trench Foundation', 'category': 'foundation', 'unit': 'sqm', 'price_per_unit': 2200, 'currency': 'ETB', 'country': 'ET', 'city': '', 'carbon_score': 2.0, 'is_eco': True},
    {'name': 'OPC Concrete Foundation', 'category': 'foundation', 'unit': 'sqm', 'price_per_unit': 2800, 'currency': 'ETB', 'country': 'ET', 'city': '', 'carbon_score': 7.8, 'is_eco': False},
    {'name': 'Corrugated Iron Sheet', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 620, 'currency': 'ETB', 'country': 'ET', 'city': '', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Stabilised Earth Floor', 'category': 'floor', 'unit': 'sqm', 'price_per_unit': 340, 'currency': 'ETB', 'country': 'ET', 'city': '', 'carbon_score': 0.6, 'is_eco': True},
    {'name': 'Plaster & Paint Finishing', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 480, 'currency': 'ETB', 'country': 'ET', 'city': '', 'carbon_score': 2.1, 'is_eco': False},

    # ── South Africa (ZAR) ───────────────────────────────────────────────────
    {'name': 'Compressed Earth Blocks (CEB)', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 380, 'currency': 'ZAR', 'country': 'ZA', 'city': '', 'carbon_score': 1.2, 'is_eco': True},
    {'name': 'Face Brick Wall', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 620, 'currency': 'ZAR', 'country': 'ZA', 'city': '', 'carbon_score': 5.2, 'is_eco': False},
    {'name': 'Pozzolana Cement Foundation', 'category': 'foundation', 'unit': 'sqm', 'price_per_unit': 1100, 'currency': 'ZAR', 'country': 'ZA', 'city': '', 'carbon_score': 4.5, 'is_eco': True},
    {'name': 'OPC Concrete Foundation', 'category': 'foundation', 'unit': 'sqm', 'price_per_unit': 1350, 'currency': 'ZAR', 'country': 'ZA', 'city': '', 'carbon_score': 7.8, 'is_eco': False},
    {'name': 'Recycled Metal Sheet (Cool Roof)', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 280, 'currency': 'ZAR', 'country': 'ZA', 'city': '', 'carbon_score': 3.0, 'is_eco': True},
    {'name': 'Concrete Roof Tile', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 420, 'currency': 'ZAR', 'country': 'ZA', 'city': '', 'carbon_score': 5.8, 'is_eco': False},
    {'name': 'Bamboo Flooring', 'category': 'floor', 'unit': 'sqm', 'price_per_unit': 390, 'currency': 'ZAR', 'country': 'ZA', 'city': '', 'carbon_score': 1.1, 'is_eco': True},
    {'name': 'Ceramic Tile Floor', 'category': 'floor', 'unit': 'sqm', 'price_per_unit': 480, 'currency': 'ZAR', 'country': 'ZA', 'city': '', 'carbon_score': 4.8, 'is_eco': False},
    {'name': 'Plaster & Paint Finishing', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 220, 'currency': 'ZAR', 'country': 'ZA', 'city': '', 'carbon_score': 2.1, 'is_eco': False},

    # ── Senegal (XOF) ────────────────────────────────────────────────────────
    {'name': 'Adobe (Sun-dried mud brick)', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 4200, 'currency': 'XOF', 'country': 'SN', 'city': '', 'carbon_score': 0.8, 'is_eco': True},
    {'name': 'Concrete Block Wall', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 6500, 'currency': 'XOF', 'country': 'SN', 'city': '', 'carbon_score': 5.5, 'is_eco': False},
    {'name': 'Pozzolana Cement Foundation', 'category': 'foundation', 'unit': 'sqm', 'price_per_unit': 14000, 'currency': 'XOF', 'country': 'SN', 'city': '', 'carbon_score': 4.5, 'is_eco': True},
    {'name': 'OPC Concrete Foundation', 'category': 'foundation', 'unit': 'sqm', 'price_per_unit': 17000, 'currency': 'XOF', 'country': 'SN', 'city': '', 'carbon_score': 7.8, 'is_eco': False},
    {'name': 'Natural Thatch Roofing', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 3500, 'currency': 'XOF', 'country': 'SN', 'city': '', 'carbon_score': 0.5, 'is_eco': True},
    {'name': 'Corrugated Iron Sheet', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 5800, 'currency': 'XOF', 'country': 'SN', 'city': '', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Stabilised Earth Floor', 'category': 'floor', 'unit': 'sqm', 'price_per_unit': 2200, 'currency': 'XOF', 'country': 'SN', 'city': '', 'carbon_score': 0.6, 'is_eco': True},
    {'name': 'Plaster & Paint Finishing', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 3200, 'currency': 'XOF', 'country': 'SN', 'city': '', 'carbon_score': 2.1, 'is_eco': False},
]

LABOUR_RATES = [
    # Nigeria
    {'skill_type': 'mason', 'country': 'NG', 'city': '', 'rate_per_day': 6500, 'currency': 'NGN'},
    {'skill_type': 'mason', 'country': 'NG', 'city': 'Lagos', 'rate_per_day': 9000, 'currency': 'NGN'},
    {'skill_type': 'carpenter', 'country': 'NG', 'city': '', 'rate_per_day': 7500, 'currency': 'NGN'},
    {'skill_type': 'plumber', 'country': 'NG', 'city': '', 'rate_per_day': 9000, 'currency': 'NGN'},
    {'skill_type': 'electrician', 'country': 'NG', 'city': '', 'rate_per_day': 9500, 'currency': 'NGN'},
    {'skill_type': 'labourer', 'country': 'NG', 'city': '', 'rate_per_day': 3500, 'currency': 'NGN'},
    # Kenya
    {'skill_type': 'mason', 'country': 'KE', 'city': '', 'rate_per_day': 1800, 'currency': 'KES'},
    {'skill_type': 'mason', 'country': 'KE', 'city': 'Nairobi', 'rate_per_day': 2500, 'currency': 'KES'},
    {'skill_type': 'carpenter', 'country': 'KE', 'city': '', 'rate_per_day': 2000, 'currency': 'KES'},
    {'skill_type': 'plumber', 'country': 'KE', 'city': '', 'rate_per_day': 2400, 'currency': 'KES'},
    {'skill_type': 'electrician', 'country': 'KE', 'city': '', 'rate_per_day': 2600, 'currency': 'KES'},
    {'skill_type': 'labourer', 'country': 'KE', 'city': '', 'rate_per_day': 900, 'currency': 'KES'},
    # Ghana
    {'skill_type': 'mason', 'country': 'GH', 'city': '', 'rate_per_day': 150, 'currency': 'GHS'},
    {'skill_type': 'carpenter', 'country': 'GH', 'city': '', 'rate_per_day': 170, 'currency': 'GHS'},
    {'skill_type': 'plumber', 'country': 'GH', 'city': '', 'rate_per_day': 200, 'currency': 'GHS'},
    {'skill_type': 'electrician', 'country': 'GH', 'city': '', 'rate_per_day': 210, 'currency': 'GHS'},
    {'skill_type': 'labourer', 'country': 'GH', 'city': '', 'rate_per_day': 80, 'currency': 'GHS'},
    # Ethiopia
    {'skill_type': 'mason', 'country': 'ET', 'city': '', 'rate_per_day': 700, 'currency': 'ETB'},
    {'skill_type': 'carpenter', 'country': 'ET', 'city': '', 'rate_per_day': 800, 'currency': 'ETB'},
    {'skill_type': 'plumber', 'country': 'ET', 'city': '', 'rate_per_day': 950, 'currency': 'ETB'},
    {'skill_type': 'electrician', 'country': 'ET', 'city': '', 'rate_per_day': 1000, 'currency': 'ETB'},
    {'skill_type': 'labourer', 'country': 'ET', 'city': '', 'rate_per_day': 350, 'currency': 'ETB'},
    # South Africa
    {'skill_type': 'mason', 'country': 'ZA', 'city': '', 'rate_per_day': 550, 'currency': 'ZAR'},
    {'skill_type': 'carpenter', 'country': 'ZA', 'city': '', 'rate_per_day': 650, 'currency': 'ZAR'},
    {'skill_type': 'plumber', 'country': 'ZA', 'city': '', 'rate_per_day': 750, 'currency': 'ZAR'},
    {'skill_type': 'electrician', 'country': 'ZA', 'city': '', 'rate_per_day': 800, 'currency': 'ZAR'},
    {'skill_type': 'labourer', 'country': 'ZA', 'city': '', 'rate_per_day': 280, 'currency': 'ZAR'},
    # Senegal
    {'skill_type': 'mason', 'country': 'SN', 'city': '', 'rate_per_day': 5500, 'currency': 'XOF'},
    {'skill_type': 'carpenter', 'country': 'SN', 'city': '', 'rate_per_day': 6000, 'currency': 'XOF'},
    {'skill_type': 'plumber', 'country': 'SN', 'city': '', 'rate_per_day': 7000, 'currency': 'XOF'},
    {'skill_type': 'electrician', 'country': 'SN', 'city': '', 'rate_per_day': 7500, 'currency': 'XOF'},
    {'skill_type': 'labourer', 'country': 'SN', 'city': '', 'rate_per_day': 3000, 'currency': 'XOF'},
]


class Command(BaseCommand):
    help = 'Seed material prices and labour rates for 6 African countries'

    def handle(self, *args, **kwargs):
        mat_created = 0
        for m in MATERIAL_PRICES:
            _, created = MaterialPrice.objects.update_or_create(
                name=m['name'], country=m['country'], city=m['city'],
                defaults=m,
            )
            if created:
                mat_created += 1

        lab_created = 0
        for l in LABOUR_RATES:
            _, created = LabourRate.objects.update_or_create(
                skill_type=l['skill_type'], country=l['country'], city=l['city'],
                defaults=l,
            )
            if created:
                lab_created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {mat_created} material prices, {lab_created} labour rates.'
        ))
