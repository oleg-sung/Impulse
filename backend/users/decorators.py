from functools import wraps

from flask import request

from backend.error import HttpError
from backend.firebase_db import fb_auth


def authorization(f):
    """
    Decorator for verifying user authorization using Session cookie from request
    Add dict with user information to request
    :param f: function to be decorated
    :return: function's decorator
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Session Cookies' in request.cookies:
            token = request.cookies.get('Session Cookies', None)
        if not token:
            raise HttpError(400, 'Permission denied')
        
        user = fb_auth.verify_session_cookie(token)
        if user['admin']:
            user_dict = {**user}
            request.user = user_dict
            return f(*args, **kwargs)
        else:
            raise HttpError(400, 'Permission denied')
    return decorator
