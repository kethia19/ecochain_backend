"""
Management command: python manage.py seed_plants

Populates the Plant catalogue with a starter set of native African flora
so Green Match returns meaningful results out of the box.
"""
from django.core.management.base import BaseCommand
from apps.plants.models import Plant


SAMPLE_PLANTS = [
    {
        'name': 'Baobab',
        'scientific_name': 'Adansonia digitata',
        'climate_zones': ['tropical_savanna', 'arid_semi_arid'],
        'sun_exposure': ['full_sun'],
        'soil_types': ['sandy', 'loamy', 'lateritic_red_clay'],
        'water_conservation': 'ultra_low',
        'water_frequency': 'Drought-tolerant once established',
        'tags': ['iconic', 'drought-tolerant', 'long-lived'],
        'care_tips': [
            'Plant in well-drained soil',
            'Water sparingly in the first year, then leave alone',
            'Prune dead branches at the start of the rainy season',
        ],
        'impact_label': 'Carbon-storing giant',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Baobab_and_elephants.jpg/640px-Baobab_and_elephants.jpg',
    },
    {
        'name': 'Aloe Vera',
        'scientific_name': 'Aloe barbadensis miller',
        'climate_zones': ['arid_semi_arid', 'mediterranean', 'tropical_savanna'],
        'sun_exposure': ['full_sun', 'partial'],
        'soil_types': ['sandy', 'loamy'],
        'water_conservation': 'ultra_low',
        'water_frequency': 'Every 2-3 weeks',
        'tags': ['medicinal', 'drought-tolerant', 'low-maintenance'],
        'care_tips': [
            'Use a sandy, fast-draining soil mix',
            'Let soil dry completely between waterings',
            'Bring indoors if temperatures drop below 10°C',
        ],
        'impact_label': 'Water-wise medicinal',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Aloe_vera_flower.jpg/640px-Aloe_vera_flower.jpg',
    },
    {
        'name': 'Moringa',
        'scientific_name': 'Moringa oleifera',
        'climate_zones': ['tropical_savanna', 'arid_semi_arid', 'tropical_rainforest'],
        'sun_exposure': ['full_sun'],
        'soil_types': ['sandy', 'loamy', 'lateritic_red_clay'],
        'water_conservation': 'low',
        'water_frequency': 'Weekly when young; biweekly when established',
        'tags': ['nutritious', 'fast-growing', 'medicinal'],
        'care_tips': [
            'Plant from seed directly in the ground',
            'Pinch top to encourage bushy growth',
            'Harvest leaves regularly for nutrition',
        ],
        'impact_label': 'Nutrition powerhouse',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Starr_080117-1612_Moringa_oleifera.jpg/640px-Starr_080117-1612_Moringa_oleifera.jpg',
    },
    {
        'name': 'Acacia',
        'scientific_name': 'Vachellia tortilis',
        'climate_zones': ['tropical_savanna', 'arid_semi_arid'],
        'sun_exposure': ['full_sun'],
        'soil_types': ['sandy', 'lateritic_red_clay'],
        'water_conservation': 'ultra_low',
        'water_frequency': 'Rainfall is enough once established',
        'tags': ['nitrogen-fixing', 'wildlife-friendly', 'iconic'],
        'care_tips': [
            'Provide deep watering for the first 6 months',
            'Plant away from foundations — taproots run deep',
            'No fertiliser needed; fixes its own nitrogen',
        ],
        'impact_label': 'Soil enricher',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Vachellia_tortilis_-_acacia.jpg/640px-Vachellia_tortilis_-_acacia.jpg',
    },
    {
        'name': 'African Violet',
        'scientific_name': 'Saintpaulia ionantha',
        'climate_zones': ['tropical_highland', 'tropical_rainforest'],
        'sun_exposure': ['partial', 'shade'],
        'soil_types': ['loamy', 'peat'],
        'water_conservation': 'moderate',
        'water_frequency': 'When top of soil feels dry',
        'tags': ['ornamental', 'indoor', 'flowering'],
        'care_tips': [
            'Water from below to avoid leaf spotting',
            'Keep in bright, indirect light',
            'Maintain humidity above 50%',
        ],
        'impact_label': 'Native ornamental',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Saintpaulia_ionantha.jpg/640px-Saintpaulia_ionantha.jpg',
    },
    {
        'name': 'Spekboom',
        'scientific_name': 'Portulacaria afra',
        'climate_zones': ['arid_semi_arid', 'mediterranean', 'tropical_savanna'],
        'sun_exposure': ['full_sun', 'partial'],
        'soil_types': ['sandy', 'loamy'],
        'water_conservation': 'ultra_low',
        'water_frequency': 'Every 2-4 weeks',
        'tags': ['carbon-sequestering', 'edible', 'drought-tolerant'],
        'care_tips': [
            'Propagates easily from cuttings',
            'Avoid overwatering — roots rot quickly',
            'Excellent ground cover for slopes',
        ],
        'impact_label': 'Carbon-sequestering champion',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Portulacaria_afra1.jpg/640px-Portulacaria_afra1.jpg',
    },
    {
        'name': 'African Marigold',
        'scientific_name': 'Tagetes erecta',
        'climate_zones': ['tropical_savanna', 'tropical_highland', 'mediterranean'],
        'sun_exposure': ['full_sun'],
        'soil_types': ['loamy', 'sandy', 'clay'],
        'water_conservation': 'moderate',
        'water_frequency': 'Twice a week',
        'tags': ['pest-repellent', 'flowering', 'companion-plant'],
        'care_tips': [
            'Deadhead spent blooms to prolong flowering',
            'Plant near vegetables to deter aphids',
            'Tolerates poor soils',
        ],
        'impact_label': 'Natural pest deterrent',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Tagetes_erecta1.jpg/640px-Tagetes_erecta1.jpg',
    },
    {
        'name': 'Sausage Tree',
        'scientific_name': 'Kigelia africana',
        'climate_zones': ['tropical_savanna', 'tropical_rainforest'],
        'sun_exposure': ['full_sun', 'partial'],
        'soil_types': ['loamy', 'clay', 'lateritic_red_clay'],
        'water_conservation': 'low',
        'water_frequency': 'Weekly during dry spells',
        'tags': ['shade-tree', 'wildlife-friendly', 'medicinal'],
        'care_tips': [
            'Allow plenty of space — mature trees are large',
            'Water deeply during establishment',
            'Falling fruit is heavy — avoid planting near walkways',
        ],
        'impact_label': 'Wildlife habitat',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Kigelia_africana_MS_4276.JPG/640px-Kigelia_africana_MS_4276.JPG',
    },
]


class Command(BaseCommand):
    help = 'Seed the Plant catalogue with sample native African flora.'

    def handle(self, *args, **options):
        created = 0
        for entry in SAMPLE_PLANTS:
            _, was_created = Plant.objects.get_or_create(
                scientific_name=entry['scientific_name'],
                defaults=entry,
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {created} new plant(s). Total catalogue: {Plant.objects.count()}.'
        ))
