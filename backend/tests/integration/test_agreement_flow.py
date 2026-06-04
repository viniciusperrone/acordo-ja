import pytest

from datetime import date, timedelta

from agreement.models import Agreement
from debts.models import Debt
from agreement.services import AgreementService
from payment.services import PaymentService

from installments.models import Installments

from utils.enum import (
    DebtStatus, AgreementStatus,
    MethodPayment, InstallmentStatus
)


@pytest.mark.integration
@pytest.mark.db
class TestAgreementFlow:

    def test_create_agreement_should_be_draft(self, debt, agent_user, session):
        data = {
            "debt_id": debt.id,
            "installments_quantity": 6,
            "first_due_date": date.today() + timedelta(days=30)
        }

        assert debt.status == DebtStatus.OPEN
        assert debt.renegotiation_count == 0

        agreement = AgreementService.create(data, agent_user, session)

        session.refresh(debt)

        assert debt.renegotiation_count == 1
        assert agreement.status == AgreementStatus.DRAFT

    def test_activate_agreement_updates_debt(self, agreement, debt, agent_user, session): # noqa: E501, E261
        AgreementService.activate(agreement, agent_user, session)

        session.refresh(agreement)
        session.refresh(debt)

        assert agreement.status == AgreementStatus.ACTIVE

        assert debt.status == DebtStatus.IN_AGREEMENT
        assert debt.updated_value == agreement.total_traded
        assert debt.last_agreement_date is not None

    def test_cancel_agreement_revert_debt(self, agreement, debt, agent_user, session):
        AgreementService.activate(agreement, agent_user, session)

        AgreementService.cancel(agreement, agent_user, session)

        session.refresh(agreement)
        session.refresh(debt)

        assert agreement.status == AgreementStatus.CANCELLED
        assert debt.status == DebtStatus.OPEN
        assert debt.updated_value is None

    def test_full_agreement_lifecycle(self, debt, agent_user, session):
        data = {
            "debt_id": debt.id,
            "installments_quantity": 6,
            "first_due_date": date.today() + timedelta(days=30)
        }

        agreement = AgreementService.create(data, agent_user, session)

        AgreementService.activate(agreement, agent_user, session)
        AgreementService.cancel(agreement, agent_user, session)

        session.refresh(debt)
        session.refresh(debt)

        assert agreement.status == AgreementStatus.CANCELLED
        assert debt.status == DebtStatus.OPEN

    def test_should_complete_agreement_and_pay_debt_when_all_installments_are_paid(
        self,
        debt,
        agent_user,
        session
    ):
        agreement = AgreementService.create(
            {
                "debt_id": debt.id,
                "installments_quantity": 2,
                "first_due_date": date.today() + timedelta(days=30)
            },
            agent_user,
            session
        )

        AgreementService.activate(
            agreement,
            agent_user,
            session,
        )

        installments = (
            session.query(Installments)
            .filter_by(agreement_id=agreement.id)
            .all()
        )

        for installment in installments:
            PaymentService.process_installment_payment(
                installment=installment,
                user=agent_user,
                amount=installment.value,
                method=MethodPayment.PIX,
                session=session,
            )

        session.commit()

        agreement = session.get(Agreement, agreement.id)
        debt = session.get(Debt, debt.id)

        assert all(
            installment.status == InstallmentStatus.PAID
            for installment in installments
        )

        assert agreement.status == AgreementStatus.COMPLETED
        assert debt.status == DebtStatus.PAID
