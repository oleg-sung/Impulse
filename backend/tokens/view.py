from flask import Blueprint, request, jsonify

from backend.tokens.services import create_token_to_user, disable_user_token, get_all_token_by_id
from backend.users.decorators import authorization

token_api = Blueprint('tokens', __name__)


@token_api.route('/', methods=['GET'])
@authorization
def get_all_user_token():
    user_id = request.user['user']['localId']
    data = get_all_token_by_id(user_id)
    return jsonify(data), 200


@token_api.route('/create/', methods=['POST'])
@authorization
def create_token_for_auth():
    data = request.json
    if {'token'}.issubset(data):
        token_value = data['token']
        user_id = request.user['user']['localId']
        data = create_token_to_user(user_id, token_value)
        return jsonify(data), 201

    return jsonify({'error': 'Required fields were not'}), 400


@token_api.route('/disable/<token_id>/', methods=['PUT'])
@authorization
def disable_token_for_auth(token_id: str):
    user_id = request.user['user']['localId']
    data = disable_user_token(user_id, token_id)
    return jsonify(data), 201


@token_api.route('/delete/<token_id>/', methods=['DELETE'])
@authorization
def delete_token(token_id: str):
    ...
