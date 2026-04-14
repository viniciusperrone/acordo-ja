from functools import wraps
from config.db import db


def transactional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            kwargs["db"] = db
            result = func(*args, **kwargs)

            if isinstance(result, tuple):
                _, status = result
            else:
                status = getattr(result, "status_code", 200)

            if 200 <= status < 300:
                db.session.commit()
            else:
                db.session.rollback()

            return result

        except Exception:
            db.session.rollback()
            raise

    return wrapper
