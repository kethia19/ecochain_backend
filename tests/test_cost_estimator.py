"""
Integration tests — Cost Estimator endpoints.
Run with: python manage.py test tests.test_cost_estimator
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import User
from apps.build_assistant.models import Layout
from apps.cost_estimator.models import MaterialPrice, LabourRate, CostEstimate, TCOProjection
from apps.cost_estimator.services.cost_calculator import calculate_cost
from apps.cost_estimator.services.tco_calculator import project_tco


def make_user(email='cost@eco.io', password='Pass1234!'):
    return User.objects.create_user(email=email, name='Cost User', password=password, status='ACTIVE')


def auth_client(user):
    client = APIClient()
    resp = client.post('/api/v1/auth/login/', {'email': user.email, 'password': 'Pass1234!'}, format='json')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {resp.data["access"]}')
    return client


def seed_layout(user):
    return Layout.objects.create(
        user=user, bedrooms=3, climate_zone='equatorial', style='modern',
        orientation='south', total_area_sqm=95.0, eco_score=70,
        layout_json={'rooms': [
            {'type': 'bedroom', 'area_sqm': 12},
            {'type': 'living_room', 'area_sqm': 22},
            {'type': 'kitchen', 'area_sqm': 10},
            {'type': 'bathroom', 'area_sqm': 5},
        ]},
    )


def seed_pricing(country='KE'):
    currency = {'NG': 'NGN', 'KE': 'KES', 'GH': 'GHS', 'ZA': 'ZAR', 'ET': 'ETB', 'SN': 'XOF'}.get(country, 'USD')
    price = 2000
    for cat in ('wall', 'foundation', 'roof', 'floor', 'finishing'):
        MaterialPrice.objects.get_or_create(
            name=f'Test Material {cat}', country=country, city='',
            defaults={'category': cat, 'unit': 'sqm', 'price_per_unit': price,
                      'currency': currency, 'carbon_score': 2.0, 'is_eco': False},
        )
    for skill in ('mason', 'carpenter', 'plumber'):
        LabourRate.objects.get_or_create(
            skill_type=skill, country=country, city='',
            defaults={'rate_per_day': 2000, 'currency': currency},
        )


# ── Service-level tests ───────────────────────────────────────────────────────

class CostCalculatorServiceTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.layout = seed_layout(self.user)
        seed_pricing('KE')

    def test_returns_required_keys(self):
        result = calculate_cost(str(self.layout.id), 'KE', '', 'KE')
        for key in ('total_cost', 'currency', 'breakdown'):
            self.assertIn(key, result)

    def test_total_cost_positive(self):
        result = calculate_cost(str(self.layout.id), 'KE', '', 'KE')
        self.assertGreater(result['total_cost'], 0)

    def test_breakdown_is_list(self):
        result = calculate_cost(str(self.layout.id), 'KE', '', 'KE')
        self.assertIsInstance(result['breakdown'], list)

    def test_invalid_layout_raises(self):
        with self.assertRaises(ValueError):
            calculate_cost('00000000-0000-0000-0000-000000000000', 'KE', '', 'KE')


class TCOCalculatorServiceTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.layout = seed_layout(self.user)

    def test_returns_required_keys(self):
        result = project_tco(str(self.layout.id), 'KE', 500000.0, 5)
        for key in ('annual_savings', 'total_savings', 'payback_months', 'savings_breakdown'):
            self.assertIn(key, result)

    def test_total_savings_equals_annual_times_years(self):
        result = project_tco(str(self.layout.id), 'NG', 1000000.0, 5)
        self.assertAlmostEqual(result['total_savings'], result['annual_savings'] * 5, places=1)

    def test_savings_breakdown_has_three_categories(self):
        result = project_tco(str(self.layout.id), 'ZA', 200000.0, 5)
        categories = [s['category'] for s in result['savings_breakdown']]
        self.assertIn('electricity', categories)
        self.assertIn('water', categories)
        self.assertIn('maintenance', categories)

    def test_invalid_layout_raises(self):
        with self.assertRaises(ValueError):
            project_tco('00000000-0000-0000-0000-000000000000', 'KE', 0.0, 5)


# ── API endpoint tests ────────────────────────────────────────────────────────

class EstimateCostAPITest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = auth_client(self.user)
        self.layout = seed_layout(self.user)
        seed_pricing('KE')

    def test_returns_estimate(self):
        resp = self.client.post('/api/v1/cost/estimate', {
            'layout_id': str(self.layout.id), 'country': 'KE',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('total_cost', resp.data)
        self.assertIn('breakdown', resp.data)

    def test_estimate_persisted(self):
        self.client.post('/api/v1/cost/estimate', {
            'layout_id': str(self.layout.id), 'country': 'KE',
        }, format='json')
        self.assertEqual(CostEstimate.objects.filter(user=self.user).count(), 1)

    def test_unknown_layout_returns_404(self):
        resp = self.client.post('/api/v1/cost/estimate', {
            'layout_id': '00000000-0000-0000-0000-000000000000', 'country': 'KE',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_country_rejected(self):
        resp = self.client.post('/api/v1/cost/estimate', {
            'layout_id': str(self.layout.id), 'country': 'XX',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_blocked(self):
        resp = APIClient().post('/api/v1/cost/estimate', {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class TCOProjectionAPITest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = auth_client(self.user)
        self.layout = seed_layout(self.user)
        seed_pricing('KE')
        # Create a cost estimate first so TCO has an upfront cost to work with
        self.client.post('/api/v1/cost/estimate', {
            'layout_id': str(self.layout.id), 'country': 'KE',
        }, format='json')

    def test_returns_tco(self):
        resp = self.client.post('/api/v1/cost/tco-projection', {
            'layout_id': str(self.layout.id), 'country': 'KE',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('annual_savings', resp.data)
        self.assertIn('payback_months', resp.data)
        self.assertIn('savings_breakdown', resp.data)

    def test_custom_projection_years(self):
        resp = self.client.post('/api/v1/cost/tco-projection', {
            'layout_id': str(self.layout.id), 'country': 'KE', 'projection_years': 10,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['projection_years'], 10)

    def test_tco_persisted(self):
        self.client.post('/api/v1/cost/tco-projection', {
            'layout_id': str(self.layout.id), 'country': 'KE',
        }, format='json')
        self.assertGreater(TCOProjection.objects.filter(user=self.user).count(), 0)


class PricingMaterialsAPITest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = auth_client(self.user)
        seed_pricing('NG')

    def test_returns_all_materials(self):
        resp = self.client.get('/api/v1/pricing/materials')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)

    def test_filter_by_country(self):
        resp = self.client.get('/api/v1/pricing/materials?country=NG')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for item in resp.data:
            self.assertEqual(item['country'], 'NG')

    def test_filter_by_category(self):
        resp = self.client.get('/api/v1/pricing/materials?country=NG&category=wall')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for item in resp.data:
            self.assertEqual(item['category'], 'wall')

    def test_material_has_last_updated(self):
        resp = self.client.get('/api/v1/pricing/materials')
        if resp.data:
            self.assertIn('last_updated', resp.data[0])


class PricingLabourAPITest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = auth_client(self.user)
        seed_pricing('KE')

    def test_returns_labour_rates(self):
        resp = self.client.get('/api/v1/pricing/labour')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_filter_by_country_and_skill(self):
        resp = self.client.get('/api/v1/pricing/labour?country=KE&skill_type=mason')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for item in resp.data:
            self.assertEqual(item['country'], 'KE')
            self.assertEqual(item['skill_type'], 'mason')


class CostReportAPITest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = auth_client(self.user)
        self.layout = seed_layout(self.user)
        seed_pricing('KE')

    def test_returns_pdf(self):
        resp = self.client.get(f'/api/v1/cost/report/{self.layout.id}?country=KE')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        self.assertTrue(resp.content.startswith(b'%PDF'))

    def test_other_user_blocked(self):
        other = User.objects.create_user(email='other2@eco.io', name='Other2', password='Pass1234!', status='ACTIVE')
        other_client = auth_client(other)
        resp = other_client.get(f'/api/v1/cost/report/{self.layout.id}')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
