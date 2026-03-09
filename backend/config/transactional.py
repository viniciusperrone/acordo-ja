from functools import wraps
from config.db import db


def transactional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            kwargs["db"] = db
            result = func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception:
            db.session.rollback()
            raise

    return wrapper
