from functools import wraps
from flask import abort # type: ignore
from flask_login import current_user # type: ignore


def require_permission(permission):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.has_permission(permission):
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator
