"""
Green Match services — encapsulates the side-effectful and algorithmic work.

Two concerns live here:

1. `enrich_location()` — turn a free-text location string into lat/lng + a
   climate zone. Uses Google Maps if a key is configured, otherwise falls
   back to the free Nominatim provider so the project also runs in dev
   without paid credentials.

2. `score_plants()` — pure function that ranks plants against the user's
   inputs. Weights are described in the architecture doc:
       Climate zone   30%
       Sun exposure   25%
       Soil           25%
       Water          20%
"""
from django.conf import settings

from geopy.geocoders import GoogleV3, Nominatim
from geopy.exc import GeopyError


# ---------------------------------------------------------------------------
# Climate zone resolution
# ---------------------------------------------------------------------------
# Each entry: (lat_min, lat_max, lng_min, lng_max) → climate zone name.
# These are coarse Africa-focused bounding boxes, not science-grade. For
# production you'd swap in a real Köppen lookup or a service like Open-Meteo.
CLIMATE_ZONES = [
    # name,                lat_min, lat_max, lng_min, lng_max
    ('mediterranean',          30,      45,    -10,     40),
    ('arid_semi_arid',         10,      30,    -20,     60),
    ('tropical_highland',      -5,      10,     30,     45),
    ('tropical_savanna',      -10,      15,    -20,     50),
    ('tropical_rainforest',   -10,      10,      5,     35),
    ('temperate',             -40,     -20,     10,     35),
]


def resolve_climate_zone(lat: float, lng: float) -> str:
    for name, lat_min, lat_max, lng_min, lng_max in CLIMATE_ZONES:
        if lat_min <= lat <= lat_max and lng_min <= lng <= lng_max:
            return name
    return 'unknown'


# ---------------------------------------------------------------------------
# Geocoding
# ---------------------------------------------------------------------------
def _geocoder():
    if settings.GOOGLE_MAPS_KEY:
        return GoogleV3(api_key=settings.GOOGLE_MAPS_KEY, timeout=10)
    # Free fallback for development.
    return Nominatim(user_agent='eco-chain-dev', timeout=10)


def enrich_location(location_string: str) -> dict:
    """Resolve a free-text location to coords + climate zone.

    Never raises — on failure returns an `unknown` zone with `None` coords
    so the scoring algorithm can still run (just without the climate boost).
    """
    try:
        location = _geocoder().geocode(location_string)
    except GeopyError:
        location = None

    if location is None:
        return {'lat': None, 'lng': None, 'climate_zone': 'unknown'}

    lat, lng = location.latitude, location.longitude
    return {
        'lat': lat,
        'lng': lng,
        'climate_zone': resolve_climate_zone(lat, lng),
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
WATER_RANK = {'moderate': 1, 'low': 2, 'ultra_low': 3}


def score_plants(plants, *, climate_zone, sun_exposure, soil_condition,
                 water_conservation) -> list:
    """Return a list of {'plant', 'score'} dicts, sorted by score desc.

    Score is a 0–100 integer. Each factor either contributes its full
    weight or nothing — the architecture doc keeps it deliberately simple.
    """
    user_water_lvl = WATER_RANK[water_conservation]
    results = []

    for plant in plants:
        score = 0.0

        if climate_zone in (plant.climate_zones or []):
            score += 0.30
        if sun_exposure in (plant.sun_exposure or []):
            score += 0.25
        if soil_condition in (plant.soil_types or []):
            score += 0.25

        plant_water_lvl = WATER_RANK.get(plant.water_conservation, 1)
        if plant_water_lvl <= user_water_lvl:
            score += 0.20

        results.append({'plant': plant, 'score': round(score * 100)})

    results.sort(key=lambda x: x['score'], reverse=True)
    return results
