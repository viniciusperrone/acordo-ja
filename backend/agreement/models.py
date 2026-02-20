import uuid

from datetime import datetime
from decimal import Decimal

from config.db import db
from utils.enum import AgreementStatus

from sqlalchemy.dialects.postgresql import UUID, NUMERIC


class Agreement(db.Model):
    __tablename__ = 'agreements'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    total_traded = db.Column(NUMERIC(12, 2), nullable=False) # Automatically calculated
    installments_quantity = db.Column(db.Integer, nullable=False, default=1) # Default 1
    installment_value = db.Column(NUMERIC(12, 2), nullable=False)

    entry_value = db.Column(NUMERIC(12, 2), nullable=False, default=Decimal("0.00"))
    discount_applied = db.Column(NUMERIC(12, 2), default=Decimal("0.00"))
    first_due_date = db.Column(db.Date, nullable=False)
    status = db.Column(
        db.Enum(AgreementStatus, name="agreementstatus"),
        default=AgreementStatus.DRAFT,
        server_default=AgreementStatus.DRAFT.value,
        nullable=False
    )

    debt_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("debts.id"),
        nullable=False,
        index=True
    )
    debt = db.relationship("Debt", back_populates="agreements")

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
