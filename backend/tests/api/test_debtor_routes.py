import pytest

import random

from debtor.models import Debtor


@pytest.mark.api
class TestDebtorRoutes:
    """
    API tests for debtor endpoints.

    Covers debtor creation, retrieval, listing,
    authentication, authorization and validation scenarios.
    """

    def test_list_debtors_success(self, client, debtor, auth_headers_admin):
        response = client.get('/debtor/list', headers=auth_headers_admin)

        assert response.status_code == 200

        data = response.json

        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_retrieve_debtor_success(self, client, debtor, auth_headers_admin):
        response = client.get(
            f"/debtor/{debtor.id}/detail",
            headers=auth_headers_admin
        )

        assert response.status_code == 200

        data = response.json

        assert data["id"] == str(debtor.id)
        assert data["name"] == debtor.name
        assert data["document"] == debtor.document

    def test_retrieve_debtor_not_found(self, client, auth_headers_admin):
        response = client.get(
            f"/debtor/{random.randint(1, 100)}/detail",
            headers=auth_headers_admin
        )

        assert response.status_code == 404

    def test_create_debtor_success(self, client, auth_headers_admin):
        payload = {
            "name": "John Doe",
            "document": "123.456.789-09",
            "email": "johndoe@test.com",
            "phone": "11999999999",
        }

        response = client.post("/debtor/add", json=payload, headers=auth_headers_admin)

        assert response.status_code == 201

        debtor = Debtor.query.filter_by(email="johndoe@test.com").first()

        assert debtor is not None
        assert debtor.name == payload["name"]

    def test_create_debtor_without_name_returns_400(self, client, auth_headers_admin):
        payload = {
            "document": "123.456.789-09",
            "email": "johndoe@test.com",
            "phone": "11999999999",
        }

        response = client.post("/debtor/add", json=payload, headers=auth_headers_admin)

        assert response.status_code == 400

    def test_create_debtor_with_invalid_email_returns_400(self, client, auth_headers_admin):
        payload = {
            "name": "John Doe",
            "document": "123.456.789-09",
            "email": "invalid-email",
            "phone": "11999999999",
        }

        response = client.post("/debtor/add", json=payload, headers=auth_headers_admin)

        assert response.status_code == 400

    def test_create_debtor_requires_authentication(self, client):
        payload = {
            "name": "John Doe",
            "document": "123.456.789-09",
            "email": "johndoe@test.com",
            "phone": "11999999999",
        }

        response = client.post("/debtor/add", json=payload)

        assert response.status_code == 401

    def test_list_debtors_requires_authentication(self, client):
        response = client.get("/debtor/list")

        assert response.status_code == 401

    def test_retrieve_debtor_requires_authentication(self, client, debtor):
        response = client.get(f"/debtor/{debtor.id}/detail")

        assert response.status_code == 401
