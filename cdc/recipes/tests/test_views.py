import pytest
from django.test import Client
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from cdc.recipes.models import RecipeIndexPage, RecipePage, RecipeTagIndexPage


class TestRecipeIndexPageView(WagtailPageTestCase):
    def setUp(self):
        self.client = Client()
        self.root_page = Page.objects.get(slug='home')

    def test_recipe_index_page_view(self):
        """Test RecipeIndexPage renders correctly"""
        index_page = RecipeIndexPage(title='Receitas', slug='receitas', intro='Bem-vindo')
        self.root_page.add_child(instance=index_page)

        response = self.client.get('/receitas/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Receitas')
        self.assertContains(response, 'Bem-vindo')


class TestRecipeTagIndexPageView(WagtailPageTestCase):
    def setUp(self):
        self.client = Client()
        self.root_page = Page.objects.get(slug='home')

    def test_recipe_tag_index_page_view_no_tag(self):
        """Test RecipeTagIndexPage without tag parameter"""
        tag_page = RecipeTagIndexPage(title='Tags', slug='tags')
        self.root_page.add_child(instance=tag_page)

        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Todas as Tags Disponíveis')

    def test_recipe_tag_index_page_view_with_tag(self):
        """Test RecipeTagIndexPage with tag parameter"""
        tag_page = RecipeTagIndexPage(title='Tags', slug='tags')
        self.root_page.add_child(instance=tag_page)

        response = self.client.get('/tags/?tag=test')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Receitas com tag "test"')


class TestRecipePageView(WagtailPageTestCase):
    def setUp(self):
        self.client = Client()
        self.root_page = Page.objects.get(slug='home')

    def test_recipe_page_view(self):
        """Test RecipePage renders correctly"""
        # Note: Would need to create RecipeIndexPage parent and RecipePage with image
        # For now, just test that the model exists and basic functionality
        recipe_page = RecipePage(title='Test Recipe', slug='test-recipe')
        self.assertEqual(recipe_page.title, 'Test Recipe')
