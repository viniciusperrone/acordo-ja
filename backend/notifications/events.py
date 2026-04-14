from sqlalchemy.sql import roles

from utils.enum import NotificationType, UserRole
from notifications.services import NotificationService


class NotificationEvents:

    @staticmethod
    def on_lead_created(lead, session):
        NotificationService.create_notification_for_roles(
            type=NotificationType.NEW_LEAD,
            title="Novo Lead Criado! 🎯",
            message=f"Um novo lead foi registrado: {lead.name} (CPF/CNPJ): {lead.document}",
            extra={
                "lead_id": lead.id,
                "lead_name": lead.name,
                "lead_document": lead.document,
                "lead_email": lead.email,
                "lead_phone": lead.phone
            },
            roles=[UserRole.ADMIN, UserRole.MANAGER, UserRole.AGENT],
            session=session
        )


    @staticmethod
    def on_payment_received(payment, installment, session):
        NotificationEvents.create_notification_for_roles(
            type=NotificationType.PAYMENT_RECEIVED,
            title="Pagamento Recebido 💰",
            message=f"Pagamento R$ {payment.amount} recebido para parcela #{installment.installment_number}",
            extra={
                "payment_id": str(payment.id),
                "installment_id": installment.id,
                "amount": str(payment.amount),
                "method": payment.method.value
            },
            roles=[UserRole.ADMIN, UserRole.MANAGER],
            session=session
        )

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
