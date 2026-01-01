import pytest
from wagtail.admin.panels import FieldPanel
from wagtail.test.utils import WagtailPageTestCase

from cdc.base.models import HomePage


class TestHomePage(WagtailPageTestCase):
    def test_home_page_creation(self):
        """Test that HomePage can be created"""
        home_page = HomePage(title='Home', slug='home')
        self.assertEqual(home_page.title, 'Home')
        self.assertEqual(home_page.slug, 'home')

    def test_home_page_content_panels(self):
        """Test that HomePage has correct content panels"""
        # Test content_panels includes body field
        panels = HomePage.content_panels
        field_panels = [panel for panel in panels if isinstance(panel, FieldPanel)]
        field_names = [panel.field_name for panel in field_panels]
        self.assertIn('body', field_names)

    def test_home_page_template(self):
        """Test that HomePage uses specific template"""
        # HomePage should use 'base/home_page.html'
        self.assertEqual(getattr(HomePage, 'template', None), 'base/home_page.html')
