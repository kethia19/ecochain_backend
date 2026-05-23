"""
Integration tests — Build Assistant endpoints.
Run with: python manage.py test tests.test_build_assistant
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import User
from apps.build_assistant.models import ClimateZone, EcoMaterial, Layout
from apps.build_assistant.services import generate_layout, suggest_eco_materials


def make_user(email='test@eco.io', password='Pass1234!'):
    return User.objects.create_user(email=email, name='Test User', password=password, status='ACTIVE')


def auth_client(user):
    client = APIClient()
    resp = client.post('/api/v1/auth/login/', {'email': user.email, 'password': 'Pass1234!'}, format='json')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {resp.data["access"]}')
    return client


def seed_zone():
    return ClimateZone.objects.create(
        code='sahel',
        name='Sahel',
        description='Hot semi-arid zone',
        typical_countries=['Niger', 'Mali'],
        cooling_strategy='Cross ventilation',
        passive_features=['roof overhang'],
    )


def seed_material(element_type='wall'):
    return EcoMaterial.objects.create(
        name='Compressed Earth Blocks',
        element_type=element_type,
        description='CEB wall',
        sustainability_rationale='Zero cement, local soil.',
        carbon_score=1.2,
        cost_delta_pct=-15.0,
        suitable_climate_zones=['sahel', 'equatorial'],
    )


# ── Service-level tests ───────────────────────────────────────────────────────

class GenerateLayoutServiceTest(TestCase):
    def test_returns_expected_keys(self):
        result = generate_layout({'bedrooms': 3, 'climate_zone': 'sahel', 'style': 'modern', 'orientation': 'south'})
        self.assertIn('layout_json', result)
        self.assertIn('eco_score', result)
        self.assertIn('total_area_sqm', result)

    def test_room_count_includes_living_kitchen(self):
        result = generate_layout({'bedrooms': 2, 'climate_zone': 'equatorial', 'style': 'traditional', 'orientation': 'east'})
        types = [r['type'] for r in result['layout_json']['rooms']]
        self.assertIn('bedroom', types)
        self.assertIn('living_room', types)
        self.assertIn('kitchen', types)

    def test_eco_score_in_range(self):
        result = generate_layout({'bedrooms': 1, 'climate_zone': 'highland', 'style': 'traditional', 'orientation': 'south'})
        self.assertGreaterEqual(result['eco_score'], 0)
        self.assertLessEqual(result['eco_score'], 100)

    def test_total_area_positive(self):
        result = generate_layout({'bedrooms': 4, 'climate_zone': 'semi_arid', 'style': 'hybrid', 'orientation': 'west'})
        self.assertGreater(result['total_area_sqm'], 0)


class SuggestMaterialsServiceTest(TestCase):
    def setUp(self):
        seed_material('wall')

    def test_returns_list(self):
        suggestions = suggest_eco_materials('wall', 'sahel')
        self.assertIsInstance(suggestions, list)

    def test_suggestion_has_prompt(self):
        suggestions = suggest_eco_materials('wall', 'sahel')
        if suggestions:
            self.assertIn('prompt', suggestions[0])
            self.assertIn('carbon_score', suggestions[0])

    def test_unknown_climate_zone_falls_back(self):
        suggestions = suggest_eco_materials('wall', 'arctic')
        self.assertIsInstance(suggestions, list)


# ── API endpoint tests ────────────────────────────────────────────────────────

class GenerateLayoutAPITest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = auth_client(self.user)

    def test_creates_layout(self):
        resp = self.client.post('/api/v1/layout/generate', {
            'bedrooms': 3, 'climate_zone': 'sahel', 'style': 'modern', 'orientation': 'south',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', resp.data)
        self.assertIn('eco_score', resp.data)
        self.assertIn('layout_json', resp.data)

    def test_layout_persisted_in_db(self):
        self.client.post('/api/v1/layout/generate', {
            'bedrooms': 2, 'climate_zone': 'equatorial', 'style': 'traditional', 'orientation': 'east',
        }, format='json')
        self.assertEqual(Layout.objects.filter(user=self.user).count(), 1)

    def test_invalid_climate_zone_rejected(self):
        resp = self.client.post('/api/v1/layout/generate', {
            'bedrooms': 2, 'climate_zone': 'arctic', 'style': 'modern', 'orientation': 'south',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_blocked(self):
        resp = APIClient().post('/api/v1/layout/generate', {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class SuggestMaterialsAPITest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = auth_client(self.user)
        seed_material('wall')

    def test_returns_suggestions(self):
        resp = self.client.post('/api/v1/materials/suggest', {
            'element_type': 'wall', 'climate_zone': 'sahel',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('suggestions', resp.data)

    def test_invalid_element_type_rejected(self):
        resp = self.client.post('/api/v1/materials/suggest', {
            'element_type': 'chimney', 'climate_zone': 'sahel',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class LayoutDetailAPITest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = auth_client(self.user)
        resp = self.client.post('/api/v1/layout/generate', {
            'bedrooms': 3, 'climate_zone': 'sahel', 'style': 'modern', 'orientation': 'south',
        }, format='json')
        self.layout_id = resp.data['id']

    def test_get_layout(self):
        resp = self.client.get(f'/api/v1/layouts/{self.layout_id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(str(resp.data['id']), str(self.layout_id))

    def test_update_layout_name(self):
        resp = self.client.put(f'/api/v1/layouts/{self.layout_id}', {'name': 'My Dream Home'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['name'], 'My Dream Home')

    def test_other_user_cannot_access(self):
        other = User.objects.create_user(email='other@eco.io', name='Other', password='Pass1234!', status='ACTIVE')
        other_client = auth_client(other)
        resp = other_client.get(f'/api/v1/layouts/{self.layout_id}')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class ClimateZonesAPITest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = auth_client(self.user)
        seed_zone()

    def test_returns_zones_list(self):
        resp = self.client.get('/api/v1/climate-zones')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)

    def test_zone_has_required_fields(self):
        resp = self.client.get('/api/v1/climate-zones')
        zone = resp.data[0]
        for field in ('code', 'name', 'description', 'cooling_strategy'):
            self.assertIn(field, zone)
