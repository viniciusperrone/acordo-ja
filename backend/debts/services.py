from creditor import Creditor
from debts import Debt
from debtor import Debtor

from .exceptions import CreditorNotExistError, DebtorNotExistError


class DebtService:

    @staticmethod
    def create_debt(data, session):
        creditor_id = data['creditor_id']

        existing_creditor = (
            session.query(Creditor)
            .filter_by(id=creditor_id)
            .first()
        )

        if not existing_creditor:
            raise CreditorNotExistError("Creditor not found")

        debtor_id = data['debtor_id']

        existing_debtor = (
            session.query(Debtor)
            .filter_by(id=debtor_id)
            .first()
        )

        if not existing_debtor:
            raise DebtorNotExistError("Debtor not found")

        debt = Debt(**data)
        session.add(debt)

        return debt
