from functools import wraps

from flask import request

from backend.error import HttpError
from backend.users.services import get_user_info_by_token, get_user_profile_info_by_id
from firebase_db import fb_auth


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
        if 'Session_cookie' in request.cookies:
            token = request.cookies['Session_cookie']
        if not token:
            raise HttpError(400, 'Permission denied')
        user = fb_auth.verify_session_cookie(token)
        user_doc = get_user_profile_info_by_id(user['user_id'])
        user_data = user_doc.to_dict()
        if user_data['user_type'] == 'admin':
            user_dict = {**user, 'user_profile': user_data}
            request.user = user_dict
            return f(*args, **kwargs)
        else:
            raise HttpError(400, 'Permission denied')
    return decorator
