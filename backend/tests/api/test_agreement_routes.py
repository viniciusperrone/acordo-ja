import pytest

from datetime import date, timedelta

from utils.enum import AgreementStatus


@pytest.mark.api
class TestAgreementRoutes:
    """
    API tests for agreement endpoints, covering creation,
    retrieval, listing, activation, cancellation, and completion
    flows with authentication and authorization rules.
    """

    def test_list_agreement_success(self, client, agreement, auth_headers_admin):
        response = client.get(
            "/agreement/list",
            headers=auth_headers_admin,
        )

        assert response.status_code == 200

        data = response.json

        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_list_agreement_requires_authentication(self, client):
        response = client.get("/agreement/list")

        assert response.status_code == 401

    def test_retrieve_agreement_success(self, client, agreement, auth_headers_admin):
        response = client.get(
            f"/agreement/{agreement.id}/detail",
            headers=auth_headers_admin,
        )

        assert response.status_code == 200
        assert response.json["id"] == str(agreement.id)

    def test_create_agreement_success(self, client, debt, auth_headers_admin):
        response = client.post(
            "/agreement/add",
            headers=auth_headers_admin,
            json={
                "debt_id": debt.id,
                "installments_quantity": 6,
                "first_due_date": (date.today() + timedelta(days=30)).isoformat(),
            }
        )

        assert response.status_code == 201

        agreement = response.get_json()

        assert agreement["debt_id"] == str(debt.id)

    def test_activate_agreement_success(self, client, agreement, auth_headers_admin, session):
        response = client.patch(
            f"/agreement/{agreement.id}/activate",
            headers=auth_headers_admin,
        )

        assert response.status_code == 204

        session.refresh(agreement)

        assert agreement.status == AgreementStatus.ACTIVE

    def test_cancel_agreement_success(self, client, agreement, auth_headers_admin, session):
        client.patch(
            f"/agreement/{agreement.id}/activate",
            headers=auth_headers_admin,
        )

        response = client.post(
            f"/agreement/{agreement.id}/cancel",
            headers=auth_headers_admin,
        )

        assert response.status_code == 204

        session.refresh(agreement)

        assert agreement.status == AgreementStatus.CANCELLED
