import uuid
from datetime import datetime
from config.db import db

from sqlalchemy.dialects.postgresql import UUID, NUMERIC


class Agreement(db.Model):
    __tablename__ = 'agreements'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    total_traded = db.Column(NUMERIC(12, 2), nullable=False)
    qtd_instalments = db.Column(db.Integer, nullable=False)
    installment_value = db.Column(NUMERIC(12, 2), nullable=False)

    entry_value = db.Column(NUMERIC(12, 2), nullable=False)
    discount_applied = db.Column(db.Float, default=0)
    first_due_date = db.Column(db.Date, nullable=False)

    debt_id = db.Column(
        db.Integer,
        db.ForeignKey("debts.id"),
        nullable=False
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
