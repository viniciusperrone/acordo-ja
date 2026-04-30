import uuid
from sqlalchemy import UUID, NUMERIC
from datetime import datetime

from config.db import db
from utils.enum import DebtStatus, DebtHistoryType


class Debt(db.Model):
    __tablename__ = 'debts'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    debtor_id = db.Column(
        db.Integer,
        db.ForeignKey('debtors.id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )

    creditor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('creditors.id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )

    original_value = db.Column(NUMERIC(12, 2), nullable=False)
    updated_value = db.Column(NUMERIC(12, 2), nullable=True)
    due_date = db.Column(db.Date, nullable=False)

    status = db.Column(
        db.Enum(DebtStatus, name="debt_status_enum"),
        default=DebtStatus.OPEN,
        server_default=DebtStatus.OPEN.value,
        nullable=False
    )

    agreements = db.relationship("Agreement", back_populates="debt", cascade="all, delete-orphan", passive_deletes=True)
    debtor = db.relationship("Debtor", back_populates="debts")
    creditor = db.relationship("Creditor", back_populates="debts")

    renegotiation_count = db.Column(db.Integer, default=0)
    last_agreement_date = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

class DebtHistory(db.Model):
    __tablename__ = 'debt_history'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    debt_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('debts.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    event_type = db.Column(
        db.Enum(DebtHistoryType, name="debt_history_type_enum"),
        nullable=False,
        index=True
    )

    old_status = db.Column(db.Enum(DebtStatus, name="debt_status_enum"), nullable=True)
    new_status = db.Column(db.Enum(DebtStatus, name="debt_status_enum"), nullable=True)
    old_value = db.Column(NUMERIC(12, 2), nullable=True)
    new_value = db.Column(NUMERIC(12, 2), nullable=True)

    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reason = db.Column(db.String, nullable=True)

    extra = db.Column(db.JSON, nullable=True)

    debt = db.relationship("Debt", backref="history")

    __table_args__ = (
        db.Index('ix_debt_history_debt_id_changed_at', 'debt_id', 'changed_at'),
    )
