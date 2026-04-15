from functools import wraps

from flask import g, abort
from flask_jwt_extended import get_jwt_identity

from users import User
from config.db import db


def current_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)

        if not user:
            abort(401, description="User not found")

        g.current_user = user

        return fn(*args, **kwargs)

    return wrapper
