from observability.structured_logger import get_logger, bind_context, log_event


logger = get_logger("agreement.events")


class AgreementEventLogger:
    """Event logger for agreement lifecycle"""

    @staticmethod
    def agreement_created(agreement_id: str, user_id: str, data: dict) -> None:
        bind_context(agreement_id=agreement_id, user_id=user_id)

        log_event(
            logger, "info", "agreement.created",
            debt_id=str(data["debt_id"]),
            total_traded=str(data["total_traded"]),
            installments_quantity=data["installments_quantity"],
            discount_applied=str(data["discount_applied"]),
        )

    @staticmethod
    def agreement_activated(agreement_id: str, user_id) -> None:
        bind_context(agreement_id=agreement_id, user_id=user_id)

        log_event(logger, "info", "agreement.activated")

    @staticmethod
    def agreement_completed(agreement_id: str, user_id: str) -> None:
        bind_context(agreement_id=agreement_id, user_id=user_id)

        log_event(logger, "info", "agreement.completed")

    @staticmethod
    def agreement_cancelled(agreement_id: str, user_id: str, reason: str = None) -> None:
        bind_context(agreement_id=agreement_id, user_id=user_id)

        log_event(
            logger, "warning", "agreement.cancelled",
            reason=reason or "No reason provided"
        )


agreement_events = AgreementEventLogger()