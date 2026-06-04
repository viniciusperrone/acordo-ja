from datetime import date

from sqlalchemy import and_

from config.db import db
from installments import Installments
from notifications.events import NotificationEvents
from observability.tracing import traced
from observability.structured_logger import get_logger, log_event
from utils.enum import InstallmentStatus


logger = get_logger("tasks.scheduler.overdue_installments")

@traced("tasks.scheduler.check_overdue_installments")
def check_overdue_installments():
    today = date.today()

    try:
        overdue_installments = Installments.query.filter(
            and_(
                Installments.status == InstallmentStatus.PENDING,
                Installments.due_date < date.today()
            )
        ).all()

        count = len(overdue_installments)

        if count == 0:
            log_event(
                logger,
                "info",
                "tasks.scheduler.no_overdue_installments",
                extra_fields={
                    "message": "No overdue installments found",
                    "total_found": count,
                    "checked_at": today.isoformat()
                }
            )

            return

        log_event(
            logger,
            "info",
            "tasks.scheduler.processing_overdue_installments",
            extra_fields={
                "message": "Processing overdue installments",
                "total_found": count,
                "checked_at": today.isoformat()
            }
        )

        for installment in overdue_installments:
            old_status = installment.status
            installment.status = InstallmentStatus.OVERDUE

            NotificationEvents.on_installment_overdue(installment, db.session)

            log_event(
                logger,
                "info",
                "tasks.scheduler.installment_marked_overdue",
                extra_fields={
                    "message": "Installment marked as overdue",
                    "installment_id": installment.id,
                    "installment_number": installment.installment_number,
                    "agreement_id": str(installment.agreement_id),
                    "due_date": installment.due_date.isoformat(),
                    "value": float(installment.value),
                    "previous_status": old_status,
                    "new_status": installment.status.value
                }
            )

        log_event(
            logger,
            "info",
            "tasks.scheduler.overdue_installments_processed",
            extra_fields={
                "message": "Overdue installments processing completed",
                "total_processed": count,
                "processed_at": today.isoformat()
            }
        )

        db.session.commit()

    except Exception as e:
        db.session.rollback()

        raise


if __name__ == '__main__':
    from app import initialize_app

    app = initialize_app()

    with app.app_context():
        check_overdue_installments()
