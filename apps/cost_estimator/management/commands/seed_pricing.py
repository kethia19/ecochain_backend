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

# Labour rates updated May 2026 from Eco_Housing_Expanded.xlsx (Labour_Rates sheet).
# Nigeria rates revised upward to reflect NGN devaluation since original seed.
# Mid-band daily rates used as national averages throughout.
LABOUR_RATES = [
    # Nigeria — updated May 2026
    {'skill_type': 'mason', 'country': 'NG', 'city': '', 'rate_per_day': 18000, 'currency': 'NGN'},
    {'skill_type': 'mason', 'country': 'NG', 'city': 'Lagos', 'rate_per_day': 22000, 'currency': 'NGN'},
    {'skill_type': 'carpenter', 'country': 'NG', 'city': '', 'rate_per_day': 20000, 'currency': 'NGN'},
    {'skill_type': 'plumber', 'country': 'NG', 'city': '', 'rate_per_day': 22000, 'currency': 'NGN'},
    {'skill_type': 'electrician', 'country': 'NG', 'city': '', 'rate_per_day': 27900, 'currency': 'NGN'},
    {'skill_type': 'labourer', 'country': 'NG', 'city': '', 'rate_per_day': 3500, 'currency': 'NGN'},
    # Kenya — carpenter updated May 2026
    {'skill_type': 'mason', 'country': 'KE', 'city': '', 'rate_per_day': 1800, 'currency': 'KES'},
    {'skill_type': 'mason', 'country': 'KE', 'city': 'Nairobi', 'rate_per_day': 2500, 'currency': 'KES'},
    {'skill_type': 'carpenter', 'country': 'KE', 'city': '', 'rate_per_day': 3500, 'currency': 'KES'},
    {'skill_type': 'plumber', 'country': 'KE', 'city': '', 'rate_per_day': 2400, 'currency': 'KES'},
    {'skill_type': 'electrician', 'country': 'KE', 'city': '', 'rate_per_day': 2600, 'currency': 'KES'},
    {'skill_type': 'labourer', 'country': 'KE', 'city': '', 'rate_per_day': 900, 'currency': 'KES'},
    # Ghana
    {'skill_type': 'mason', 'country': 'GH', 'city': '', 'rate_per_day': 150, 'currency': 'GHS'},
    {'skill_type': 'carpenter', 'country': 'GH', 'city': '', 'rate_per_day': 170, 'currency': 'GHS'},
    {'skill_type': 'plumber', 'country': 'GH', 'city': '', 'rate_per_day': 200, 'currency': 'GHS'},
    {'skill_type': 'electrician', 'country': 'GH', 'city': '', 'rate_per_day': 210, 'currency': 'GHS'},
    {'skill_type': 'labourer', 'country': 'GH', 'city': '', 'rate_per_day': 80, 'currency': 'GHS'},
    # Ethiopia — plumber updated May 2026
    {'skill_type': 'mason', 'country': 'ET', 'city': '', 'rate_per_day': 700, 'currency': 'ETB'},
    {'skill_type': 'carpenter', 'country': 'ET', 'city': '', 'rate_per_day': 800, 'currency': 'ETB'},
    {'skill_type': 'plumber', 'country': 'ET', 'city': '', 'rate_per_day': 1200, 'currency': 'ETB'},
    {'skill_type': 'electrician', 'country': 'ET', 'city': '', 'rate_per_day': 1000, 'currency': 'ETB'},
    {'skill_type': 'labourer', 'country': 'ET', 'city': '', 'rate_per_day': 350, 'currency': 'ETB'},
    # South Africa
    {'skill_type': 'mason', 'country': 'ZA', 'city': '', 'rate_per_day': 550, 'currency': 'ZAR'},
    {'skill_type': 'carpenter', 'country': 'ZA', 'city': '', 'rate_per_day': 650, 'currency': 'ZAR'},
    {'skill_type': 'plumber', 'country': 'ZA', 'city': '', 'rate_per_day': 750, 'currency': 'ZAR'},
    {'skill_type': 'electrician', 'country': 'ZA', 'city': '', 'rate_per_day': 800, 'currency': 'ZAR'},
    {'skill_type': 'labourer', 'country': 'ZA', 'city': '', 'rate_per_day': 280, 'currency': 'ZAR'},
    # Senegal — carpenter updated May 2026
    {'skill_type': 'mason', 'country': 'SN', 'city': '', 'rate_per_day': 5500, 'currency': 'XOF'},
    {'skill_type': 'carpenter', 'country': 'SN', 'city': '', 'rate_per_day': 18000, 'currency': 'XOF'},
    {'skill_type': 'plumber', 'country': 'SN', 'city': '', 'rate_per_day': 7000, 'currency': 'XOF'},
    {'skill_type': 'electrician', 'country': 'SN', 'city': '', 'rate_per_day': 7500, 'currency': 'XOF'},
    {'skill_type': 'labourer', 'country': 'SN', 'city': '', 'rate_per_day': 3000, 'currency': 'XOF'},
]

