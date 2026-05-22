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
