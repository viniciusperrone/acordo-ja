from datetime import datetime, date

from installments.exceptions import InstallmentWithoutAgreement
from notifications.events import NotificationEvents
from observability.events.payment_events import payments_events
from observability.events.agreement_events import agreement_events
from observability.events.debt_events import debt_events
from observability.tracing import traced
from payment.models import Payment
from payment.exception import PaymentError
from debts.history_service import DebtHistoryService

from utils.enum import (
    InstallmentStatus,
    AgreementStatus,
    DebtStatus,
    MethodPayment
)


class PaymentService:

    @staticmethod
    @traced("payment.register")
    def process_installment_payment(
        installment,
        user,
        amount,
        method,
        session
    ):

        if not installment.agreement:
            raise InstallmentWithoutAgreement(
                f"Installment {installment.id} has no agreement associated"
            )

        if not isinstance(method, MethodPayment):
            raise PaymentError("Invalid payment method")

        if installment.status == InstallmentStatus.PAID:
            raise PaymentError("Installment already paid")

        if installment.agreement.status != AgreementStatus.ACTIVE:
            raise PaymentError(
                f"Cannot pay installment {installment.id} "
                f"because agreement is not active"
            )

        if amount != installment.value:
            raise PaymentError("Payment must match installment value")

        payment = Payment(
            installment=installment,
            amount=amount,
            paid_at=datetime.utcnow(),
            method=method,
        )

        installment.status = InstallmentStatus.PAID
        installment.payment_date = date.today()

        session.add(payment)
        session.flush()

        agreement = installment.agreement

        payments_events.payment_received(
            payment_id=str(payment.id),
            data={
                'installment_id': installment.id,
                'amount': payment.amount,
                'method': payment.method.value,
                'agreement_id': agreement.id,
            }
        )

        if all(i.status == InstallmentStatus.PAID for i in agreement.installments):
            agreement.status = AgreementStatus.COMPLETED

            NotificationEvents.on_agreement_completed(agreement, session)

            agreement_events.agreement_completed(
                agreement_id=str(agreement.id),
                user_id=str(user.id),
            )

            agreement.debt.status = DebtStatus.PAID

            debt_events.debt_paid(
                debt_id=str(agreement.debt.id),
                user_id=str(user.id),
                data={
                    'updated_value': agreement.debt.updated_value,
                    'agreement_id': agreement.id,
                }
            )

            NotificationEvents.on_debt_paid(agreement.debt, session)

            DebtHistoryService.record_debt_paid(
                debt=agreement.debt,
                agreement_id=str(agreement.id),
                payment_id=str(payment.id),
                paid_at=payment.paid_at,
                session=session
            )

        session.flush()

        NotificationEvents.on_payment_received(payment, installment, session)

        return payment
 