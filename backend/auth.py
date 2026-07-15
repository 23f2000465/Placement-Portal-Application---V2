from functools import wraps

from flask import jsonify, session

from extensions import db
from models import User


def role_required(*allowed_roles):
    """Session ke user aur role ko har protected API par check karta hai."""
    def decorator(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            user = db_user()
            if not user:
                return jsonify(message="Login required"), 401
            if not user.is_active:
                session.clear()
                return jsonify(message="Account is deactivated"), 403
            if allowed_roles and user.role not in allowed_roles:
                return jsonify(message="You are not allowed to use this API"), 403
            return function(user, *args, **kwargs)
        return wrapped
    return decorator


def db_user():
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None
