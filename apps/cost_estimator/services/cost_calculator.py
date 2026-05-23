"""
Cost calculation service.
Resolves material and labour prices from the DB, then applies them
to the layout's room areas to produce an itemised cost breakdown.
Falls back to national average when city-level data is unavailable.
"""
from decimal import Decimal
from apps.build_assistant.models import Layout
from apps.cost_estimator.models import MaterialPrice, LabourRate

# Approximate labour-day multipliers per room type
_LABOUR_DAYS = {
    'bedroom': {'mason': 8, 'carpenter': 4, 'plumber': 1},
    'living_room': {'mason': 10, 'carpenter': 5, 'plumber': 1},
    'kitchen': {'mason': 6, 'carpenter': 3, 'plumber': 3},
    'bathroom': {'mason': 5, 'carpenter': 2, 'plumber': 4},
    'dining_room': {'mason': 6, 'carpenter': 3, 'plumber': 0},
    'study': {'mason': 4, 'carpenter': 2, 'plumber': 0},
    'veranda': {'mason': 4, 'carpenter': 3, 'plumber': 0},
}

_DEFAULT_LABOUR = {'mason': 6, 'carpenter': 3, 'plumber': 1}

# sqm of material per sqm of room floor area by category
_MATERIAL_RATIOS = {
    'wall': 2.0,        # walls are ~2× floor area
    'foundation': 0.3,  # foundation area ≈ 30% of floor
    'roof': 1.1,        # roof slightly larger than floor
    'floor': 1.0,
    'finishing': 1.5,
}


def _get_price(name_fragment: str, category: str, country: str, city: str):
    """Return the best matching MaterialPrice or None."""
    qs = MaterialPrice.objects.filter(category=category, country=country)
    if city:
        city_qs = qs.filter(city__iexact=city)
        if city_qs.exists():
            return city_qs.first()
    return qs.first()


def _get_labour(skill: str, country: str, city: str):
    """Return matching LabourRate or None."""
    qs = LabourRate.objects.filter(skill_type=skill, country=country)
    if city:
        city_qs = qs.filter(city__iexact=city)
        if city_qs.exists():
            return city_qs.first()
    return qs.first()


def calculate_cost(layout_id: str, country: str, city: str, labour_zone: str) -> dict:
    """
    Returns {'total_cost', 'currency', 'breakdown', 'disclaimer'}.
    Raises ValueError if the layout does not exist.
    """
    try:
        layout = Layout.objects.get(id=layout_id)
    except Layout.DoesNotExist:
        raise ValueError(f'Layout {layout_id} not found.')

    rooms = layout.layout_json.get('rooms', [])
    total_area = layout.total_area_sqm or sum(r.get('area_sqm', 0) for r in rooms)

    breakdown = []
    total = Decimal('0')
    disclaimer = None

    # Determine primary currency (from first material price found)
    currency = 'USD'
    for cat in ['wall', 'foundation', 'roof', 'floor']:
        mp = _get_price('', cat, country, city)
        if mp:
            currency = mp.currency
            break

    # Material costs by category
    for cat, ratio in _MATERIAL_RATIOS.items():
        mp = _get_price('', cat, country, city)
        if not mp:
            if city:
                disclaimer = f'City-level rates unavailable for {city}; using national average.'
                mp = _get_price('', cat, country, '')
            if not mp:
                continue

        quantity = total_area * ratio
        line_total = Decimal(str(quantity)) * mp.price_per_unit
        total += line_total
        breakdown.append({
            'category': cat,
            'description': mp.name,
            'unit_cost': float(mp.price_per_unit),
            'quantity': round(quantity, 2),
            'total': float(line_total.quantize(Decimal('0.01'))),
            'currency': mp.currency,
        })

    # Labour costs
    total_labour_days = {'mason': 0, 'carpenter': 0, 'plumber': 0}
    for room in rooms:
        room_type = room.get('type', 'bedroom')
        days = _LABOUR_DAYS.get(room_type, _DEFAULT_LABOUR)
        for skill, d in days.items():
            total_labour_days[skill] = total_labour_days.get(skill, 0) + d

    for skill, days in total_labour_days.items():
        if days == 0:
            continue
        lr = _get_labour(skill, labour_zone, city)
        if not lr:
            lr = _get_labour(skill, labour_zone, '')
        if not lr:
            continue
        line_total = Decimal(str(days)) * lr.rate_per_day
        total += line_total
        breakdown.append({
            'category': 'labour',
            'description': f'{skill.capitalize()} ({days} days)',
            'unit_cost': float(lr.rate_per_day),
            'quantity': float(days),
            'total': float(line_total.quantize(Decimal('0.01'))),
            'currency': lr.currency,
        })

    return {
        'total_cost': float(total.quantize(Decimal('0.01'))),
        'currency': currency,
        'breakdown': breakdown,
        'disclaimer': disclaimer,
    }
