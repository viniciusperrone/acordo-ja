from datetime import date
from sqlalchemy import and_

from config.db import db
from installments import Installments
from notifications.events import NotificationEvents
from utils.enum import InstallmentStatus


def check_overdue_installments():
    try:
        overdue_installments = Installments.query.filter(
            and_(
                Installments.status == InstallmentStatus.PENDING,
                Installments.due_date < date.today
            )
        ).all()

        count = len(overdue_installments)

        if count == 0:
            return

        for installment in overdue_installments:
            installment.status = InstallmentStatus.OVERDUE

            NotificationEvents.on_installment_overdue(installment, db.session)

        db.session.commit()


    except Exception as e:
        db.session.rollback()

        raise

if __name__ == '__main__':
    from app import initialize_app

    app = initialize_app()

    with app.app_context():
        check_overdue_installments()