from config.db import db

from utils.choices import  INSTALLMENT_STATUS_CHOICES


class Installments(db.Model):
    __tablename__ = "installments"

    id = db.Column(db.Integer, primary_key=True)
    installment_number = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    payment_date = db.Column(db.Date)

    status = db.Column(
        db.Enum(
            *[choice[0] for choice in INSTALLMENT_STATUS_CHOICES],
            name="installment_status_enum"
        ),
        nullable=False,
        default="PENDING"
    )

