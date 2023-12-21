from flask import Blueprint, jsonify, request
from firebase_admin import auth

from app.email import send_mail
from app.permissions import user_is_admin
from app.services import create_token, disable_token
from app.error import validate, HttpError
from app.schema import UserProfile
from firebase_db import db, pb

user_profile = db.collection('user_profile')
user_api = Blueprint('user_api', __name__)


@user_api.route('/register/', methods=['POST'])
def register():
    """
    Register a new user in the app
    """
    password = request.json.pop('password', None)
    data = validate(request.json, UserProfile)
    try:
        user = auth.create_user(email=data['email'], password=password)
    except Exception as e:
        raise HttpError(400, str(e))
    token_ref = create_token(user.uid)
    data['token'] = token_ref
    user_profile.document(user.uid).set(data)
    email_verification_link = auth.generate_email_verification_link(user.email)
    send_mail('Email confirmation', user.email, email_verification_link)
    return jsonify({'Success': True}), 201


@user_api.route('/login/', methods=['POST'])
def login():
    data = request.json
    if {'email', 'password'}.issubset(data):
        user = auth.get_user_by_email(data['email'])
        if user.email_verified:
            user = pb.auth().sign_in_with_email_and_password(data['email'], data['password'])
            token = user['idToken']
            return jsonify({'token': token}, 200)

        else:
            return jsonify({'error': 'Email has not been confirmed'}), 400

    else:
        return jsonify({'error': 'Required fields were not passed'}), 400


@user_api.route('/token/create/', methods=['POST'])
def create_token_for_auth():
    user_info = user_is_admin(request)
    data = request.json
    if {'token'}.issubset(data):
        token_value = data['token']
        user = auth.get_user_by_email(user_info['email'])
        create_token(user.uid, token_value)
        return jsonify({'status': 'OK'}), 201

    return jsonify({'error': 'Required fields were not'}), 400


@user_api.route('/token/disable/<token_id>/', methods=['POST'])
def disable_token_for_auth(token_id):
    user_info = user_is_admin(request)
    user = auth.get_user_by_email(user_info['email'])
    data = disable_token(user.uid, token_id)
    return jsonify(data), 201
