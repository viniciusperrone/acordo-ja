import pytest

from installments.models import Installments
from payment.services import PaymentService

from utils.enum import InstallmentStatus, AgreementStatus, MethodPayment


@pytest.mark.api
class TestPaymentRoutes:
    """
    Test suite for payment API endpoints.

    Covers payments listing operations, authentication requirements,
    pagination responses, and payment retrieval scenarios.
    """

    def test_list_payments_success(self, client, session, agreement, agent_user, auth_headers_admin):
        installment = Installments(
            installment_number=1,
            due_date=agreement.first_due_date,
            value=agreement.installment_value,
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        session.add(installment)

        agreement.status = AgreementStatus.ACTIVE
        session.commit()

        PaymentService.process_installment_payment(
            installment=agreement.installments[0],
            user=agent_user,
            amount=agreement.installments[0].value,
            method=MethodPayment.PIX,
            session=session,
        )

        session.commit()

        response = client.get(
            "/payment/list",
            headers=auth_headers_admin,
        )

        assert response.status_code == 200

        data = response.json

        assert "items" in data
        assert "total" in data
        assert "pages" in data
        assert "current_page" in data

        assert data["total"] == 1
        assert len(data["items"]) == 1

    def test_list_payments_requires_authentication(self, client):
        response = client.get("/payment/list")

        assert response.status_code == 401

    def test_list_payments_returns_empty_result(self, client, auth_headers_admin):
        response = client.get(
            "/payment/list",
            headers=auth_headers_admin,
        )

        assert response.status_code == 200

        data = response.json

        assert data["items"] == []
        assert data["total"] == 0

    def test_list_payments_supports_pagination(self, client, agreement, agent_user, session, auth_headers_admin):
        installment = Installments(
            installment_number=1,
            due_date=agreement.first_due_date,
            value=agreement.installment_value,
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        session.add(installment)

        agreement.status = AgreementStatus.ACTIVE
        session.commit()

        PaymentService.process_installment_payment(
            installment=agreement.installments[0],
            user=agent_user,
            amount=agreement.installments[0].value,
            method=MethodPayment.PIX,
            session=session,
        )

        session.commit()

        response = client.get(
            "/payment/list?page=1&per_page=1",
            headers=auth_headers_admin,
        )

        assert response.status_code == 200

        data = response.json

        assert data["current_page"] == 1
        assert len(data["items"]) <= 1
