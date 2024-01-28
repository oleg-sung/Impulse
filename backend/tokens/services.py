from google.cloud.firestore_v1 import DocumentReference

from backend.error import HttpError, validate
from backend.tokens.schema import UpdateToken, Token
from backend.firebase_db.services import FirebaseDB


class TokenService:
    token_model_name = 'token'

    def __init__(self, user_id=None):
        self.user_id = user_id
        self.db = FirebaseDB()

    def create_token_document(self, data: dict) -> DocumentReference:
        """

        """
        data = validate(data, Token)
        token_doc = self.db.create_doc(self.token_model_name, data)
        return token_doc

    def disable_user_token(self, token_id: str) -> dict:
        """

        """
        token_obj = self.db.get_doc(self.token_model_name, token_id)
        token_dict = token_obj.to_dict()
        if token_dict is None or token_dict['userCreatedID'] != self.user_id:
            raise HttpError(404, 'Document not found')
        data = {
            'is_active': False if token_dict['isActive'] else True
        }
        validated_data = validate(data, UpdateToken)
        self.db.update_doc(self.token_model_name, token_id, validated_data)
        return {'id': token_id, 'is_active':  data['is_active']}

    def get_token_info_dict(self, token_id: str) -> dict:
        """

        """
        token = self.db.get_doc(self.token_model_name, token_id)
        token_dict = token.to_dict()
        return token_dict | {'id': token.id}

    def get_all_token_by_id(self) -> dict:
        """

        """
        tokens_query = self.db.search_doc(
            self.token_model_name,
            'userCreatedID', '==', self.user_id
        )
        token_list = []
        for token in tokens_query.stream():
            token_list.append(token.to_dict() | {'id': token.id})
        return {'status': 'success', 'data': token_list}

    def delete_token_by_id(self, token_id: str) -> dict:
        """

        """
        token_obj = self.db.get_doc(self.token_model_name, token_id)
        token_dict = token_obj.to_dict()
        if token_dict['userCreatedID'] != self.user_id:
            raise HttpError(404, f'token {token_id} not found')
        if token_dict['authCount'] > 0:
            raise HttpError(404, f'token {token_id} has auth count greater than 0')
        self.db.delete_doc(self.token_model_name, token_id)
        return {'status': f'token {token_id} has been deleted'}
