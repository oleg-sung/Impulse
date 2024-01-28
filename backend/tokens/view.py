from flask import Blueprint, request, jsonify

from backend.tokens.services import TokenService
from backend.users.decorators import authorization

token_api = Blueprint('tokens', __name__)


@token_api.route('/', methods=['GET'])
@authorization
def get_all_user_token():
    user_id = request.user['user_id']
    data = TokenService(user_id).get_all_token_by_id()
    return jsonify(data), 200


@token_api.route('/create/', methods=['POST'])
@authorization
def create_token_for_auth():
    if {'code'}.issubset(request.json):
        user_id = request.user['user_id']
        data = request.json | {'user_id': user_id, 'club_id': user_id}
        token_doc = TokenService().create_token_document(data)
        return jsonify({'status': True, 'msg': 'Token has created', 'id': token_doc.id}), 201

    return jsonify({'error': 'Required fields were not'}), 400


@token_api.route('/disable/<token_id>/', methods=['PUT'])
@authorization
def disable_token_for_auth(token_id: str):
    user_id = request.user['user_id']
    data = TokenService(user_id).disable_user_token(token_id)
    return jsonify(data), 201


@token_api.route('/delete/<token_id>/', methods=['DELETE'])
@authorization
def delete_token(token_id: str):
    data = TokenService(request.user['user_id']).delete_token_by_id(token_id)
    return jsonify(data), 204
