from installments.models import Installments
from installments.exceptions import InstallmentNotFound


class InstallmentService:

    @staticmethod
    def get(installment_id, session):
        installment = session.get(Installments, installment_id)

        if not installment:
            raise InstallmentNotFound

        return installment
