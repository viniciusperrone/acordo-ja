from functools import wraps

from flask import g

from common.exceptions import UnauthorizedError, ForbiddenError
from utils.enum import UserRole


def permission_roles(*roles):

    if not all(isinstance(role, UserRole) for role in roles):
        raise ValueError("All roles must be instances of UserRole")

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):

            user = getattr(g, "current_user", None)

            print("user", user)

            if not user:
                raise UnauthorizedError

            if user.role not in roles:
                raise ForbiddenError

            return fn(*args, **kwargs)

        return wrapper
    return decorator
