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
    def search(document: str, session) -> dict:
        from utils.validators import validate_cnpj_or_cpf

        document = validate_cnpj_or_cpf(document)

        debts_query = (session.query(Debt)
                       .join(Debt.debtor)
                       .filter(Debt.debtor.has(document=document))
                       .order_by(Debt.created_at.desc()))

        total_amount = 0
        count = debts_query.count()
        has_debts = count > 0
        redirect_url = f"/leads/add?document={document}" if has_debts else None
        debts = []
        for debt in debts_query.all():
            item = {
                'id': debt.id,
                'amount': debt.original_value,
                'due_date': debt.due_date,
                'status': debt.status,
                'creditor': debt.creditor.bank_name,
            }

            total_amount += debt.original_value
            debts.append(item)

        return dict(
            document=document,
            has_debts=count > 0,
            debts=debts,
            total_debts=count,
            total_amount=total_amount,
            redirect_url=redirect_url
        )

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

    @staticmethod
    def get_timeline(debt: Debt, session):
        return DebtHistoryService.get_by_debt(debt.id, session)
