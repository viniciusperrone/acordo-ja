import re
from marshmallow import ValidationError
from validate_docbr import CPF, CNPJ

from leads import Lead
from notifications.events import NotificationEvents


class LeadService:

    @staticmethod
    def validate_document(document):
        document = re.sub(r"\D", "", document)

        cpf = CPF()
        cnpj = CNPJ()

        is_valid_cpf = len(document) == 11 and cpf.validate(document)
        is_valid_cnpj = len(document) == 14 and cnpj.validate(document)

        if not (is_valid_cpf or is_valid_cnpj):
            raise ValidationError("CPF or CNPJ must be valid")

        return document

    @staticmethod
    def create(data, document, session):
        if not document:
            raise ValidationError('Lead must have a document')

        document = LeadService.validate_document(document)

        data = {**data, 'document': document}
        lead = Lead(**data)

        session.add(lead)
        session.flush()

        NotificationEvents.on_lead_created(lead, session)
        
        return lead
