"""Tests for recipe API views, including pending recipe handling."""

from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from wagtail.test.utils import WagtailTestUtils

from cdc.recipes.models import RecipePage


class TestPendingRecipesView(WagtailTestUtils, TestCase):
    def setUp(self):
        self.login()
        from wagtail.models import Page

        self.root_page = Page.objects.get(slug='home')

        from cdc.recipes.models import RecipeIndexPage

        self.index_page = RecipeIndexPage.objects.filter(slug='recipes').first()
        if not self.index_page:
            self.index_page = RecipeIndexPage(title='Recipes', slug='recipes')
            self.root_page.add_child(instance=self.index_page)

    @patch('cdc.recipes.views.settings')
    def test_get_pending_recipes_success(self, mock_settings):
        """Test GET pending recipes with valid API key"""
        mock_settings.RECIPE_API_KEY = 'test_key'

        # Create a recipe with pending status
        recipe = RecipePage(title='Pending Recipe', slug='pending', status='pending_review', raw_input='Test input')
        self.index_page.add_child(instance=recipe)

        response = self.client.get(reverse('recipes:pending'), HTTP_X_API_KEY='test_key')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('pendings', data)
        self.assertEqual(len(data['pendings']), 1)
        self.assertEqual(data['pendings'][0]['title'], 'Pending Recipe')

    @patch('cdc.recipes.views.settings')
    def test_get_pending_recipes_unauthorized(self, mock_settings):
        """Test GET pending recipes with invalid API key"""
        mock_settings.RECIPE_API_KEY = 'test_key'

        response = self.client.get(reverse('recipes:pending'), HTTP_X_API_KEY='wrong_key')

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('error', data)

    @patch('cdc.recipes.views.settings')
    def test_post_update_recipe_success(self, mock_settings):
        """Test POST update recipe with processed data"""
        mock_settings.RECIPE_API_KEY = 'test_key'

        recipe = RecipePage(title='Test Recipe', slug='test', status='pending_review', raw_input='Original input')
        self.index_page.add_child(instance=recipe)

        response = self.client.post(
            reverse('recipes:pending'),
            data={
                'id': recipe.id,
                'ai_response': {
                    'description': 'AI processed description',
                    'directions': 'AI processed directions',
                    'font': 'AI processed font',
                },
                'tags': 'tag1, tag2',
            },
            HTTP_X_API_KEY='test_key',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'updated')

        # Refresh from DB
        recipe.refresh_from_db()
        self.assertEqual(recipe.status, 'final_review')
        self.assertEqual(recipe.raw_ai_response['description'], 'AI processed description')
        self.assertEqual(recipe.description, 'AI processed description')

    @patch('cdc.recipes.views.settings')
    def test_post_update_recipe_not_found(self, mock_settings):
        """Test POST update with non-existent recipe ID"""
        mock_settings.RECIPE_API_KEY = 'test_key'

        response = self.client.post(
            reverse('recipes:pending'),
            data={'id': 999, 'processed_description': 'Test'},
            HTTP_X_API_KEY='test_key',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error', data)

    @patch('cdc.recipes.views.settings')
    def test_post_update_recipe_unauthorized(self, mock_settings):
        """Test POST update recipe with invalid API key"""
        mock_settings.RECIPE_API_KEY = 'test_key'

        recipe = RecipePage(title='Test Recipe', slug='test', status='pending_review')
        self.index_page.add_child(instance=recipe)

        response = self.client.post(
            reverse('recipes:pending'),
            data={'id': recipe.id, 'ai_response': {}},
            HTTP_X_API_KEY='wrong_key',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Unauthorized')

    @patch('cdc.recipes.views.settings')
    def test_post_update_recipe_invalid_json(self, mock_settings):
        """Test POST update recipe with invalid JSON"""
        mock_settings.RECIPE_API_KEY = 'test_key'

        response = self.client.post(
            reverse('recipes:pending'),
            data='invalid json',
            HTTP_X_API_KEY='test_key',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid JSON')

    @patch('cdc.recipes.views.settings')
    def test_post_update_recipe_without_tags(self, mock_settings):
        """Test POST update recipe without tags"""
        mock_settings.RECIPE_API_KEY = 'test_key'

        recipe = RecipePage(title='Test Recipe', slug='test', status='pending_review', raw_input='Original input')
        self.index_page.add_child(instance=recipe)

        response = self.client.post(
            reverse('recipes:pending'),
            data={
                'id': recipe.id,
                'ai_response': {
                    'description': 'AI processed description',
                    'directions': 'AI processed directions',
                    'font': 'AI processed font',
                },
                # No 'tags' key, so tags_str will be empty
            },
            HTTP_X_API_KEY='test_key',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'updated')

        # Refresh from DB and check tags are not set
        recipe.refresh_from_db()
        self.assertEqual(recipe.status, 'final_review')
        self.assertEqual(recipe.tags.count(), 0)  # No tags set
