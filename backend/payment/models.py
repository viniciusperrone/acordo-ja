import uuid
from sqlalchemy import UUID, NUMERIC

from config.db import db
from utils.enum import MethodPayment


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    installment_id = db.Column(db.Integer, db.ForeignKey('installments.id'), nullable=False)
    installment = db.relationship("Installments", back_populates="payments")
    amount = db.Column(NUMERIC(12, 2), nullable=False)
    paid_at = db.Column(db.DateTime, nullable=False)
    method = db.Column(
        db.Enum(MethodPayment, name="method_payment_enum"),
        nullable=False,
    )

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
