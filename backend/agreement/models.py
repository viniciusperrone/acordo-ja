import uuid
from datetime import datetime
from config.db import db

from sqlalchemy.dialects.postgresql import UUID


class Agreement(db.Model):
    __tablename__ = 'agreements'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    total_traded = db.Column(db.Float, nullable=False)
    qtd_instalments = db.Column(db.Integer, nullable=False)

    discount_applied = db.Column(db.Float, default=0)

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
