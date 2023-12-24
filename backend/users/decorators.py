from functools import wraps

from flask import request

from backend.error import HttpError
from backend.users.services import get_user_info_by_token, get_user_profile_info_by_id


def authorization(f):
    """
    Decorator for verifying user authorization using Authorization header from request
    Add dict with user information to request
    :param f: function to be decorated
    :return:
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            raise HttpError(400, 'Permission denied')
        user_info = get_user_info_by_token(token)
        user_id = user_info['users'][0]['localId']
        user_data = get_user_profile_info_by_id(user_id)
        if user_data['user_type'] == 'admin':
            user_dict = {'user': user_info['users'][0], 'user_profile': user_data}
            request.user = user_dict
            return f(*args, **kwargs)
    return decorator
