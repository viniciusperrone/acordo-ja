import pytest

import uuid

from creditor.models import Creditor


@pytest.mark.api
class TestCreditorRoutes:
    """
    API tests for creditor endpoints.

    Covers creditor creation, retrieval, listing,
    authentication, authorization and validation scenarios.
    """

    def test_list_creditors_success(
        self,
        client,
        creditor,
        auth_headers_admin,
    ):
        response = client.get(
            "/creditors/list",
            headers=auth_headers_admin,
        )

        assert response.status_code == 200

        data = response.json

        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_retrieve_creditor_success(
        self,
        client,
        creditor,
        auth_headers_admin,
    ):
        response = client.get(
            f"/creditors/{creditor.id}/detail",
            headers=auth_headers_admin,
        )

        assert response.status_code == 200

        data = response.json

        assert data["id"] == str(creditor.id)
        assert data["bank_code"] == creditor.bank_code

    def test_retrieve_creditor_not_found(
        self,
        client,
        auth_headers_admin,
    ):
        response = client.get(
            f"/creditors/{uuid.uuid4()}/detail",
            headers=auth_headers_admin,
        )

        assert response.status_code == 404

    def test_create_creditor_success(
        self,
        client,
        auth_headers_admin,
    ):
        payload = {
            "bank_code": "341",
            "interest_rate": "0.10",
            "fine_rate": "0.05",
            "discount_limit": "5.00",
        }

        response = client.post(
            "/creditors/add",
            json=payload,
            headers=auth_headers_admin,
        )

        assert response.status_code == 201

        creditor = Creditor.query.filter_by(
            bank_code="341"
        ).first()

        assert creditor is not None
        assert creditor.bank_code == "341"

    def test_create_creditor_with_existing_bank_code_returns_error(
        self,
        client,
        creditor,
        auth_headers_admin,
    ):
        payload = {
            "bank_code": creditor.bank_code,
            "interest_rate": "0.10",
            "fine_rate": "0.05",
            "discount_limit": "5.00",
        }

        response = client.post(
            "/creditors/add",
            json=payload,
            headers=auth_headers_admin,
        )

        assert response.status_code == 400

    def test_create_creditor_requires_authentication(
        self,
        client,
    ):
        payload = {
            "bank_code": "341",
            "interest_rate": "0.10",
            "fine_rate": "0.05",
            "discount_limit": "5.00",
        }

        response = client.post(
            "/creditors/add",
            json=payload,
        )

        assert response.status_code == 401

    def test_list_creditors_requires_authentication(
        self,
        client,
    ):
        response = client.get("/creditors/list")

        assert response.status_code == 401

    def test_retrieve_creditor_requires_authentication(
        self,
        client,
        creditor,
    ):
        response = client.get(
            f"/creditors/{creditor.id}/detail"
        )

        assert response.status_code == 401
