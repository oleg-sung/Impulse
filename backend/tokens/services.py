from google.cloud.firestore_v1 import DocumentReference, DocumentSnapshot
from google.cloud.firestore_v1.base_query import QueryType
from firebase_admin.auth import UserRecord

from backend.error import HttpError, validate
from backend.tokens.schema import UpdateToken, Token
from firebase_db import token_model


def create_token_to_user(data: dict, code=None) -> DocumentSnapshot:
    """
    Create a new token for user at registered
    :param data: data ....
    :param code: value token or None
    :return: True if token was created
    """
    data["code"] = code or 'IsAdminToken'

    return create_token_document(data)


def disable_user_token(user_id: str, token_id: str) -> dict:
    """

    """
    token_obj = get_token_info_by_id(token_id)
    token_dict = token_obj.to_dict()
    if token_dict is None or token_dict['userCreatedID'] != user_id:
        raise HttpError(404, 'This token not found')
    data = update_token_info(token_obj, is_active=False if token_dict['isActive'] else True)
    return data


def get_all_token_by_id(user_id: str) -> dict:
    """
    ...
    """
    tokens_query = search_token_by_user_id(user_id)
    token_list = []
    for token in tokens_query.stream():
        token_list.append(token.to_dict() | {'id': token.id})
    return {'status': 'success', 'data': token_list}


def create_token_document(data: dict) -> DocumentSnapshot:
    """
    Create a new token to firebase
    :param data: created data to create token document
    :return: ...
    """
    data = validate(data, Token)
    token = token_model.document()
    token.set(data)
    return token.get()


def create_token_reference_dict(user: UserRecord) -> dict:
    """
    Create dict with token reference for user's profile
    :param user: user object
    :return: token reference dict
    """
    query = search_token_by_user_id(user.uid)
    reference = get_token_reference_for_admin(query)
    return {
        'token': reference
    }


def search_token_by_user_id(user_id: str) -> QueryType:
    """
    Search token by user's uid
    :param user_id: user's uid
    :return: if the token was found return QueryType or raise HttpError
    """
    token_query = token_model.where('userCreatedID', '==', user_id)
    if not token_query:
        raise HttpError(404, f'token not found: {user_id}')
    return token_query


def get_token_reference_for_admin(query: QueryType) -> DocumentReference:
    """
    Get token reference for admin user to firebase
    :param query: Query objects of tokens
    :return: token reference for admin user
    """
    for token in query.stream():
        token_code = token.to_dict()['code']
        if token_code == 'IsAdminToken':
            return token.reference
    raise HttpError(404, 'token not found')


def get_token_info_by_id(token_id: str) -> DocumentSnapshot:
    """
    Get token information by token_id
    :param token_id: id token's document
    :return: dict with token information
    """
    try:
        token_info = token_model.document(token_id).get()
    except Exception as e:
        raise HttpError(400, str(e))
    return token_info


def update_token_info(token: DocumentSnapshot, **kwargs) -> dict:
    """
    Update token information
    :param token: token object Document Snapshot type
    :param kwargs: parameters to update token information
    :return: dict with status updated token
    """
    data = validate({**kwargs}, UpdateToken)
    try:
        token.reference.update(data)
    except Exception as e:
        raise HttpError(400, str(e))
    return {'status': f'token {token.id} - update successful'}


def delete_token_by_id(token_id: str, user_id: str) -> dict:
    token = get_token_info_by_id(token_id)
    token_dict = token.to_dict()
    token_id = token.id
    if token_dict['userCreatedID'] != user_id:
        raise HttpError(404, f'token {token_id} not found')
    if token_dict['authCount'] > 0:
        raise HttpError(404, f'token {token_id} has auth count greater than 0')
    token.reference.delete()
    return {'status': f'token {token_id} has been deleted'}

