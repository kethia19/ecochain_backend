"""Seed African climate zone presets and eco materials catalogue."""
from django.core.management.base import BaseCommand
from apps.build_assistant.models import ClimateZone, EcoMaterial


CLIMATE_ZONES = [
    {
        'code': 'sahel',
        'name': 'Sahel',
        'description': 'Hot, dry semi-arid zone spanning the southern edge of the Sahara. Long dry seasons, high solar radiation.',
        'typical_countries': ['Niger', 'Mali', 'Burkina Faso', 'Chad', 'Senegal', 'Nigeria (north)'],
        'cooling_strategy': 'Cross-ventilation, shade courtyards, thick thermal-mass walls',
        'passive_features': ['roof overhang', 'thick walls', 'internal courtyard', 'night-flush ventilation'],
    },
    {
        'code': 'equatorial',
        'name': 'Equatorial',
        'description': 'Hot, humid zone near the equator. High rainfall year-round, dense vegetation.',
        'typical_countries': ['DR Congo', 'Cameroon', 'Gabon', 'Uganda', 'Kenya (coast)'],
        'cooling_strategy': 'Natural cross-ventilation, green canopy, raised floors',
        'passive_features': ['raised floor', 'louvred windows', 'deep roof eaves', 'green canopy'],
    },
    {
        'code': 'subtropical_coastal',
        'name': 'Subtropical Coastal',
        'description': 'Warm, humid coastal zones with sea breezes and moderate seasonal variation.',
        'typical_countries': ['South Africa (east coast)', 'Mozambique', 'Tanzania', 'Ghana (coast)'],
        'cooling_strategy': 'Sea-breeze orientation, thermal mass, shaded verandas',
        'passive_features': ['sea-breeze orientation', 'roof overhang', 'shaded veranda', 'thermal mass'],
    },
    {
        'code': 'semi_arid',
        'name': 'Semi-Arid',
        'description': 'Dry zone with hot days, cool nights. Seasonal rainfall, sparse vegetation.',
        'typical_countries': ['Ethiopia (low)', 'Kenya (north)', 'Somalia', 'Zimbabwe (west)'],
        'cooling_strategy': 'Passive evaporative cooling, small high windows, shade trees',
        'passive_features': ['thick walls', 'small high windows', 'shade trees', 'evaporative cooling'],
    },
    {
        'code': 'highland',
        'name': 'Highland',
        'description': 'Cooler high-altitude zone. Strong solar radiation, cold nights. Optimal for passive solar design.',
        'typical_countries': ['Ethiopia (highland)', 'Kenya (central)', 'Rwanda', 'Uganda (west)'],
        'cooling_strategy': 'Passive solar gain, insulated walls, south-facing glazing',
        'passive_features': ['south-facing glazing', 'thermal mass', 'roof insulation', 'solar water heating'],
    },
    {
        'code': 'tropical_wet',
        'name': 'Tropical Wet',
        'description': 'Hot, very wet climate with heavy monsoon rains. High humidity, dense forest.',
        'typical_countries': ['Sierra Leone', 'Liberia', 'Guinea', 'Nigeria (south)'],
        'cooling_strategy': 'Rain shedding, ridge ventilation, wide eaves, elevated structure',
        'passive_features': ['steep roof', 'ventilated ridge', 'wide eaves', 'elevated structure'],
    },
]

