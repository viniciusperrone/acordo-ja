from installments import Installments
from utils.enum import AgreementStatus, InstallmentStatus
from .exceptions import InstallmentNotFoundError, InstallmentWithoutAgreementError, InstallmentError


class InstallmentService:

    @staticmethod
    def get_installment_or_fail(installment_id):
        installment = Installments.query.get(installment_id)

        if not installment:
            raise InstallmentNotFoundError("Installment not found")

        return installment


    @staticmethod
    def paid_installment(installment: Installments, session):
        agreement = installment.agreement

        if not agreement:
            raise InstallmentWithoutAgreementError(
                f"Installment {installment.id} has no agreement associated"
            )

        if agreement.status != AgreementStatus.ACTIVE:
            raise InstallmentError(
                f"Cannot pay installment {installment.id} because agreement "
                f"{agreement.id} is not active (status={agreement.status.name})"
            )

        if installment.status == InstallmentStatus.PAID:
            raise InstallmentError(f"Installment {installment.id} is already paid")

        installment.status = InstallmentStatus.PAID
        session.commit()

        return installment


    @staticmethod
    def cancel_installment(installment: Installments, session):
        agreement = installment.agreement

        if not agreement:
            raise InstallmentWithoutAgreementError(
                f"Installment {installment.id} has no agreement associated"
            )