from creditor import Creditor
from debts import Debt
from debtor import Debtor

from creditor.exceptions import CreditorNotFound
from debtor.exceptions import DebtorNotFound
from debts.exceptions import DebtNotFound

from debts.history_service import DebtHistoryService


class DebtService:

    @staticmethod
    def get(debt_id, session):
        debt = session.get(Debt, debt_id)

        if debt is None:
            raise DebtNotFound

        return debt

    @staticmethod
    def create(data, user, session):
        creditor_id = data['creditor_id']

        existing_creditor = (
            session.query(Creditor)
            .filter_by(id=creditor_id)
            .first()
        )

        if not existing_creditor:
            raise CreditorNotFound

        debtor_id = data['debtor_id']

        existing_debtor = (
            session.query(Debtor)
            .filter_by(id=debtor_id)
            .first()
        )

        if not existing_debtor:
            raise DebtorNotFound

        debt = Debt(**data)

        session.add(debt)
        session.flush()

        DebtHistoryService.record_debt_created(debt, user, session)

        return debt
