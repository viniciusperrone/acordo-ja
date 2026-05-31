from observability.structured_logger import get_logger, bind_context, log_event


logger = get_logger("payments.events")


class PaymentEventLogger:
    """Event logger for payment operations"""

    @staticmethod
    def payment_received(payment_id: str, user_id: str, data: dict) -> None:
        bind_context(payment_id=payment_id, user_id=user_id)

        log_event(
            logger, "info", "payment.received",
            installment_id=data["installment_id"],
            amount=str(data["amount"]),
            method=data["method"],
            agreement_id=str(data["agreement_id"]),
        )

    @staticmethod
    def payment_failed(installment_id: int, user_id: str, reason: str) -> None:
        bind_context(installment_id=installment_id, user_id=user_id)

        log_event(
            logger, "error", "payment.failed",
            reason=reason,
        )


payments_events = PaymentEventLogger()
