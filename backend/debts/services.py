import hashlib

from creditor import Creditor
from debts import Debt
from debtor import Debtor

from creditor.exceptions import CreditorNotFound
from debtor.exceptions import DebtorNotFound
from debts.exceptions import DebtNotFound

from debts.history_service import DebtHistoryService
from observability.structured_logger import log_event
from observability.events.debt_events import logger, debt_events
from observability.tracing import traced


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
                'status': debt.status.value,
                'creditor': debt.creditor.bank_name,
            }

            total_amount += debt.original_value
            debts.append(item)

        log_event(
            logger,
            "info",
            "debt.search.performed",
            document_hash=hashlib.sha256(document.encode()).hexdigest(),
            has_debts=has_debts,
            total_debts=count
        )

        return dict(
            document=document,
            has_debts=count > 0,
            debts=debts,
            total_debts=count,
            total_amount=total_amount,
            redirect_url=redirect_url
        )

    @staticmethod
    @traced("debt.create")
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

        debt_events.debt_created(
            debt_id=str(debt.id),
            user_id=user.id,
            data={
                'creditor_id': str(creditor_id),
                'debtor_id': str(debtor_id),
                'original_value': str(debt.original_value),
                'due_date': debt.due_date.isoformat(),
            })

        return debt

    @staticmethod
    def get_timeline(debt: Debt, session):
        return DebtHistoryService.get_by_debt(debt.id, session)
