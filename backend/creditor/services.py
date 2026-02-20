from creditor import Creditor
from creditor.exceptions import CreditorAlreadyExistsError


class CreditorService:

    @staticmethod
    def create_creditor(data, session):
        existing_creditor = (
            session.query(Creditor)
            .filter_by(bank_code=data['bank_code'])
            .first()
        )

        if existing_creditor:
            raise CreditorAlreadyExistsError(
                "Creditor already exists"
            )

        creditor = Creditor(**data)
        session.add(creditor)

        return creditor
