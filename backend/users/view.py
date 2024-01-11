from flask import Blueprint, jsonify, request

from backend.error import validate
from .decorators import authorization
from .schema import UserProfile
from backend.users.services import user_register, login_user, create_user_info_dict, send_password_reset_link

user_api = Blueprint('user', __name__)


@user_api.route('/profile/', methods=['GET'])
@authorization
def get_user_profile():
    """
    Get dict with user's info using token authorization
    :return: JSON with user's info
    """
    data = create_user_info_dict(request.user['user_profile'])
    return jsonify(data), 200


@user_api.route('/register/', methods=['POST'])
def register():
    """
    Register a new user in the backend and send email to the user's email address to verify
    Created the new user then it make user's profile
    :param: email: email of the user
    :param: password: <PASSWORD>
    :param: first_name: first name of the user
    :param: last_name: last name of the user
    :param: birth_date: birth date of the user
    :param: phone: phone number of the user
    :return: JSON
    """
    password = request.json.pop('password', None)
    data = validate(request.json, UserProfile)
    response_data = user_register(data, password)
    return jsonify(response_data), 201


@user_api.route('/login/', methods=['POST'])
def login():
    """
    login a user in the app and return user's token'
    :param: email: email of the user
    :param: password: <PASSWORD>
    :return: JSON with user's token
    """
    data = request.json
    if {'email', 'password'}.issubset(data):
        data = login_user(email=data['email'], password=data['password'])
        return jsonify(data), 201

    else:
        return jsonify({'error': 'Required fields were not passed'}), 400


@user_api.route('/password/reset/', methods=['POST'])
@authorization
def change_password():
    """
    Send password reset link to user's email address
    :return: JSON with status
    """
    email = request.user['email']
    data = send_password_reset_link(email)
    return jsonify(data), 201


@user_api.route('/profile/change/', methods=['PUT'])
@authorization
def change_profile_info():
    ...
