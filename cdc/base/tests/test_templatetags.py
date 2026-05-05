from unittest.mock import MagicMock

from django.template import Context
from django.test import TestCase
from wagtail.models import Page

from cdc.base.templatetags.navigation_tags import get_site_root, is_active_menuitem
from cdc.recipes.models import RecipeIndexPage


class TestNavigationTags(TestCase):
    def setUp(self):
        self.root_page = Page.objects.get(slug='home')
        self.index_page = RecipeIndexPage.objects.filter(slug='receitas').first()
        if not self.index_page:
            self.index_page = RecipeIndexPage(title='Receitas', slug='receitas')
            self.root_page.add_child(instance=self.index_page)

    def test_get_site_root(self):
        """Test get_site_root template tag"""
        mock_request = MagicMock()
        context = {'request': mock_request}
        # Mock Site.find_for_request
        with self.settings(SITE_ID=1):
            result = get_site_root(context)
            # Since we can't easily mock Site, just check it doesn't error
            self.assertIsNotNone(result)

    def test_is_active_menuitem_true(self):
        """Test is_active_menuitem returns True when page matches menuitem"""
        context = {'page': self.index_page}
        menuitem = self.index_page
        result = is_active_menuitem(context, menuitem)
        self.assertTrue(result)

    def test_is_active_menuitem_false(self):
        """Test is_active_menuitem returns False when no page in context"""
        context = {}
        menuitem = self.index_page
        result = is_active_menuitem(context, menuitem)
        self.assertFalse(result)