from utils.enum import NotificationType, UserRole
from notifications.services import NotificationService


class NotificationEvents:

    @staticmethod
    def on_lead_created(lead, session):
        NotificationService.create_notification_for_roles(
            notification_type=NotificationType.NEW_LEAD,
            title="Novo Lead Criado! 🎯",
            message=f"Um novo lead foi registrado: {lead.name} (CPF/CNPJ): {lead.document}",
            extra={
                "lead_id": str(lead.id),
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
        NotificationService.create_notification_for_roles(
            notification_type=NotificationType.PAYMENT_RECEIVED,
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
        NotificationService.create_notification_for_roles(
            notification_type=NotificationType.INSTALLMENT_OVERDUE,
            title="Parcela Vencida ⚠️",
            message=f"A parcela #{installment.installment_number} está vencida desde {installment.due_date}",
            extra={
                "installment_id": installment.id,
                "installment_number": installment.installment_number,
                "due_date": installment.due_date.isoformat(),
                "value": str(installment.value),
                "agreement_id": str(installment.agreement_id)
            },
            roles=[UserRole.ADMIN, UserRole.MANAGER, UserRole.AGENT],
            session=session
        )

    @staticmethod
    def on_agreement_created(agreement, session):
        NotificationService.create_notification_for_roles(
            notification_type=NotificationType.AGREEMENT_CREATED,
            title="Novo Acordo Criado ✅",
            message=f"Um novo acordo foi criado no valor de R$ {agreement.total_traded} em {agreement.installments_quantity}x",
            metadata={
                "agreement_id": str(agreement.id),
                "total_traded": str(agreement.total_traded),
                "installments_quantity": agreement.installments_quantity,
                "debt_id": str(agreement.debt_id)
            },
            roles=[UserRole.ADMIN, UserRole.MANAGER],
            session=session
        )

    @staticmethod
    def on_agreement_completed(agreement, session):
        NotificationService.create_notification_for_roles(
            notification_type=NotificationType.AGREEMENT_COMPLETED,
            title="Acordo Finalizado 🎉",
            message=f"O acordo de R$ {agreement.total_traded} foi completamente quitado!",
            metadata={
                "agreement_id": str(agreement.id),
                "total_traded": str(agreement.total_traded),
                "debt_id": str(agreement.debt_id)
            },
            roles=[UserRole.ADMIN, UserRole.MANAGER],
            session=session
        )

    @staticmethod
    def on_debt_paid(debt, session):
        NotificationService.create_notification_for_roles(
            notification_type=NotificationType.DEBT_PAID,
            title="Dívida Quitada 🎊",
            message=f"A dívida de R$ {debt.updated_value} foi totalmente paga!",
            metadata={
                "debt_id": str(debt.id),
                "debtor_id": debt.debtor_id,
                "original_value": str(debt.original_value),
                "updated_value": str(debt.updated_value)
            },
            roles=[UserRole.ADMIN, UserRole.MANAGER],
            session=session
        )
