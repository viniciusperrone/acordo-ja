from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, NUMERIC

from config.db import db
from utils.enum import InstallmentStatus


class Installments(db.Model):
    __tablename__ = "installments"

    id = db.Column(db.Integer, primary_key=True)
    installment_number = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    payment_date = db.Column(db.Date)
    value = db.Column(NUMERIC(12, 2), nullable=False)

    status = db.Column(
       db.Enum(
           InstallmentStatus,
           name="installment_status_enum"
       ),
       default=InstallmentStatus.PENDING,
       server_default=InstallmentStatus.PENDING.value,
       nullable=False
    )

    agreement = db.relationship("Agreement", backref="installments")

    agreement_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("agreements.id", on_delete='CASCADE'),
        nullable=False
    )

    payments = db.relationship(
        "Payment",
        back_populates="installment",
        cascade="all, delete-orphan"
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
