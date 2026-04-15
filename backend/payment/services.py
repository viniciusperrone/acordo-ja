from datetime import datetime, date

from installments.exceptions import InstallmentWithoutAgreementError
from notifications.events import NotificationEvents
from payment.models import Payment
from payment.exception import PaymentError

from utils.enum import (
    InstallmentStatus,
    AgreementStatus,
    DebtStatus,
    MethodPayment
)


class PaymentService:

    @staticmethod
    def register_payment(installment, amount, method, session):

        if not installment.agreement:
            raise InstallmentWithoutAgreementError(
                f"Installment {installment.id} has no agreement associated"
            )

        if not isinstance(method, MethodPayment):
            raise PaymentError("Invalid payment method")

        if installment.status == InstallmentStatus.PAID:
            raise PaymentError("Installment already paid")

        if installment.agreement.status != AgreementStatus.ACTIVE:
            raise PaymentError(
                f"Cannot pay installment {installment.id} because agreement is not active"
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

        agreement = installment.agreement

        if all(i.status == InstallmentStatus.PAID for i in agreement.installments):
            agreement.status = AgreementStatus.COMPLETED

            agreement.debt.status = DebtStatus.PAID

        session.flush()

        NotificationEvents.on_payment_received(payment, installment, session)

        return payment
