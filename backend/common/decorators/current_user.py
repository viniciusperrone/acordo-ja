from functools import wraps

from flask import g, abort
from flask_jwt_extended import get_jwt_identity

from users import User


def current_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        db = kwargs.get("db")

        if not db:
            raise RuntimeError("DB session not provided")

        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)

        if not user:
            abort(401, description="User not found")

        g.current_user = user

        return fn(*args, **kwargs)

    return wrapper
