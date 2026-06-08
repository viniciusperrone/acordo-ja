import pytest

import uuid
import random
from decimal import Decimal
from datetime import timedelta, date

from debts.models import Debt


@pytest.mark.api
class TestDebtRoutes:
    """
    API tests for debt endpoints.

    Cover debt creation, retrieval, listing, document search,
    and timeline access through HTTP routes.
    """

    def test_create_debt_success(self, client, debtor, creditor, auth_headers_admin):
        payload = {
            "debtor_id": debtor.id,
            "creditor_id": str(creditor.id),
            "original_value": "1500.00",
            "due_date": (date.today() + timedelta(days=30)).isoformat(),
        }

        response = client.post(
            "/debts/add",
            headers=auth_headers_admin,
            json=payload
        )

        assert response.status_code == 201

        debt = Debt.query.filter_by(
            debtor_id=debtor.id,
            creditor_id=creditor.id,
        ).first()

        assert debt is not None
        assert debt.original_value == Decimal("1500.00")

    def test_create_debt_with_invalid_creditor(self, client, creditor, auth_headers_admin):
        payload = {
            "debtor_id": random.randint(1, 100),
            "creditor_id": str(creditor.id),
            "original_value": "1500.00",
            "due_date": (date.today() + timedelta(days=30)).isoformat(),
        }

        response = client.post(
            "/debts/add",
            headers=auth_headers_admin,
            json=payload
        )

        assert response.status_code == 404

    def test_create_debt_with_invalid_debtor(self):
        payload = {
            "debtor_id": '',
            "creditor_id": str(uuid.uuid4()),
            "original_value": "1500.00",
            "due_date": (date.today() + timedelta(days=30)).isoformat(),
        }

        response = client.post(
            "/debts/add",
            headers=auth_headers_admin,
            json=payload
        )

        assert response.status_code == 404

    def test_retrieve_debt_success(self, client, debt, auth_headers_admin):
        response = client.get(
            f"/debts/{debt.id}/detail",
            headers=auth_headers_admin
        )

        assert response.status_code == 200

        data = response.json

        assert data["id"] == str(debt.id)

    def test_retrieve_debt_not_found(self, client, auth_headers_admin):
        response = client.get(
            f"/debts/{uuid.uuid4()}/detail",
            headers=auth_headers_admin
        )

        assert response.status_code == 404

    def test_list_debts_success(self, client, debt, auth_headers_admin):
        response = client.get(
            "/debts/list",
            headers=auth_headers_admin
        )

        assert response.status_code == 200

        data = response.json

        assert "items" in data
        assert data["total"] >= 1

    def test_search_debt_by_document_success(self, client, debt, debtor):
        response = client.get(
            f"/debts/search?document={debtor.document}"
        )

        assert response.status_code == 200

        data = response.get_json()

        assert data["has_debts"] is True
        assert data["total_debts"] >= 1

    def test_search_debt_by_document_without_results(self, client):
        response = client.get(
            "/debts/search?document=52998224725"
        )

        assert response.status_code == 200

        data = response.get_json()

        assert data["has_debts"] is False
        assert data["total_debts"] == 0

    def test_get_debt_timeline_success(self, client, debt, auth_headers_admin):
        response = client.get(
            f"/debts/{debt.id}/timeline",
            headers=auth_headers_admin,
        )

        assert response.status_code == 200

        data = response.json

        assert "items" in data
        assert "total" in data

    def test_get_debt_timeline_not_found(self, client, auth_headers_admin):
        debt_id = uuid.uuid4()

        response = client.get(
            f"/debts/{debt_id}/timeline",
            headers=auth_headers_admin
        )

        assert response.status_code == 404
