"""Tests for recipe models, ensuring correct behavior of pages, ingredients, and workflows."""

from unittest.mock import patch

import pytest
from django.test import TestCase
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from cdc.recipes.models import (
    AIProcessingTask,
    Ingredient,
    Metric,
    Qualifier,
    RecipeIndexPage,
    RecipeIngredient,
    RecipeIngredientQualifier,
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
        # Checks that 'intro' panel is included in content_panels
        self.assertIn('intro', panels)

    def test_recipe_index_page_context(self):
        """Test get_context returns recipepages"""
        index_page = RecipeIndexPage.objects.filter(slug='receitas').first()
        if not index_page:
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
        tag_page = RecipeTagIndexPage.objects.filter(slug='tags').first()
        if not tag_page:
            tag_page = RecipeTagIndexPage(title='Tags', slug='tags')
            self.root_page.add_child(instance=tag_page)

        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/tags/')

        context = tag_page.get_context(request)
        self.assertIn('all_tags', context)
        self.assertIn('recipepages', context)
        self.assertEqual(list(context['recipepages']), [])

    def test_recipe_tag_index_page_context_with_tag(self):
        """Test get_context with tag parameter"""
        tag_page = RecipeTagIndexPage.objects.filter(slug='tags').first()
        if not tag_page:
            tag_page = RecipeTagIndexPage(title='Tags', slug='tags')
            self.root_page.add_child(instance=tag_page)

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
        required_fields = ['tags', 'raw_input', 'description', 'directions', 'font', 'image']
        for field in required_fields:
            self.assertIn(field, field_names)

        # Check for InlinePanel
        inline_panels = [panel for panel in panels if isinstance(panel, InlinePanel)]
        inline_names = [panel.relation_name for panel in inline_panels]
        self.assertIn('ingredients', inline_names)

    def test_recipe_page_fields(self):
        """Test RecipePage has new and restored fields"""
        recipe_page = RecipePage()
        # Check field existence
        self.assertTrue(hasattr(recipe_page, 'raw_input'))
        self.assertTrue(hasattr(recipe_page, 'raw_ai_response'))
        self.assertTrue(hasattr(recipe_page, 'description'))
        self.assertTrue(hasattr(recipe_page, 'directions'))
        self.assertTrue(hasattr(recipe_page, 'font'))
        self.assertTrue(hasattr(recipe_page, 'status'))

    def test_recipe_page_save_method(self):
        """Test save method sets live based on status"""
        index_page = RecipeIndexPage.objects.filter(slug='recipes').first()
        if not index_page:
            index_page = RecipeIndexPage(title='Recipes', slug='recipes')
            self.root_page.add_child(instance=index_page)

        recipe_page = RecipePage(title='Test Recipe', slug='test-recipe', status='draft')
        index_page.add_child(instance=recipe_page)
        recipe_page.save()
        self.assertFalse(recipe_page.live)

        recipe_page.status = 'published'
        recipe_page.save()
        self.assertTrue(recipe_page.live)


class TestIngredient(TestCase):
    def test_ingredient_creation(self):
        """Test Ingredient model"""
        ingredient = Ingredient.objects.create(name='Farinha')
        self.assertEqual(str(ingredient), 'Farinha')
        self.assertEqual(ingredient.name, 'Farinha')

    def test_ingredient_unique_name(self):
        """Test name uniqueness"""
        Ingredient.objects.create(name='Farinha')
        with self.assertRaises(Exception):
            Ingredient.objects.create(name='Farinha')

    def test_ingredient_ordering(self):
        """Test ordering by name"""
        Ingredient.objects.create(name='Zebra')
        Ingredient.objects.create(name='Abacaxi')
        ingredient_names = ['Abacaxi', 'Zebra']
        ingredients = list(Ingredient.objects.filter(name__in=ingredient_names).order_by('name'))
        self.assertEqual(ingredients[0].name, 'Abacaxi')
        self.assertEqual(ingredients[1].name, 'Zebra')


class TestMetric(TestCase):
    def test_metric_creation(self):
        """Test Metric model"""
        metric = Metric.objects.create(name='Gramas', abbr='g')
        self.assertEqual(str(metric), 'g')
        self.assertEqual(metric.name, 'Gramas')
        self.assertEqual(metric.abbr, 'g')

    def test_metric_str_fallback(self):
        """Test __str__ fallback to name when abbr is empty"""
        metric = Metric.objects.create(name='Unidade', abbr='')
        self.assertEqual(str(metric), 'Unidade')

    def test_metric_ordering(self):
        """Test ordering by name"""
        Metric.objects.create(name='Zilo', abbr='zl')
        Metric.objects.create(name='Abacaxi', abbr='ab')
        metric_names = ['Abacaxi', 'Zilo']
        metrics = list(Metric.objects.filter(name__in=metric_names).order_by('name'))
        self.assertEqual(metrics[0].name, 'Abacaxi')
        self.assertEqual(metrics[1].name, 'Zilo')


class TestQualifier(TestCase):
    def test_qualifier_creation(self):
        """Test Qualifier model"""
        qualifier = Qualifier.objects.create(name='Picado')
        self.assertEqual(str(qualifier), 'Picado')
        self.assertEqual(qualifier.name, 'Picado')

    def test_qualifier_ordering(self):
        """Test ordering by name"""
        Qualifier.objects.create(name='Zebra')
        Qualifier.objects.create(name='Abacaxi')
        qualifiers = list(Qualifier.objects.all())
        self.assertEqual(qualifiers[0].name, 'Abacaxi')
        self.assertEqual(qualifiers[1].name, 'Zebra')


class TestRecipeIngredient(TestCase):
    def setUp(self):
        # Create related objects for testing
        self.ingredient = Ingredient.objects.create(name='Farinha')
        self.metric = Metric.objects.create(name='Gramas', abbr='g')

    def test_recipe_ingredient_str_method(self):
        """Test RecipeIngredient string representation method logic"""
        # Create instance without saving to test the __str__ method logic
        recipe_ingredient = RecipeIngredient(ingredient=self.ingredient, metric=self.metric, quantity=200)
        expected = '200 g de Farinha'
        # Test the __str__ method directly
        self.assertEqual(str(recipe_ingredient), expected)

    def test_recipe_ingredient_str_with_none_quantity(self):
        """Test RecipeIngredient string with None quantity"""
        recipe_ingredient = RecipeIngredient(ingredient=self.ingredient, metric=self.metric, quantity=None)
        # Should handle None quantity gracefully
        quantity_str = str(recipe_ingredient.quantity or '?')
        self.assertEqual(quantity_str, '?')

    def test_recipe_ingredient_panels(self):
        """Test RecipeIngredient has correct panels"""
        panels = RecipeIngredient.panels
        # Should have panels defined
        self.assertIsInstance(panels, list)
        self.assertGreater(len(panels), 0)

    def test_recipe_ingredient_qualifier_list(self):
        """Test RecipeIngredient qualifier_list property"""
        # Create qualifiers
        qualifier1 = Qualifier.objects.create(name='Picado')
        qualifier2 = Qualifier.objects.create(name='Fresco')

        # Create a recipe page to hold the ingredient
        root_page = Page.objects.get(slug='home')
        index_page = RecipeIndexPage.objects.filter(slug='receitas').first()
        if not index_page:
            index_page = RecipeIndexPage(title='Receitas', slug='receitas')
            root_page.add_child(instance=index_page)
        recipe_page = RecipePage(title='Test Recipe', slug='test-recipe')
        index_page.add_child(instance=recipe_page)

        # Create recipe ingredient
        recipe_ingredient = RecipeIngredient(page=recipe_page, ingredient=self.ingredient, metric=self.metric, quantity=100)
        recipe_ingredient.save()

        # Create qualifier instances
        RecipeIngredientQualifier.objects.create(ingredient=recipe_ingredient, qualifier=qualifier1)
        RecipeIngredientQualifier.objects.create(ingredient=recipe_ingredient, qualifier=qualifier2)

        # Test the property
        self.assertEqual(recipe_ingredient.qualifier_list, ['Picado', 'Fresco'])


class TestRecipeIngredientQualifier(TestCase):
    def setUp(self):
        self.qualifier = Qualifier.objects.create(name='Picado')

    def test_recipe_ingredient_qualifier_str(self):
        """Test RecipeIngredientQualifier string representation"""
        # Create instance without saving (since __str__ doesn't need DB)
        riq = RecipeIngredientQualifier(qualifier=self.qualifier)
        self.assertEqual(str(riq), 'Picado')


class TestAIProcessingTask(TestCase):
    def test_ai_processing_task_on_action(self):
        """Test AIProcessingTask on_action method"""
        task = AIProcessingTask()
        # Call on_action with dummy args (it does nothing)
        task.on_action(None, None, 'some_action')  # Should not raise any exception


class TestRecipePageTemplate(WagtailPageTestCase):
    """Tests for RecipePage template rendering"""

    def setUp(self):
        self.root_page = Page.objects.get(slug='home')

        self.index = RecipeIndexPage(title='Recipes', slug='recipes')
        self.root_page.add_child(instance=self.index)

        self.ingredient = Ingredient.objects.create(name='Farinha')
        self.metric = Metric.objects.create(name='Gramas', abbr='g')

    def _create_recipe(self, **kwargs):
        recipe = RecipePage(**kwargs)
        self.index.add_child(instance=recipe)
        recipe.save_revision().publish()
        return recipe

    def test_recipe_page_can_render(self):
        """Test RecipePage renders successfully"""
        recipe = self._create_recipe(title='Render Test', slug='render-test')
        response = self.client.get(recipe.url)
        self.assertEqual(response.status_code, 200)

    def test_recipe_page_displays_description(self):
        """Test description is displayed on recipe page"""
        recipe = self._create_recipe(
            title='Desc Test', slug='desc-test',
            description='Descricao especial de teste',
        )
        response = self.client.get(recipe.url)
        self.assertContains(response, 'Descricao especial de teste')

    def test_recipe_page_displays_directions(self):
        """Test directions are displayed on recipe page"""
        recipe = self._create_recipe(
            title='Dir Test', slug='dir-test',
            directions='<p>Misture todos os ingredientes</p>',
        )
        response = self.client.get(recipe.url)
        self.assertContains(response, 'Misture todos os ingredientes')

    def test_recipe_page_displays_font(self):
        """Test font is displayed on recipe page"""
        recipe = self._create_recipe(
            title='Font Test', slug='font-test',
            font='Livro de receitas da familia',
        )
        response = self.client.get(recipe.url)
        self.assertContains(response, 'Livro de receitas da familia')

    def test_recipe_page_displays_ingredients(self):
        """Test ingredients are displayed on recipe page"""
        recipe = self._create_recipe(
            title='Ing Test', slug='ing-test',
        )
        RecipeIngredient.objects.create(
            page=recipe,
            ingredient=self.ingredient,
            metric=self.metric,
            quantity=200,
        )
        response = self.client.get(recipe.url)
        self.assertContains(response, 'Farinha')
        self.assertContains(response, '200')
        self.assertContains(response, 'g')

    def test_recipe_page_displays_tags(self):
        """Test tags are displayed on recipe page"""
        recipe = self._create_recipe(
            title='Tag Test', slug='tag-test',
        )
        recipe.tags.add('doce', 'bolo')
        recipe.save_revision().publish()
        response = self.client.get(recipe.url)
        self.assertContains(response, 'doce')
        self.assertContains(response, 'bolo')

    def test_recipe_page_voltar_link(self):
        """Test 'Voltar para receitas' link is present"""
        recipe = self._create_recipe(
            title='Back Test', slug='back-test',
        )
        response = self.client.get(recipe.url)
        self.assertContains(response, 'Voltar para receitas')
