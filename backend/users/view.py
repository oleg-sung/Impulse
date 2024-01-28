from flask import Blueprint, jsonify, request, make_response

from .decorators import authorization
from backend.users.services import UserServices, UserProfileService, ClubServices

user_api = Blueprint('user', __name__)


@user_api.route('/profile/', methods=['GET'])
@authorization
def get_user_profile():
    """
    Get dict with user's info using token authorization
    :return: JSON with user's info
    """
    data = UserProfileService(request.user['user_id']).get_user_profile()
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
    :param: club name: club name of the user
    :return: JSON
    """
    password = request.json.pop('password', None)
    response_data = UserServices().user_register(request.json, password)
    return jsonify(response_data), 201


@user_api.route('/login/', methods=['POST'])
def login():
    """
    login a user in the app and return user's token'
    :param: email: email of the user
    :param: password: <PASSWORD>
    :return: JSON with user's token
    """
    if {'email', 'password'}.issubset(request.json):
        data = UserServices().login_user(email=request.json['email'], password=request.json['password'])
        res = make_response('Log in')
        res.set_cookie('Session Cookies', data['Session Cookies'], max_age=60 * 60 * 24 * 365 * 2)
        return res

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
    data = UserServices().send_password_reset_link(email)
    return jsonify(data), 201


@user_api.route('/profile/change/', methods=['PUT'])
@authorization
def change_profile_info():
    data = UserProfileService(request.user['user_id']).update_user_profile(request.json)
    return jsonify(data), 201


@user_api.route('/club/change/', methods=['PUT'])
@authorization
def change_club_info():
    image = request.files.get('image', None)
    data = request.form.to_dict()
    data = ClubServices(request.user['user_id']).update_club(data, image)
    return jsonify(data), 200


@user_api.route('/club/', methods=['GET'])
@authorization
def club_info():
    data = ClubServices(request.user['user_id']).get_club_dict()
    return jsonify(data), 200


@user_api.route('/club/coaches/', methods=['GET'])
@authorization
def list_coach():
    ...


@user_api.route('/club/coaches/<id_coach>/set/', methods=['POST'])
@authorization
def set_coach():
    ...
