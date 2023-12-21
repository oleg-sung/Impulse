from app.error import HttpError
from firebase_db import pb, db

user_profile = db.collection('user_profile')


def user_is_admin(request):
    token = request.headers.get('Authorization', None)
    if token:
        user_info = pb.auth().get_account_info(token)
        user_id = user_info['users'][0]['localId']
        user = user_profile.document(user_id).get()
        if user.to_dict()['user_type'] == 'admin':
            return user.to_dict()
    raise HttpError(400, 'Permission denied')
