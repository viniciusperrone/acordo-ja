import uuid
from sqlalchemy import UUID
from werkzeug.security import generate_password_hash, check_password_hash

from config.db import db
from utils.enum import UserRole


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)

    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    must_change_password = db.Column(db.Boolean, default=True, nullable=False)

    role = db.Column(
        db.Enum(UserRole, name="user_role_enum"),
        nullable=False
    )

    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
