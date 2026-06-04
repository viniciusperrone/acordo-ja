import pytest

from datetime import timedelta, date

from agreement.services import AgreementService
from payment.exception import PaymentError
from payment.services import PaymentService
from utils.enum import MethodPayment, InstallmentStatus, AgreementStatus, DebtStatus


@pytest.mark.integration
@pytest.mark.db
class TestPaymentFlow:
    """
    Validate the payment lifecycle, including installment settlement,
    agreement completion, and debt payoff scenarios.
    """

    def test_should_pay_single_installment(self, debt, agent_user, session):
        agreement = AgreementService.create(
            {
                "debt_id": debt.id,
                "installments_quantity": 2,
                "first_due_date": date.today() + timedelta(days=30),
            },
            agent_user,
            session
        )

        AgreementService.activate(agreement, agent_user, session)

        installment = agreement.installments[0]

        payment = PaymentService.process_installment_payment(
            installment=installment,
            user=agent_user,
            amount=installment.value,
            method=MethodPayment.PIX,
            session=session
        )

        session.commit()

        session.refresh(installment)
        session.refresh(agreement)
        session.refresh(debt)

        assert payment.id is not None
        assert installment.status == InstallmentStatus.PAID
        assert installment.payment_date is not None
        assert agreement.status == AgreementStatus.ACTIVE
        assert debt.status == DebtStatus.IN_AGREEMENT

    def test_should_complete_agreement_after_last_installment_payment(self, debt, agent_user, session):
        agreement = AgreementService.create(
            {
                "debt_id": debt.id,
                "installments_quantity": 2,
                "first_due_date": date.today() + timedelta(days=30),
            },
            agent_user,
            session
        )

        AgreementService.activate(agreement, agent_user, session)

        for installment in agreement.installments:
            PaymentService.process_installment_payment(
                installment=installment,
                user=agent_user,
                amount=installment.value,
                method=MethodPayment.PIX,
                session=session
            )

        session.commit()

        session.refresh(agreement)
        session.refresh(debt)

        assert agreement.status == AgreementStatus.COMPLETED
        assert debt.status == DebtStatus.PAID

    def test_should_not_pay_installment_when_agreement_is_draft(self, debt, agent_user, session):
        agreement = AgreementService.create(
            {
                "debt_id": debt.id,
                "installments_quantity": 2,
                "first_due_date": date.today() + timedelta(days=30),
            },
            agent_user,
            session
        )

        installment = agreement.installments[0]

        with pytest.raises(PaymentError):
            PaymentService.process_installment_payment(
                installment=installment,
                user=agent_user,
                amount=installment.value,
                method=MethodPayment.PIX,
                session=session,
            )

    def test_should_not_pay_installment_twice(self, debt, agent_user, session):
        agreement = AgreementService.create(
            {
                "debt_id": debt.id,
                "installments_quantity": 1,
                "first_due_date": date.today() + timedelta(days=30),
            },
            agent_user,
            session,
        )

        AgreementService.activate(
            agreement,
            agent_user,
            session,
        )

        installment = agreement.installments[0]

        PaymentService.process_installment_payment(
            installment=installment,
            user=agent_user,
            amount=installment.value,
            method=MethodPayment.PIX,
            session=session,
        )

        with pytest.raises(PaymentError):
            PaymentService.process_installment_payment(
                installment=installment,
                user=agent_user,
                amount=installment.value,
                method=MethodPayment.PIX,
                session=session,
            )
