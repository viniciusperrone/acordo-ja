from marshmallow import ValidationError

from leads import Lead


class LeadService:

    @staticmethod
    def create(data, document, session):
        if not document:
            raise ValidationError('Lead must have a document')

        data = {**data, 'document': document}
        lead = Lead(**data)

        session.add(lead)

        return lead
