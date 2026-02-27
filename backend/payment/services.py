from datetime import datetime

from payment.models import Payment
from payment.exception import PaymentError

from utils.enum import InstallmentStatus, AgreementStatus, DebtStatus


class PaymentService:

    @staticmethod
    def register_payment(installment, amount, method, session):

        if installment.status == InstallmentStatus.PAID:
            raise PaymentError("Installment already paid")

        if installment.agreement.status != AgreementStatus.ACTIVE:
            raise PaymentError("Agreement is not active")

        if amount != installment.amount:
            raise PaymentError("Payment must match installment value")

        payment = Payment(
            installment=installment,
            amount=amount,
            paid_at=datetime.utcnow(),
            method=method,
        )

        session.add(payment)

        agreement = installment.agreement

        if all(i.status == InstallmentStatus.PAID for i in agreement.installments):
            agreement.status = AgreementStatus.COMPLETED

            agreement.debt.status = DebtStatus.PAID

        session.commit()

        return payment
