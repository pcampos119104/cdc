import json

import pytest


class TestBaseViews:
    def test_home(self, client, db):
        """
        Test if home page works
        """
        resp = client.get('/')
        assert resp.status_code == 200

    def test_simple_page(self, client, db):
        """
        Test if simple page works
        """
        resp = client.get('/base/simple/')
        assert resp.status_code == 200
        assert 'Página Simples com Botão' in resp.content.decode()

    def test_api_response_get(self, client, db):
        """
        Test if API response view works with GET
        """
        resp = client.get('/base/api/response/')
        assert resp.status_code == 200
        assert resp['Content-Type'] == 'application/json'

        data = json.loads(resp.content.decode())
        assert data['status'] == 'success'
        assert 'Botão foi pressionado com sucesso!' in data['message']

    def test_api_response_post_not_allowed(self, client, db):
        """
        Test if API response view rejects POST
        """
        resp = client.post('/base/api/response/')
        assert resp.status_code == 405
