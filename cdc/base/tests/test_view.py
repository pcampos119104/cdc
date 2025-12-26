import pytest


class TestBaseViews:
    def test_home(self, client, db):
        """
        Test if home page works
        """
        resp = client.get('/')
        assert resp.status_code == 200
