import base64
from datetime import timedelta
from typing import Any

from firebase_admin.auth import UserRecord, UserNotFoundError
from firebase_admin.exceptions import FirebaseError
from google.cloud.firestore_v1 import DocumentSnapshot, DocumentReference, ArrayUnion
from google.cloud.firestore_v1.base_query import QueryType, FieldFilter
from google.cloud.storage import Blob

from requests.exceptions import HTTPError
from backend.error import HttpError
from backend.firebase_db.tasks import upload_file_to_storage, delete_document, update_document
from backend.firebase_db import pb_auth, token_model, user_profile_model, club_model, collection_model, bucket
from backend.firebase_db import auth as fb_auth


class FirebaseDB:
    MODEL_DICT = {
        'user_profile': user_profile_model,
        'token': token_model,
        'club': club_model,
        'collection': collection_model
    }

    def get_doc(self, model_name: str, doc_id: str) -> DocumentSnapshot:
        """

        """
        doc = self.MODEL_DICT.get(model_name).document(doc_id).get()
        if not doc.exists:
            raise HttpError(404, f'Document {doc_id} not found')
        return doc

    def create_doc(self, model_name, data: dict, _id: str = None) -> DocumentReference:
        """

        """
        doc = self.MODEL_DICT.get(model_name).document(_id)
        doc.set(data)
        return doc

    def update_doc(self, model_name: str, _id: str, data: dict) -> None:
        update_document.delay(model_name, _id, data)

    def delete_doc(self, model_name: str, _id: str) -> None:
        delete_document.delay(model_name, _id)

    def search_doc(self, model_name, field: str, operators: str, value: str | int) -> QueryType:
        query = self.MODEL_DICT.get(model_name).where(filter=FieldFilter(field, operators, value))
        if not query:
            raise ValueError('Query is empty')
        return query

    def add_doc_to_map(self, model_name, data: list[str], _id: str = None) -> None:
        key, key2, value = data
        doc = self.MODEL_DICT.get(model_name).document(_id)
        add_dict = {f'{key}.{key2}': ArrayUnion([value])}
        doc.update(add_dict)

    def add_doc_to_list(self, model_name: str, key: str, value: Any, _id: str = None) -> None:
        doc = self.MODEL_DICT.get(model_name).document(_id)
        add_dict = {f'{key}': ArrayUnion([value])}
        doc.update(add_dict)


class FirebaseAuth:

    def __init__(self):
        self.fb_auth = fb_auth
        self.pb_auth = pb_auth

    def create_user_to_firebase(self, email: str, password: str) -> UserRecord:
        """
        Create a new user to firebase
        :param email: user's email address
        :param password: user's password
        :return: user objects
        """
        try:
            user = self.fb_auth.create_user(email=email, password=password)
            self.create_claims(user.uid, admin=True)
        except FirebaseError as e:
            raise HttpError(400, str(e))
        return user

    def login_to_firebase(self, email: str, password: str) -> dict:
        """
        Login to firebase
        :param email: verified user's email
        :param password: user's password
        :return: user's dict with token and user info
        """
        try:
            user_dict = self.pb_auth.sign_in_with_email_and_password(email, password)
        except HTTPError as e:
            raise HttpError(400, str(e))
        return user_dict

    def get_user_by_email(self, email: str) -> UserRecord:
        """
        Get user info by email and return
        :param email: user's email
        :return: object with user info
        """
        try:
            return self.fb_auth.get_user_by_email(email)
        except UserNotFoundError:
            raise HttpError(404, 'User not found')

    def create_cookies(self, token, time=None) -> dict:
        """

        """
        cookies = self.fb_auth.create_session_cookie(token, timedelta(seconds=1209600) if time is None else time)
        return {'Session Cookies': cookies}

    def create_claims(self, uid, **kwargs) -> None:
        self.fb_auth.set_custom_user_claims(uid, {**kwargs})


class Storage:

    def __init__(self, name: str = None):
        self.name = name
        self.blob = None

    def create_blob(self, content: bytes, content_type: str = None, metadata: dict = None) -> str:
        _content = base64.b64encode(content).decode('utf-8')
        upload_file_to_storage.delay(_content, self.name, content_type, metadata)
        return metadata['id']

    def update_blob(
            self,
            content: bytes = None,
            content_type: str = None,
            metadata: dict = None
    ) -> list[str]:
        if metadata is not None:
            self.blob.metadata = metadata
        if content_type is not None:
            self.blob.content_type = content_type
        if content is not None:
            _content = base64.b64encode(content).decode('utf-8')
            upload_file_to_storage.delay(_content, self.name)
        else:
            raise ValueError

        return [self.blob.metadata['id'], self.blob.name]

    def get_blob(self) -> Blob:
        self.blob = bucket.get_blob(self.name)
        return self.blob

    def delete_blob(self):
        ...

    def get_blobs(self, prefix: str) -> list:
        blobs = bucket.list_blobs(prefix=prefix)
        return blobs
