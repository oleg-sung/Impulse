from firebase_admin.auth import UserRecord

from backend.email import send_mail
from backend.error import HttpError
from backend.tokens.services import create_token_to_user, create_token_reference_dict
from firebase_db import fb_auth, user_profile_model, pb_auth


def login_user(email: str, password: str) -> dict:
    user = get_user_info_by_email(email)
    if user.email_verified:
        data = login_to_firebase(email, password)
        token = data['idToken']
        return {'status': 'success', 'token': token}
    raise HttpError(400, 'email has not been confirmed')


def user_register(data: dict, password: str) -> dict:
    user = create_user_to_firebase(data['email'], password)
    status = create_token_to_user(user)
    if status:
        data = {**data, **create_token_reference_dict(user)}
    create_user_profile(user, data)
    send_email_with_verification_link(user)
    return {'status': 'success'}


def create_user_info_dict(data: dict) -> dict:
    """
    Change token to token path for reading json
    :param data: user_dict form authorization user's token
    :return: new user_dict with token path
    """
    data['user_profile']['token'] = data['user_profile']['token'].path
    return data


def create_user_to_firebase(email: str, password: str) -> UserRecord:
    """
    Create a new user to firebase
    :param email: user's email address
    :param password: user's password
    :return: user objects
    """
    try:
        user = fb_auth.create_user(email=email, password=password)
    except Exception as e:
        raise HttpError(400, str(e))
    return user


def create_user_profile(user: UserRecord, data: dict) -> bool:
    """
    Create a new document with user profile data to firebase
    :param user: created user's id
    :param data: validated data for user profile
    :return: True if user profile created
    """
    try:
        user_profile_model.document(user.uid).set(data)
    except Exception as e:
        raise HttpError(400, str(e))
    return True


def send_email_with_verification_link(user: UserRecord) -> None:
    """
    Send email with verification link to user email address
    :param user: object user(USer Record type)
    :return: None
    """
    link = create_email_verification_link(user.email)
    subject = f'Verification link for {user.uid}'
    send_mail(subject, user.email, link)


def create_email_verification_link(email: str) -> str:
    """
    Create email verification link to verify user's email address
    :param email: user's email
    :return: link to verify
    """
    return fb_auth.generate_email_verification_link(email)


def get_user_info_by_token(token: str) -> dict:
    """
    Get user info by user's token and return
    :param token: user's created at login
    :return: dict with user info
    """
    try:
        return pb_auth.get_account_info(token)
    except Exception as e:
        raise HttpError(400, str(e))


def get_user_info_by_email(email: str) -> UserRecord:
    """
    Get user info by email and return
    :param email: user's email
    :return: object with user info
    """
    try:
        return fb_auth.get_user_by_email(email)
    except Exception as e:
        raise HttpError(404, str(e))


def get_user_profile_info_by_id(user_id: str) -> dict:
    """
    Get user profile info by user's uid
    :param user_id: user's uid
    :return: dict with user profile info
    """
    try:
        user = user_profile_model.document(user_id).get()
    except Exception as e:
        raise HttpError(404, str(e))
    return user.to_dict()


def login_to_firebase(email: str, password: str) -> dict:
    """
    Login to firebase
    :param email: verified user's email
    :param password: user's password
    :return: user's dict with token and user info
    """
    try:
        user_dict = pb_auth.sign_in_with_email_and_password(email, password)
    except Exception as e:
        raise HttpError(400, str(e))
    return user_dict


def send_password_reset_link(email: str) -> dict:
    try:
        link = fb_auth.generate_password_reset_link(email)
        subject = 'Password Reset'
        send_mail(subject, email, link)
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    return {'status': True, 'message': 'email sent successfully'}
