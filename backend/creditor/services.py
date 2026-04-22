from creditor import Creditor
from creditor.exceptions import CreditorAlreadyExistsError, CreditorNotFound


class CreditorService:

    @staticmethod
    def get(creditor_id, session):
        creditor = session.get(Creditor, creditor_id)

        if not creditor:
            raise CreditorNotFound

        return creditor


    @staticmethod
    def create_creditor(data, session):
        existing_creditor = (
            session.query(Creditor)
            .filter_by(bank_code=data['bank_code'])
            .first()
        )

        if existing_creditor:
            raise CreditorAlreadyExistsError("Creditor already exists")

        creditor = Creditor(**data)
        session.add(creditor)
        session.flush()

        return creditor
