import pytest
from django.urls import reverse


class TestBaseViews:
    def test_home(self, client):
        """
        Test if home page works
        """
        resp = client.get(reverse('base:home'))
        assert resp.status_code == 200
