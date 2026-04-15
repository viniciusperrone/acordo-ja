import uuid
from datetime import datetime

from sqlalchemy import UUID

from config.db import db
from utils.enum import NotificationType


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = db.Column(
        db.Enum(NotificationType, name="notification_type_enum"),
        nullable=False,
    )

    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    extra = db.Column(db.JSON, nullable=False)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True, index=True)
    user = db.relationship("User", backref="notifications")

    is_read = db.Column(db.Boolean, nullable=False, default=False)
    read_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def mark_as_read(self):
        self.is_read = True
        self.read_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': str(self.id),
            'type': self.type.value,
            'title': self.title,
            'message': self.message,
            'metadata': self.metadata,
            'user_id': str(self.user_id) if self.user_id else None,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat(),
        }
