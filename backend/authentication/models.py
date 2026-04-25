import uuid
from datetime import datetime, timedelta

from sqlalchemy import UUID

from config.db import db


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    token = db.Column(db.String(255), nullable=False, unique=True, index=True)

    expires_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(minutes=30),
        index=True
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    used_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    user = db.relationship('User', backref="password_reset_tokens")

    @property
    def is_expired(self) -> bool:
        if self.is_used:
            return True

        return datetime.utcnow() > self.expires_at

    @property
    def is_used(self) -> bool:
        return self.used_at is not None


class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
