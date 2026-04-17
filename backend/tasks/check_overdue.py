from datetime import date
from sqlalchemy import and_

from config.db import db
from installments import Installments
from notifications.events import NotificationEvents
from utils.enum import InstallmentStatus


def check_overdue_installments():
    from flask import current_app

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
            current_app.logger.info(
                "No overdue installments found",
                extra={"checked_at": today.isoformat()}
            )

            return

        current_app.logger.info(
            "Processing overdue installments",
            extra={
                "total_found": count,
                "checked_at": today.isoformat()
            }
        )

        for installment in overdue_installments:
            old_status = installment.status
            installment.status = InstallmentStatus.OVERDUE

            NotificationEvents.on_installment_overdue(installment, db.session)

            current_app.logger.info(
                "Installment marked as overdue",
                extra={
                    "installment_id": installment.id,
                    "installment_number": installment.installment_number,
                    "agreement_id": str(installment.agreement_id),
                    "due_date": installment.due_date.isoformat(),
                    "value": float(installment.value),
                    "previous_status": old_status,
                    "new_status": installment.status.value
                }
            )

        current_app.logger.info(
            "Overdue installments processing completed",
            extra={
                "total_processed": count,
                "processed_at": today.isoformat()
            }
        )

        db.session.commit()


    except Exception as e:
        db.session.rollback()

        current_app.logger.exception(
            "Error processing overdue installments",
            extra={
                "checked_at": today.isoformat(),
                "error": str(e)
            }
        )

        raise

if __name__ == '__main__':
    from app import initialize_app

    app = initialize_app()

    with app.app_context():
        check_overdue_installments()