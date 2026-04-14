from utils.enum import NotificationType, UserRole
from notifications.services import NotificationService


class NotificationEvents:

    @staticmethod
    def on_lead_created(lead, session):
        ...

    @staticmethod
    def on_payment_received(payment, installment, session):
        ...

    @staticmethod
    def on_installment_overdue(installment, session):
        ...

    @staticmethod
    def on_agreement_created(agreement, session):
        ...

    @staticmethod
    def on_agreement_completed(agreement, session):
        ...

    @staticmethod
    def on_debt_paid(debt, session):
        ...
