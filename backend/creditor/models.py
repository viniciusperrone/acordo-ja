import uuid
from sqlalchemy import UUID, NUMERIC

from config.db import db
from utils.br_bank import BR_BANK_CHOICES


class Creditor(db.Model):
    __tablename__ = 'creditors'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_code = db.Column(
        db.Enum(
            *[choice[0] for choice in BR_BANK_CHOICES],
            name="br_bank_enum"
        ),
        nullable=False,
        unique=True
    )

    interest_rate = db.Column(NUMERIC(5,2))
    fine_rate = db.Column(NUMERIC(5,2))
    discount_limit = db.Column(NUMERIC(5,2))

    created_at = db.Column(db.DateTime, default=db.func.now())

    @property
    def bank_name(self):
        return dict(BR_BANK_CHOICES).get(self.bank_code)
