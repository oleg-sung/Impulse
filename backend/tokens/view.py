from flask import Blueprint, request, jsonify

from backend.tokens.services import create_token_to_user, disable_user_token, get_all_token_by_id, delete_token_by_id
from backend.users.decorators import authorization

token_api = Blueprint('tokens', __name__)


@token_api.route('/', methods=['GET'])
@authorization
def get_all_user_token():
    user_id = request.user['user_id']
    data = get_all_token_by_id(user_id)
    return jsonify(data), 200


@token_api.route('/create/', methods=['POST'])
@authorization
def create_token_for_auth():
    data = request.json | request.user['user_profile'] | {'userCreatedID': request.user['uid']}
    if {'code'}.issubset(data):
        token_value = data['code']
        token = create_token_to_user(data, token_value)

        return jsonify({'status': 'token has created', 'token_id': token.id}), 201

    return jsonify({'error': 'Required fields were not'}), 400


@token_api.route('/disable/<token_id>/', methods=['PUT'])
@authorization
def disable_token_for_auth(token_id: str):
    user_id = request.user['user_id']
    data = disable_user_token(user_id, token_id)
    return jsonify(data), 201


@token_api.route('/delete/<token_id>/', methods=['DELETE'])
@authorization
def delete_token(token_id: str):
    data = delete_token_by_id(token_id, request.user['user_id'])
    return jsonify(data), 204
