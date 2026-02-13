from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, NUMERIC

from config.db import db

from utils.choices import  INSTALLMENT_STATUS_CHOICES


class Installments(db.Model):
    __tablename__ = "installments"

    id = db.Column(db.Integer, primary_key=True)
    installment_number = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    payment_date = db.Column(db.Date)
    value = db.Column(NUMERIC(12, 2), nullable=False)

    status = db.Column(
        db.Enum(
            *[choice[0] for choice in INSTALLMENT_STATUS_CHOICES],
            name="installment_status_enum"
        ),
        nullable=False,
        default="PENDING"
    )

    agreement = db.relationship("Agreement", backref="installments")

    agreement_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("agreements.id"),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
