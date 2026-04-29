from django.test import TestCase
from wagtail.test.utils import WagtailTestUtils

from cdc.recipes.models import Ingredient, Metric, Qualifier


class TestIngredientSnippet(WagtailTestUtils, TestCase):
    def setUp(self):
        self.login()

    def test_ingredient_snippet_viewset(self):
        """Test Ingredient snippet admin interface"""
        # Test list view
        response = self.client.get('/cms/snippets/recipes/ingredient/')
        self.assertEqual(response.status_code, 200)

    def test_ingredient_create(self):
        """Test creating ingredient via admin"""
        response = self.client.post('/cms/snippets/recipes/ingredient/add/', {'name': 'Test Ingredient'})
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)


class TestMetricSnippet(WagtailTestUtils, TestCase):
    def setUp(self):
        self.login()

    def test_metric_snippet_viewset(self):
        """Test Metric snippet admin interface"""
        response = self.client.get('/cms/snippets/recipes/metric/')
        self.assertEqual(response.status_code, 200)

    def test_metric_create(self):
        """Test creating metric via admin"""
        response = self.client.post('/cms/snippets/recipes/metric/add/', {'name': 'Test Metric', 'abbr': 'TM'})
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)


class TestQualifierSnippet(WagtailTestUtils, TestCase):
    def setUp(self):
        self.login()

    def test_qualifier_snippet_viewset(self):
        """Test Qualifier snippet admin interface"""
        response = self.client.get('/cms/snippets/recipes/qualifier/')
        self.assertEqual(response.status_code, 200)

    def test_qualifier_create(self):
        """Test creating qualifier via admin"""
        response = self.client.post('/cms/snippets/recipes/qualifier/add/', {'name': 'Test Qualifier'})
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
