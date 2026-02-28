from installments import Installments
from .exceptions import InstallmentNotFoundError


class InstallmentService:

    @staticmethod
    def get_installment_or_fail(installment_id):
        installment = Installments.query.get(installment_id)

        if not installment:
            raise InstallmentNotFoundError("Installment not found")

        return installment
