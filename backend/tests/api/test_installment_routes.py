import pytest

import random

from installments.models import Installments
from payment.models import Payment

from utils.enum import AgreementStatus, InstallmentStatus


@pytest.mark.api
class TestInstallmentRoutes:
    """
    API tests for installment endpoints, covering listing,
    payment processing, authentication requirements,
    and installment state transitions.
    """

    def test_list_installments_success(self, client, agreement, auth_headers_admin):
        response = client.get("/installments/list", headers=auth_headers_admin)

        assert response.status_code == 200

        data = response.json

        assert "items" in data
        assert "total" in data

    def test_list_installments_requires_authentication(self, client):
        response = client.get("/installments/list")

        assert response.status_code == 401

    def test_pay_installment_success(self, client, agreement, auth_headers_admin, session):
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

        found_installment = (
            session.query(Installments)
            .filter_by(agreement_id=agreement.id)
            .first()
        )

        response = client.post(
            f"/installments/{found_installment.id}/pay",
            headers=auth_headers_admin,
            json={
                "amount": str(installment.value),
                "method": "PIX"
            }
        )

        assert response.status_code == 201

        session.refresh(installment)

        payment = (
            session.query(Payment)
            .filter_by(installment_id=installment.id)
            .first()
        )

        assert payment is not None
        assert installment.status == InstallmentStatus.PAID

    def test_pay_installment_requires_authentication(self, client, agreement, session):
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

        response = client.post(
            f"/installments/{installment.id}/pay",
            json={
                "amount": str(installment.value),
                "method": "PIX",
            },
        )

        assert response.status_code == 401

    def test_pay_installment_not_found(self, client, auth_headers_admin):
        response = client.post(
            f"/installments/{random.randint(1, 1000)}/pay",
            headers=auth_headers_admin,
            json={
                "amount": "100.00",
                "method": "PIX",
            },
        )

        assert response.status_code == 404

    def test_pay_installment_cannot_pay_twice(self, client, agreement, session, auth_headers_admin):
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

        client.post(
            f"/installments/{installment.id}/pay",
            headers=auth_headers_admin,
            json={
                "amount": str(installment.value),
                "method": "PIX",
            }
        )

        response = client.post(
            f"/installments/{installment.id}/pay",
            headers=auth_headers_admin,
            json={
                "amount": str(installment.value),
                "method": "PIX",
            },
        )

        assert response.status_code == 400

    def test_pay_installment_with_inactive_agreement(self, client, agreement, auth_headers_admin, session):
        installment = Installments(
            installment_number=1,
            due_date=agreement.first_due_date,
            value=agreement.installment_value,
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        session.add(installment)
        session.commit()

        response = client.post(
            f"/installments/{installment.id}/pay",
            headers=auth_headers_admin,
            json={
                "amount": str(installment.value),
                "method": "PIX",
            },
        )

        assert response.status_code == 400
