from marshmallow import ValidationError

from leads import Lead
from notifications.events import NotificationEvents


class LeadService:

    @staticmethod
    def create(data, document, session):
        from utils.validators import validate_cnpj_or_cpf

        if not document:
            raise ValidationError('Lead must have a document')

        document = validate_cnpj_or_cpf(document)

        data = {**data, 'document': document}
        lead = Lead(**data)

        session.add(lead)
        session.flush()

        NotificationEvents.on_lead_created(lead, session)
        
        return lead
