from observability.structured_logger import get_logger, bind_context, log_event


logger = get_logger("debt.events")

class DebtEventLogger:
    """
        Structured event logger for debt lifecycle events.

        Events:
            - debt_created
            - agreement_activated
            - debt_cancelled
            - debt_paid
            - debt_overdue
    """

    def debt_created(self, debt_id: str, user_id: str, data: dict) -> None:
        bind_context(debt_id=debt_id, user_id=user_id)

        log_event(logger, "info", "debt.debt_created",
            creditor_id=data['creditor_id'],
            debtor_id=data['debtor_id'],
            original_value=data["original_value"],
            due_date=data["due_date"],
        )

    def debt_entered_agreement(self, debt_id: str, user_id: str, data: dict) -> None:
        bind_context(debt_id=debt_id, user_id=user_id)

        log_event(logger, "info", "debt.entered_agreement",
            agreement_id=data['agreement_id'],
            old_status=data['old_status'],
            status=data['status'],
            updated_value=data['updated_value'],
            last_agreement_date=data["last_agreement_date"],
            agreement_status=data["agreement_status"],
        )

    def debt_cancelled(self, debt_id: str, user_id: str, data: dict) -> None:
        bind_context(debt_id=debt_id, user_id=user_id)



