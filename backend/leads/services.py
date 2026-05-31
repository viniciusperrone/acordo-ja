from leads import Lead
from notifications.events import NotificationEvents


class LeadService:

    @staticmethod
    def create(data, session):
        lead = Lead(**data)

        session.add(lead)
        session.flush()

        NotificationEvents.on_lead_created(lead, session)

        return lead
