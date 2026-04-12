import uuid

from config.db import db
from sqlalchemy import UUID


class Lead(db.Model):
    __tablename__ = 'leads'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150))
    phone = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
