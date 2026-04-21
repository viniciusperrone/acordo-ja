from datetime import datetime, date
from typing import Optional, Dict, Any
from decimal import Decimal

from .models import Debt, DebtHistory
from users.models import User
from utils.enum import DebtHistoryType, DebtStatus, AgreementStatus


class DebtHistoryService:

    @staticmethod
    def record_event(
        debt: Debt,
        event_type: DebtHistoryType,
        old_status: Optional[DebtStatus] = None,
        new_status: Optional[DebtStatus] = None,
        old_value: Optional[Decimal] = None,
        new_value: Optional[Decimal] = None,
        reason: str = "",
        extra: Optional[Dict[str, Any]] = None,
        session = None
    ) -> DebtHistory:

        history = DebtHistory(
            debt_id=debt.id,
            event_type=event_type,
            old_status=old_status,
            new_status=new_status,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            extra=extra,
            changed_at=datetime.utcnow(),
        )

        session.add(history)
        session.flush()

        return history

    @staticmethod
    def record_debt_created(debt: Debt, user: User, session) -> DebtHistory:
        extra = {
            "debtor_id": debt.debtor_id,
            "creditor_id": str(debt.creditor_id),
            "user": {
                "user_id": str(user.id),
                "name": user.name,
                "role": user.role.value,
            },
            "due_date": debt.due_date.isoformat(),
        }

        return DebtHistoryService.record_event(
            debt=debt,
            event_type=DebtHistoryType.DEBT_CREATED,
            new_status=DebtStatus.OPEN,
            reason=f"Dívida criada - Valor: R$ {debt.original_value}",
            extra=extra,
            session=session,
        )

    @staticmethod
    def record_agreement_activated(
            debt: Debt,
            agreement_id: str,
            old_status: DebtStatus,
            total_traded: Decimal,
            installments_quantity: int,
            user: User,
            session
    ) -> DebtHistory:
        return DebtHistoryService.record_event(
            debt=debt,
            event_type=DebtHistoryType.AGREEMENT_ACTIVATED,
            old_status=old_status,
            new_status=DebtStatus.IN_AGREEMENT,
            old_value=debt.original_value,
            new_value=total_traded,
            reason=f"Acordo criado - Valor: R$ {total_traded}",
            extra={
                "agreement_id": agreement_id,
                "installments_quantity": installments_quantity,
                "total_traded": str(total_traded),
                "user": {
                    "user_id": str(user.id),
                    "name": user.name,
                    "role": user.role.value,
                },
            },
            session=session
        )

    @staticmethod
    def record_agreement_cancelled(
            debt: Debt,
            agreement_id: str,
            debt_old_status: DebtStatus,
            agreement_new_status: AgreementStatus,
            agreement_old_status: AgreementStatus,
            session
    ) -> DebtHistory:
        old_value = debt.updated_value

        return DebtHistoryService.record_event(
            debt=debt,
            event_type=DebtHistoryType.AGREEMENT_CANCELLED,
            old_status=debt_old_status,
            new_status=DebtStatus.OPEN,
            old_value=old_value,
            new_value=None,
            reason=f"Acordo {agreement_id} cancelado",
            extra={
                "agreement_id": agreement_id,
                "agreement_new_status": agreement_new_status.value,
                "agreement_old_status": agreement_old_status.value,
            },
            session=session,
        )

    @staticmethod
    def record_debt_paid(
            debt: Debt,
            agreement_id: str,
            payment_id: str,
            paid_at: datetime,
            session
    ) -> DebtHistory:

        return DebtHistoryService.record_event(
            debt=debt,
            event_type=DebtHistoryType.DEBT_PAID,
            old_status=DebtStatus.IN_AGREEMENT,
            new_status=DebtStatus.PAID,
            old_value=debt.updated_value,
            new_value=debt.original_value,
            reason=f"Dívida quitada - Acordo {agreement_id} completo",
            extra={
                "agreement_id": agreement_id,
                "payment_id": payment_id,
                "paid_at": paid_at.isoformat(),
            },
            session=session,
        )

    @staticmethod
    def record_debt_cancelled(
        debt: Debt,
        cancellation_reason: str,
        session
    ) -> DebtHistory:

        return DebtHistoryService.record_event(
            debt=debt,
            event_type=DebtHistoryType.DEBT_CANCELLED,
            old_status=DebtStatus.OPEN,
            new_status=DebtStatus.CANCELLED,
            reason=f"Dívida cancelada",
            extra={
                "cancellation_reason": cancellation_reason,
            },
            session=session,
        )

    @staticmethod
    def record_debt_defaulted(
        debt: Debt,
        old_status: DebtStatus,
        due_date: date,
        session
    ) -> DebtHistory:

        return DebtHistoryService.record_event(
            debt=debt,
            event_type=DebtHistoryType.DEBT_DEFAULTED,
            old_status=old_status,
            new_status=DebtStatus.DEFAULTED,
            reason=f"Dívida entrou em Inadimplência",
            extra={
                "due_date": due_date.isoformat(),
            },
            session=session
        )

    @staticmethod
    def get_debt_timeline(debt_id: str, event_type: Optional[DebtHistoryType] = None) -> list:
        query = DebtHistory.query.filter_by(debt_id=debt_id)

        if event_type:
            query = query.filter_by(event_type=event_type)

        return query.order_by(DebtHistory.changed_at.desc()).all()

    @staticmethod
    def get_statistics(debt_id: str) -> Dict[str, Any]:
        history = DebtHistory.query.filter_by(debt_id=debt_id).all()

        stats = {
            "total_events": len(history),
            "renegotiations": 0,
            "status_changes": 0,
            "value_changes": 0,
            "events_by_type": {}
        }

        for event in history:
            event_type_str = event.event_type.value
            stats["events_by_type"][event_type_str] = \
                stats["events_by_type"].get(event_type_str, 0) + 1

            if event.event_type == DebtHistoryType.AGREEMENT_CREATED:
                stats["renegotiations"] += 1

            if event.old_status and event.new_status:
                stats["status_changes"] += 1

            if event.old_value is not None or event.new_value is not None:
                stats["value_changes"] += 1

        return stats
