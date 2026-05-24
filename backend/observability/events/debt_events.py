from observability.structured_logger import get_logger, bind_context, log_event


logger = get_logger("debt.events")

class DebtEventLogger:
    """
    Structured event logger for debt lifecycle events.

    Events:
        - debt_created
        - debt_entered_agreement
        - debt_cancelled
        - debt_paid
        - debt_overdue
        - debt_value_updated
    """

    @staticmethod
    def debt_created(debt_id: str, user_id: str, data: dict) -> None:
        bind_context(debt_id=debt_id, user_id=user_id)

        log_event(
            logger, "info", "debt.created",
            creditor_id=data['creditor_id'],
            debtor_id=data['debtor_id'],
            original_value=data["original_value"],
            due_date=data["due_date"],
        )

    @staticmethod
    def debt_entered_agreement(debt_id: str, user_id: str, data: dict) -> None:
        bind_context(debt_id=debt_id, user_id=user_id)

        log_event(
            logger, "info", "debt.entered_agreement",
            agreement_id=str(data['agreement_id']),
            old_status=data['old_status'],
            status=data['status'],
            updated_value=str(data['updated_value']),
            last_agreement_date=data["last_agreement_date"],
            agreement_status=data["agreement_status"],
        )

    @staticmethod
    def debt_cancelled(debt_id: str, user_id: str, reason: str) -> None:
        bind_context(debt_id=debt_id, user_id=user_id)

        log_event(
            logger, "warning", "debt.cancelled",
            reason=reason or "No reason provided"
        )

    @staticmethod
    def debt_paid(debt_id: str, user_id: str, data: dict) -> None:
        bind_context(debt_id=debt_id, user_id=user_id)

        log_event(
            logger, "info", "debt.paid",
            final_value=str(data["updated_value"]),
            agreement_id=str(data["agreement_id"]),
        )

    @staticmethod
    def debt_paid(debt_id: str, user_id: str, data: dict) -> None:
        bind_context(debt_id=debt_id, user_id=user_id)

        log_event(
            logger, "info", "debt.paid",
            final_value=str(data["updated_value"]),
            agreement_id=str(data["agreement_id"]),
        )

    @staticmethod
    def debt_value_updated(debt_id: str, user_id: str, old_value: str, new_value: str, reason: str) -> None:
        bind_context(debt_id=debt_id, user_id=user_id)

        log_event(
            logger, "info", "debt.value_updated",
            old_value=old_value,
            new_value=new_value,
            reason=reason
        )


debt_events = DebtEventLogger()
