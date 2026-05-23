"""
Layout generation and material suggestion logic.
The generate_layout function is a deterministic stub — the AI Team will replace
it with their fine-tuned model call once the model is ready.
"""
from .models import EcoMaterial

# Room area ranges by type (sqm): (min, max)
_ROOM_AREAS = {
    'bedroom': (10, 14),
    'living_room': (18, 28),
    'kitchen': (8, 12),
    'bathroom': (4, 6),
    'dining_room': (10, 14),
    'study': (8, 10),
    'veranda': (8, 12),
}

# Climate zone defaults: (passive_features, cooling_strategy, base_eco_score)
_ZONE_CONFIG = {
    'sahel':              (['roof overhang', 'thick walls', 'courtyard'],   'cross-ventilation + shade courtyards', 60),
    'equatorial':         (['raised floor', 'louvred windows', 'deep roof'], 'natural ventilation + green canopy',  65),
    'subtropical_coastal':(['sea-breeze orientation', 'roof overhang'],     'sea-breeze + thermal mass',            62),
    'semi_arid':          (['thick walls', 'small windows', 'shade trees'],  'passive evaporative cooling',         58),
    'highland':           (['south-facing glazing', 'thermal mass'],        'solar gain + insulation',              70),
    'tropical_wet':       (['steep roof', 'ventilated ridge', 'wide eaves'], 'rain shedding + airflow',             64),
}

# Window count per room based on orientation bonus
_WINDOW_COUNT = {'south': 2, 'east': 2, 'west': 1, 'north': 1}


def generate_layout(data: dict) -> dict:
    """Return layout JSON, eco_score, and total_area_sqm for given preferences."""
    bedrooms = data['bedrooms']
    climate_zone = data['climate_zone']
    style = data['style']
    orientation = data['orientation']

    zone_cfg = _ZONE_CONFIG.get(climate_zone, _ZONE_CONFIG['equatorial'])
    passive_features, _, base_eco_score = zone_cfg

    rooms = []
    total_area = 0.0

    bedroom_area = 12.0 if style == 'modern' else 10.0
    for i in range(bedrooms):
        rooms.append({
            'type': 'bedroom',
            'label': f'Bedroom {i + 1}',
            'area_sqm': bedroom_area,
            'windows': _WINDOW_COUNT.get(orientation, 2),
            'orientation': orientation,
        })
        total_area += bedroom_area

    living_area = 24.0 if bedrooms >= 3 else 18.0
    rooms.append({
        'type': 'living_room',
        'label': 'Living Room',
        'area_sqm': living_area,
        'windows': 3,
        'orientation': orientation,
    })
    total_area += living_area

    kitchen_area = 10.0
    rooms.append({'type': 'kitchen', 'label': 'Kitchen', 'area_sqm': kitchen_area, 'windows': 1, 'orientation': 'north'})
    total_area += kitchen_area

    bathrooms = max(1, bedrooms // 2)
    for i in range(bathrooms):
        rooms.append({'type': 'bathroom', 'label': f'Bathroom {i + 1}', 'area_sqm': 5.0, 'windows': 1, 'orientation': 'north'})
        total_area += 5.0

    rooms.append({'type': 'veranda', 'label': 'Veranda', 'area_sqm': 10.0, 'windows': 0, 'orientation': orientation})
    total_area += 10.0

    # Eco score modifiers
    eco_score = base_eco_score
    if orientation == 'south':
        eco_score += 5
    if style == 'traditional':
        eco_score += 3
    if bedrooms <= 3:
        eco_score += 2

    layout_json = {
        'rooms': rooms,
        'ventilation_paths': [f'{orientation}-facing cross ventilation'],
        'passive_features': passive_features,
        'style': style,
        'orientation': orientation,
        'climate_zone': climate_zone,
    }

    return {
        'layout_json': layout_json,
        'eco_score': min(eco_score, 100),
        'total_area_sqm': total_area,
    }


def suggest_eco_materials(element_type: str, climate_zone: str) -> list:
    """Return eco material suggestions with a contextual prompt."""
    materials = EcoMaterial.objects.filter(
        element_type=element_type,
        is_eco_alternative=True,
    )

    # Prefer materials suited to this climate zone; fall back to all if none match
    zone_specific = [m for m in materials if climate_zone in (m.suitable_climate_zones or [])]
    pool = zone_specific if zone_specific else list(materials)

    result = []
    for m in pool[:4]:
        prompt = (
            f'Would you like to use {m.name}? '
            f'{m.sustainability_rationale} '
            f'({"saves" if m.cost_delta_pct <= 0 else "adds"} '
            f'{abs(m.cost_delta_pct):.0f}% vs conventional, '
            f'carbon score: {m.carbon_score:.1f})'
        )
        result.append({
            'id': m.id,
            'name': m.name,
            'element_type': m.element_type,
            'description': m.description,
            'sustainability_rationale': m.sustainability_rationale,
            'carbon_score': m.carbon_score,
            'cost_delta_pct': m.cost_delta_pct,
            'prompt': prompt,
        })

    return result
