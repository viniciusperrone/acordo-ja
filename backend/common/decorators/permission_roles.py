from functools import wraps

from flask import g

from common.exceptions import UnauthorizedError, ForbiddenError
from utils.enum import UserRole


def permission_roles(*roles):
    """
    Secures Flask endpoints by validating the current user's role against allowed roles.

    NOTE: Must be placed BELOW the authentication/identity decorator (e.g., @current_user)
    so that the identity is populated before this permission check runs.

    Example:
        @current_user
        @permission_roles(UserRole.ADMIN, UserRole.MANAGER)
        def activate_agreement():
            ...
    """

    if not all(isinstance(role, UserRole) for role in roles):
        raise ValueError("All roles must be instances of UserRole")

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):

            user = getattr(g, "current_user", None)

            if not user:
                raise UnauthorizedError

            if getattr(user, 'role', None) not in roles:
                raise ForbiddenError

            return fn(*args, **kwargs)

        return wrapper
    return decorator
