import pytest
from django.test import TestCase
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from cdc.recipes.models import (
    RecipeIndexPage,
    RecipePage,
    RecipeTagIndexPage,
)


class TestRecipeIndexPage(WagtailPageTestCase):
    def setUp(self):
        self.root_page = Page.objects.get(slug='home')

    def test_recipe_index_page_creation(self):
        """Test RecipeIndexPage can be created"""
        index_page = RecipeIndexPage(title='Receitas', slug='receitas')
        self.assertEqual(index_page.title, 'Receitas')

    def test_recipe_index_page_subpage_types(self):
        """Test RecipeIndexPage allows RecipePage as subpage"""
        self.assertIn('recipes.RecipePage', RecipeIndexPage.subpage_types)

    def test_recipe_index_page_content_panels(self):
        """Test RecipeIndexPage has intro field"""
        panels = RecipeIndexPage.content_panels
        # The intro field is passed directly as a string in the content_panels list
        self.assertIn('intro', panels)

    def test_recipe_index_page_context(self):
        """Test get_context returns recipepages"""
        index_page = RecipeIndexPage(title='Receitas', slug='receitas')
        self.root_page.add_child(instance=index_page)

        context = index_page.get_context(None)
        self.assertIn('recipepages', context)


class TestRecipeTagIndexPage(WagtailPageTestCase):
    def setUp(self):
        self.root_page = Page.objects.get(slug='home')

    def test_recipe_tag_index_page_creation(self):
        """Test RecipeTagIndexPage can be created"""
        tag_page = RecipeTagIndexPage(title='Tags', slug='tags')
        self.assertEqual(tag_page.title, 'Tags')

    def test_recipe_tag_index_page_template(self):
        """Test RecipeTagIndexPage uses correct template"""
        self.assertEqual(RecipeTagIndexPage.template, 'recipes/recipe_tag_index_page.html')

    def test_recipe_tag_index_page_context_no_tag(self):
        """Test get_context without tag parameter"""
        tag_page = RecipeTagIndexPage(title='Tags', slug='tags')
        self.root_page.add_child(instance=tag_page)

        # Create a mock request without GET parameters
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/tags/')

        context = tag_page.get_context(request)
        self.assertIn('all_tags', context)
        self.assertIn('recipepages', context)
        # recipepages should be empty queryset
        self.assertEqual(list(context['recipepages']), [])

    def test_recipe_tag_index_page_context_with_tag(self):
        """Test get_context with tag parameter"""
        tag_page = RecipeTagIndexPage(title='Tags', slug='tags')
        self.root_page.add_child(instance=tag_page)

        # Create mock request with tag parameter
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/tags/?tag=test')

        context = tag_page.get_context(request)
        self.assertIn('current_tag', context)
        self.assertEqual(context['current_tag'], 'test')
        self.assertIn('recipepages', context)


class TestRecipePage(WagtailPageTestCase):
    def setUp(self):
        self.root_page = Page.objects.get(slug='home')

    def test_recipe_page_creation(self):
        """Test RecipePage basic creation"""
        # Note: Would need image for full creation, testing basic fields
        recipe_page = RecipePage(title='Test Recipe', slug='test-recipe')
        self.assertEqual(recipe_page.title, 'Test Recipe')

    def test_recipe_page_parent_page_types(self):
        """Test RecipePage parent restrictions"""
        self.assertIn('recipes.RecipeIndexPage', RecipePage.parent_page_types)

    def test_recipe_page_subpage_types(self):
        """Test RecipePage doesn't allow subpages"""
        self.assertEqual(RecipePage.subpage_types, [])

    def test_recipe_page_content_panels(self):
        """Test RecipePage has all required content panels"""
        panels = RecipePage.content_panels
        field_panels = [panel for panel in panels if isinstance(panel, FieldPanel)]
        field_names = [panel.field_name for panel in field_panels]
        required_fields = ['tags', 'description', 'directions', 'font', 'image']
        for field in required_fields:
            self.assertIn(field, field_names)

        # Check for InlinePanel
        inline_panels = [panel for panel in panels if isinstance(panel, InlinePanel)]
        inline_names = [panel.relation_name for panel in inline_panels]
        # No inline panels expected after removal
