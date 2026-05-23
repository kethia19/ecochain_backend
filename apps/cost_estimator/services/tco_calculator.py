"""
5-year (or N-year) Total Cost of Ownership projection.
Compares eco build against a conventional equivalent and computes:
  - Electricity savings from passive cooling
  - Water savings from rainwater harvesting
  - Maintenance savings from durable local materials
  - Payback period in months

Coefficients updated May 2026 from Eco_Housing_Expanded.xlsx (Operational_Savings sheet).
Baseline electricity converted from monthly local currency using mid-2026 exchange rates.
"""
from decimal import Decimal
from apps.build_assistant.models import Layout

# Annual electricity saving (% of baseline) by climate zone for passive design.
# Source: Operational_Savings sheet — country-to-zone mapping:
#   tropical_wet / equatorial → Nigeria (32%) + Ghana (30%) avg
#   semi_arid → Kenya (28%), highland → Ethiopia (24%)
#   subtropical_coastal → South Africa (26%), sahel → Senegal (29%)
_PASSIVE_COOLING_SAVING_PCT = {
    'sahel': 0.29,
    'equatorial': 0.31,
    'subtropical_coastal': 0.26,
    'semi_arid': 0.28,
    'highland': 0.24,
    'tropical_wet': 0.32,
}

# Average annual household electricity cost (USD) by country.
# Source: monthly local-currency baselines from Operational_Savings sheet,
# converted at mid-2026 rates (NGN 1600, GHS 15, KES 130, ETB 115, ZAR 18, XOF 600).
_BASELINE_ELECTRICITY_USD = {
    'NG': 713,   # 95,000 NGN/mo × 12 ÷ 1600
    'GH': 576,   # 720 GHS/mo × 12 ÷ 15
    'KE': 1292,  # 14,000 KES/mo × 12 ÷ 130
    'ET': 990,   # 9,500 ETB/mo × 12 ÷ 115
    'ZA': 1733,  # 2,600 ZAR/mo × 12 ÷ 18
    'SN': 1160,  # 58,000 XOF/mo × 12 ÷ 600
}

# Rainwater harvesting annual saving (USD) — assumes 2,000L/year capture vs mains supply.
# TODO: replace with water-cost-derived figures once water tariff data is available.
_RAINWATER_SAVING_USD = {
    'NG': 80, 'KE': 120, 'GH': 70, 'ET': 60, 'ZA': 150, 'SN': 65,
}

# Maintenance premium for conventional vs eco materials (USD/year for a 3BR house)
_MAINTENANCE_SAVING_BASE_USD = 95.0

# Scale maintenance savings with house size
_SQMT_MAINTENANCE_FACTOR = 0.8  # USD per sqm per year


def project_tco(layout_id: str, country: str, upfront_cost: float, projection_years: int = 5) -> dict:
    """
    Returns a dict with keys:
      upfront_cost, annual_savings, total_savings, payback_months, savings_breakdown
    """
    try:
        layout = Layout.objects.get(id=layout_id)
    except Layout.DoesNotExist:
        raise ValueError(f'Layout {layout_id} not found.')

    climate_zone = layout.climate_zone
    area = layout.total_area_sqm or 80.0

    # Electricity savings
    baseline_elec = _BASELINE_ELECTRICITY_USD.get(country, 480)
    passive_pct = _PASSIVE_COOLING_SAVING_PCT.get(climate_zone, 0.25)
    annual_elec_saving = baseline_elec * passive_pct

    # Water savings
    annual_water_saving = _RAINWATER_SAVING_USD.get(country, 80)

    # Maintenance savings
    annual_maint_saving = _MAINTENANCE_SAVING_BASE_USD + (area * _SQMT_MAINTENANCE_FACTOR)

    total_annual = annual_elec_saving + annual_water_saving + annual_maint_saving
    total_savings = total_annual * projection_years

    # Eco premium: eco builds cost ~5–15% more upfront vs conventional
    eco_premium = upfront_cost * 0.10
    payback_months = int((eco_premium / total_annual) * 12) if total_annual > 0 else 9999

    savings_breakdown = [
        {
            'category': 'electricity',
            'annual_saving': round(annual_elec_saving, 2),
            'description': f'Passive cooling cuts electricity use by {passive_pct*100:.0f}% vs conventional',
        },
        {
            'category': 'water',
            'annual_saving': round(annual_water_saving, 2),
            'description': 'Rainwater harvesting reduces mains water cost',
        },
        {
            'category': 'maintenance',
            'annual_saving': round(annual_maint_saving, 2),
            'description': 'Durable local materials lower repair and replacement costs',
        },
    ]

    return {
        'upfront_cost': round(upfront_cost, 2),
        'annual_savings': round(total_annual, 2),
        'total_savings': round(total_savings, 2),
        'payback_months': payback_months,
        'savings_breakdown': savings_breakdown,
        'currency': 'USD',
        'projection_years': projection_years,
    }