ECO_MATERIALS = [
    # Walls
    {
        'name': 'Compressed Earth Blocks (CEB)',
        'element_type': 'wall',
        'description': 'Soil compressed under high pressure into dense, load-bearing blocks. No firing needed.',
        'sustainability_rationale': 'Uses local soil, zero cement, low embodied energy. Natural thermal mass.',
        'carbon_score': 1.2,
        'cost_delta_pct': -15.0,
        'suitable_climate_zones': ['sahel', 'semi_arid', 'highland', 'equatorial'],
    },
    {
        'name': 'Recycled Plastic Bricks',
        'element_type': 'wall',
        'description': 'Bricks manufactured from shredded post-consumer plastic waste.',
        'sustainability_rationale': 'Diverts plastic from landfill; durable, moisture-resistant, locally sourced in urban areas.',
        'carbon_score': 2.5,
        'cost_delta_pct': -10.0,
        'suitable_climate_zones': ['equatorial', 'tropical_wet', 'subtropical_coastal'],
    },
    {
        'name': 'Adobe (Sun-dried mud brick)',
        'element_type': 'wall',
        'description': 'Traditional mud brick dried in the sun. Mixed with straw for tensile strength.',
        'sustainability_rationale': 'Zero energy production, fully biodegradable, excellent thermal regulation.',
        'carbon_score': 0.8,
        'cost_delta_pct': -25.0,
        'suitable_climate_zones': ['sahel', 'semi_arid'],
    },
    {
        'name': 'Laterite Stone Block',
        'element_type': 'wall',
        'description': 'Cut from naturally occurring iron-rich laterite rock, abundant across sub-Saharan Africa.',
        'sustainability_rationale': 'Quarried locally, no processing, high thermal mass reduces cooling load.',
        'carbon_score': 1.0,
        'cost_delta_pct': -20.0,
        'suitable_climate_zones': ['equatorial', 'tropical_wet', 'subtropical_coastal', 'sahel'],
    },
    # Roofing
    {
        'name': 'Natural Thatch Roofing',
        'element_type': 'roof',
        'description': 'Dried grass or palm fronds layered to create a waterproof, insulating roof.',
        'sustainability_rationale': 'Fully renewable, excellent natural insulation, low embodied carbon.',
        'carbon_score': 0.5,
        'cost_delta_pct': -30.0,
        'suitable_climate_zones': ['equatorial', 'tropical_wet', 'sahel'],
    },
    {
        'name': 'Recycled Metal Sheet (Cool Roof)',
        'element_type': 'roof',
        'description': 'Reclaimed corrugated iron painted with solar-reflective coating.',
        'sustainability_rationale': 'Extends lifecycle of existing metal; cool-roof coating cuts solar heat gain by 30%.',
        'carbon_score': 3.0,
        'cost_delta_pct': -5.0,
        'suitable_climate_zones': ['sahel', 'semi_arid', 'highland', 'subtropical_coastal'],
    },
    {
        'name': 'Bamboo Structural Roof Frame',
        'element_type': 'roof',
        'description': 'Bamboo poles used as roof structure instead of sawn timber.',
        'sustainability_rationale': 'Fastest-growing renewable material; stronger than steel by weight.',
        'carbon_score': 0.9,
        'cost_delta_pct': -20.0,
        'suitable_climate_zones': ['equatorial', 'tropical_wet', 'subtropical_coastal'],
    },
    # Foundation
    {
        'name': 'Pozzolana (Volcanic Ash) Cement Foundation',
        'element_type': 'foundation',
        'description': 'Concrete mix using pozzolana volcanic ash as a partial cement replacement.',
        'sustainability_rationale': 'Reduces OPC cement by up to 40%, cuts embodied carbon significantly.',
        'carbon_score': 4.5,
        'cost_delta_pct': -12.0,
        'suitable_climate_zones': ['highland', 'equatorial', 'subtropical_coastal', 'tropical_wet', 'sahel', 'semi_arid'],
    },
    {
        'name': 'Rubble Stone Trench Foundation',
        'element_type': 'foundation',
        'description': 'Locally quarried rubble stone set in a lime-stabilised trench.',
        'sustainability_rationale': 'Eliminates formwork, uses on-site stone, lime is lower carbon than OPC.',
        'carbon_score': 2.0,
        'cost_delta_pct': -18.0,
        'suitable_climate_zones': ['highland', 'semi_arid', 'sahel'],
    },
    # Floor
    {
        'name': 'Stabilised Earth Floor',
        'element_type': 'floor',
        'description': 'Compacted earth mixed with 5% lime for hardness and sealed with linseed oil.',
        'sustainability_rationale': 'Near-zero embodied carbon, provides natural thermal mass underfoot.',
        'carbon_score': 0.6,
        'cost_delta_pct': -35.0,
        'suitable_climate_zones': ['sahel', 'semi_arid', 'highland', 'equatorial'],
    },
    {
        'name': 'Bamboo Flooring',
        'element_type': 'floor',
        'description': 'Engineered bamboo planks as a durable, renewable hardwood alternative.',
        'sustainability_rationale': 'Harvested in 3–5 years vs 25+ for hardwood; harder than oak.',
        'carbon_score': 1.1,
        'cost_delta_pct': -8.0,
        'suitable_climate_zones': ['equatorial', 'tropical_wet', 'subtropical_coastal'],
    },
    # Structural walls — new materials from Eco_Materials_Catalogue (May 2026)
    {
        'name': 'Rammed Earth',
        'element_type': 'wall',
        'description': 'Compacted layers of moist subsoil, gravel, and a small amount of stabiliser, formed between temporary shuttering.',
        'sustainability_rationale': 'Uses on-site or locally sourced subsoil; near-zero embodied energy; excellent thermal mass reduces cooling loads by up to 30%.',
        'carbon_score': 0.9,
        'cost_delta_pct': -20.0,
        'suitable_climate_zones': ['sahel', 'semi_arid', 'highland', 'equatorial', 'subtropical_coastal', 'tropical_wet'],
    },
    # Roofing — new materials from Eco_Materials_Catalogue (May 2026)
    {
        'name': 'Solar Roof Tiles',
        'element_type': 'roof',
        'description': 'Photovoltaic tiles that replace conventional roofing while generating on-site electricity.',
        'sustainability_rationale': 'Eliminates separate PV installation; offsets grid electricity over lifetime; reduces dependence on diesel generators common in off-grid areas.',
        'carbon_score': 5.0,
        'cost_delta_pct': 40.0,
        'suitable_climate_zones': ['sahel', 'semi_arid', 'highland', 'subtropical_coastal', 'equatorial'],
    },
    # Foundation — new materials from Eco_Materials_Catalogue (May 2026)
    {
        'name': 'Green Cement LC3',
        'element_type': 'foundation',
        'description': 'Limestone Calcined Clay Cement (LC3) — blends calcined clay and limestone to replace up to 50% of clinker.',
        'sustainability_rationale': 'Cuts CO2 emissions by ~40% vs OPC; raw materials (clay, limestone) are abundant across Africa; same strength class as OPC 42.5.',
        'carbon_score': 3.5,
        'cost_delta_pct': -8.0,
        'suitable_climate_zones': ['sahel', 'semi_arid', 'highland', 'equatorial', 'subtropical_coastal', 'tropical_wet'],
    },
    # Insulation
    {
        'name': 'Coconut Fibre Insulation',
        'element_type': 'insulation',
        'description': 'Insulation boards made from compressed coconut coir waste.',
        'sustainability_rationale': 'Agricultural by-product, biodegradable, mould-resistant in humid climates.',
        'carbon_score': 0.7,
        'cost_delta_pct': -5.0,
        'suitable_climate_zones': ['equatorial', 'tropical_wet', 'subtropical_coastal'],
    },
    {
        'name': 'Sheep Wool Insulation',
        'element_type': 'insulation',
        'description': 'Washed and treated wool batts for wall and roof insulation.',
        'sustainability_rationale': 'Renewable, sequesters carbon, biodegradable, naturally moisture-buffering.',
        'carbon_score': 0.4,
        'cost_delta_pct': 5.0,
        'suitable_climate_zones': ['highland', 'subtropical_coastal'],
    },
]


class Command(BaseCommand):
    help = 'Seed African climate zones and eco materials catalogue'

    def handle(self, *args, **kwargs):
        zones_created = 0
        for z in CLIMATE_ZONES:
            _, created = ClimateZone.objects.update_or_create(
                code=z['code'], defaults=z,
            )
            if created:
                zones_created += 1

        mats_created = 0
        for m in ECO_MATERIALS:
            _, created = EcoMaterial.objects.update_or_create(
                name=m['name'], element_type=m['element_type'], defaults=m,
            )
            if created:
                mats_created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {zones_created} climate zones, {mats_created} eco materials.'
        ))
