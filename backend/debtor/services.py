from debtor.models import Debtor
from debtor.exceptions import DebtorNotFound, DuplicateDocumentDebtor


class DebtorService:

    @staticmethod
    def get(debtor_id, session):
        debtor = session.get(Debtor, debtor_id)

        if debtor is None:
            raise DebtorNotFound("Debtor not found")

        return debtor

    @staticmethod
    def create(data, session):
        existing_debtor = (
            session.query(Debtor)
            .filter_by(document=data['document'])
            .first()
        )

        if existing_debtor:
            raise DuplicateDocumentDebtor

        debtor = Debtor(**data)

        session.add(debtor)
        session.flush()

        return debtor
