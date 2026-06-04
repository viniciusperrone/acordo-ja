from functools import wraps
from uuid import UUID

from flask import abort, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from config.db import db
from users import User


def current_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()

        user_id = get_jwt_identity()
        user = db.session.get(User, UUID(user_id))

        if not user:
            abort(401, description="User not found")

        g.current_user = user

        return fn(*args, **kwargs)

    return wrapper
