from app.error import HttpError
from firebase_db import db

token = db.collection('tokens')


def create_token(user_id, code=None):
    data = {
        'code': code or 'adminToken',
        'is_active': True,
        'auth_count': 1,
        'user_id': user_id,
    }
    token.document().set(data)
    token_info = token.where('user_id', '==', user_id)
    reference_data = [doc.reference for doc in token_info.stream()]
    return reference_data[0]


def disable_token(user_id, token_id):
    token_info = token.document(token_id).get()
    dict = token_info.to_dict()
    if token_info and dict:
        if dict['user_id'] == user_id:
            token_info.update({'is_active': False}) 
            return {'success': 'Ok'}
    raise HttpError(404, 'Not Found')