# ── New city-level material prices from Eco_Housing_Expanded.xlsx (May 2026) ──
# Conversion factors applied:
#   Bamboo Panels: sourced per sqm — no conversion needed (finishing category)
#   Laterite Blocks: 100 pcs ÷ 8 = price per sqm (standard 450×225mm block, single wythe)
#   Roofing Sheets: 1 bundle ÷ 9 = price per sqm (9 sheets × 1 sqm/sheet average)
# Negative prices from the source data (ZA data errors) are excluded.
MATERIAL_PRICES_V2 = [
    # ── Bamboo Panels (finishing) ────────────────────────────────────────────
    {'name': 'Bamboo Panels', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 17659, 'currency': 'NGN', 'country': 'NG', 'city': 'Lagos', 'carbon_score': 1.1, 'is_eco': True},
    {'name': 'Bamboo Panels', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 17953, 'currency': 'NGN', 'country': 'NG', 'city': 'Abuja', 'carbon_score': 1.1, 'is_eco': True},
    {'name': 'Bamboo Panels', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 18224, 'currency': 'NGN', 'country': 'NG', 'city': 'Port Harcourt', 'carbon_score': 1.1, 'is_eco': True},
    {'name': 'Bamboo Panels', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 692,   'currency': 'GHS', 'country': 'GH', 'city': 'Accra', 'carbon_score': 1.1, 'is_eco': True},
    {'name': 'Bamboo Panels', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 22,    'currency': 'GHS', 'country': 'GH', 'city': 'Kumasi', 'carbon_score': 1.1, 'is_eco': True},
    {'name': 'Bamboo Panels', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 2172,  'currency': 'KES', 'country': 'KE', 'city': 'Nairobi', 'carbon_score': 1.1, 'is_eco': True},
    {'name': 'Bamboo Panels', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 2555,  'currency': 'KES', 'country': 'KE', 'city': 'Mombasa', 'carbon_score': 1.1, 'is_eco': True},
    {'name': 'Bamboo Panels', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 2322,  'currency': 'ETB', 'country': 'ET', 'city': 'Addis Ababa', 'carbon_score': 1.1, 'is_eco': True},
    {'name': 'Bamboo Panels', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 2894,  'currency': 'ETB', 'country': 'ET', 'city': 'Dire Dawa', 'carbon_score': 1.1, 'is_eco': True},
    {'name': 'Bamboo Panels', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 361,   'currency': 'ZAR', 'country': 'ZA', 'city': 'Johannesburg', 'carbon_score': 1.1, 'is_eco': True},
    {'name': 'Bamboo Panels', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 17661, 'currency': 'XOF', 'country': 'SN', 'city': 'Dakar', 'carbon_score': 1.1, 'is_eco': True},
    {'name': 'Bamboo Panels', 'category': 'finishing', 'unit': 'sqm', 'price_per_unit': 17689, 'currency': 'XOF', 'country': 'SN', 'city': 'Thiès', 'carbon_score': 1.1, 'is_eco': True},

    # ── Laterite Blocks (wall) — 100 pcs ÷ 8 = sqm ─────────────────────────
    {'name': 'Laterite Blocks', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 5578, 'currency': 'NGN', 'country': 'NG', 'city': 'Lagos', 'carbon_score': 1.0, 'is_eco': True},
    {'name': 'Laterite Blocks', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 5600, 'currency': 'NGN', 'country': 'NG', 'city': 'Abuja', 'carbon_score': 1.0, 'is_eco': True},
    {'name': 'Laterite Blocks', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 5595, 'currency': 'NGN', 'country': 'NG', 'city': 'Port Harcourt', 'carbon_score': 1.0, 'is_eco': True},
    {'name': 'Laterite Blocks', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 91,   'currency': 'GHS', 'country': 'GH', 'city': 'Accra', 'carbon_score': 1.0, 'is_eco': True},
    {'name': 'Laterite Blocks', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 33,   'currency': 'GHS', 'country': 'GH', 'city': 'Kumasi', 'carbon_score': 1.0, 'is_eco': True},
    {'name': 'Laterite Blocks', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 641,  'currency': 'KES', 'country': 'KE', 'city': 'Nairobi', 'carbon_score': 1.0, 'is_eco': True},
    {'name': 'Laterite Blocks', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 647,  'currency': 'KES', 'country': 'KE', 'city': 'Mombasa', 'carbon_score': 1.0, 'is_eco': True},
    {'name': 'Laterite Blocks', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 737,  'currency': 'ETB', 'country': 'ET', 'city': 'Addis Ababa', 'carbon_score': 1.0, 'is_eco': True},
    {'name': 'Laterite Blocks', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 758,  'currency': 'ETB', 'country': 'ET', 'city': 'Dire Dawa', 'carbon_score': 1.0, 'is_eco': True},
    {'name': 'Laterite Blocks', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 112,  'currency': 'ZAR', 'country': 'ZA', 'city': 'Johannesburg', 'carbon_score': 1.0, 'is_eco': True},
    {'name': 'Laterite Blocks', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 112,  'currency': 'ZAR', 'country': 'ZA', 'city': 'Cape Town', 'carbon_score': 1.0, 'is_eco': True},
    {'name': 'Laterite Blocks', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 6279, 'currency': 'XOF', 'country': 'SN', 'city': 'Dakar', 'carbon_score': 1.0, 'is_eco': True},
    {'name': 'Laterite Blocks', 'category': 'wall', 'unit': 'sqm', 'price_per_unit': 6242, 'currency': 'XOF', 'country': 'SN', 'city': 'Thiès', 'carbon_score': 1.0, 'is_eco': True},

    # ── Roofing Sheets (roof) — bundle ÷ 9 = sqm ────────────────────────────
    {'name': 'Corrugated Roofing Sheets', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 20015, 'currency': 'NGN', 'country': 'NG', 'city': 'Lagos', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Corrugated Roofing Sheets', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 20032, 'currency': 'NGN', 'country': 'NG', 'city': 'Abuja', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Corrugated Roofing Sheets', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 19963, 'currency': 'NGN', 'country': 'NG', 'city': 'Port Harcourt', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Corrugated Roofing Sheets', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 277,   'currency': 'GHS', 'country': 'GH', 'city': 'Accra', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Corrugated Roofing Sheets', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 238,   'currency': 'GHS', 'country': 'GH', 'city': 'Kumasi', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Corrugated Roofing Sheets', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 2047,  'currency': 'KES', 'country': 'KE', 'city': 'Nairobi', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Corrugated Roofing Sheets', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 1955,  'currency': 'KES', 'country': 'KE', 'city': 'Mombasa', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Corrugated Roofing Sheets', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 2310,  'currency': 'ETB', 'country': 'ET', 'city': 'Addis Ababa', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Corrugated Roofing Sheets', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 2299,  'currency': 'ETB', 'country': 'ET', 'city': 'Dire Dawa', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Corrugated Roofing Sheets', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 362,   'currency': 'ZAR', 'country': 'ZA', 'city': 'Johannesburg', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Corrugated Roofing Sheets', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 318,   'currency': 'ZAR', 'country': 'ZA', 'city': 'Cape Town', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Corrugated Roofing Sheets', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 18301, 'currency': 'XOF', 'country': 'SN', 'city': 'Dakar', 'carbon_score': 6.2, 'is_eco': False},
    {'name': 'Corrugated Roofing Sheets', 'category': 'roof', 'unit': 'sqm', 'price_per_unit': 18346, 'currency': 'XOF', 'country': 'SN', 'city': 'Thiès', 'carbon_score': 6.2, 'is_eco': False},
]


class Command(BaseCommand):
    help = 'Seed material prices and labour rates for 6 African countries'

    def handle(self, *args, **kwargs):
        mat_created = 0
        for m in MATERIAL_PRICES + MATERIAL_PRICES_V2:
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
