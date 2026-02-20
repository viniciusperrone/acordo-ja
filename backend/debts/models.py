import uuid
from sqlalchemy import UUID, NUMERIC
from datetime import datetime as dt

from config.db import db
from utils.enum import DebtStatus


class Debt(db.Model):
    __tablename__ = 'debts'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    debtor_id = db.Column(
        db.Integer,
        db.ForeignKey('debtors.id'),
        nullable=False,
        index=True
    )

    creditor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('creditors.id'),
        nullable=False,
        index=True
    )

    original_value = db.Column(NUMERIC(12, 2), nullable=False)
    updated_value = db.Column(NUMERIC(12, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False)

    status = db.Column(
        db.Enum(DebtStatus, name="debt_status_enum"),
        default=DebtStatus.OPEN,
        server_default=DebtStatus.OPEN.value,
        nullable=False
    )

    agreements = db.relationship("Agreement", back_populates="debt")

    renegotiation_count = db.Column(db.Integer, default=0)
    last_agreement_date = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=dt.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=dt.utcnow)
