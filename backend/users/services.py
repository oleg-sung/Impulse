from google.cloud.firestore_v1 import DocumentReference
from werkzeug.datastructures.file_storage import FileStorage

from backend.collection.validators import image_validate
from backend.email import send_mail, send_email_with_verification_link
from backend.error import HttpError, validate
from backend.tokens.services import TokenService
from backend.users.schema import UpdateUserProfileSchema, ClubSchema, UserProfileSchema, UpdateClubSchema
from backend.firebase_db.services import Storage, FirebaseDB, FirebaseAuth


class UserProfileService:
    user_profile_model_name = 'user_profile'

    def __init__(self, user_id: str = None):
        self.user_id = user_id
        self.db = FirebaseDB()

    def create_user_profile(self, data: dict) -> None:
        """
        Create a new document with user profile data to firebase
        :param data: validated data for user profile
        :return: user's profile document type Document Snapshot
        """
        data = validate(data, UserProfileSchema)
        self.db.create_doc(self.user_profile_model_name, data, self.user_id)

    def update_user_profile(self, data: dict) -> dict:
        """

        """
        data = validate(data, UpdateUserProfileSchema)
        self.db.update_doc(self.user_profile_model_name, self.user_id, data)
        return {'status': True, 'message': 'User profile updated', 'id': self.user_id}

    def get_user_profile(self) -> dict:
        """

        """
        profile_doc = self.db.get_doc(self.user_profile_model_name, self.user_id)
        data = profile_doc.to_dict()
        data['token'] = data['token'].path
        return data


class ClubServices:
    club_model_name = 'club'

    def __init__(self, user_id: str = None):
        self.user_id = user_id
        self.db = FirebaseDB()

    def create_club(self, data: dict) -> DocumentReference:
        """

        """
        validated_data = validate(data, ClubSchema)
        club = self.db.create_doc(self.club_model_name, validated_data, self.user_id)
        return club

    def get_club_dict(self) -> dict:
        """

        """
        data = self.db.get_doc(self.club_model_name, self.user_id)
        return data.to_dict()

    def update_club(self, data: dict, image: FileStorage = None) -> dict:
        """

        """
        if image:
            blob_data = self.set_image_to_club(image)
            data['image'] = blob_data[0]
        validated_data = validate(data, UpdateClubSchema)
        self.db.update_doc(self.club_model_name, self.user_id, validated_data)
        return {'status': 'success', 'id': self.user_id}

    def set_image_to_club(self, image: FileStorage):
        image_bytes, image_name = image_validate(image)
        blob_name = f'club/{self.user_id}.{image_name.split('.')[-1]}'
        stor = Storage(blob_name)
        blob = stor.get_blob()
        if blob:
            blob_data = stor.update_blob(content=image_bytes)
        else:
            blob_data = stor.create_blob(image_bytes, image.content_type)

        return blob_data


class UserServices(UserProfileService, ClubServices):

    def __init__(self):
        self.auth = FirebaseAuth()
        super(UserProfileService, self).__init__()

    def user_register(self, data: dict, password: str) -> dict:
        """

        """
        user = self.auth.create_user_to_firebase(data['email'], password)
        self.user_id = user.uid
        self.create_club(data)
        data['userCreatedID'] = self.user_id
        data['clubID'] = self.user_id
        data["code"] = 'IsAdminToken'
        token = TokenService().create_token_document(data)
        data['token'] = token.get().reference
        self.create_user_profile(data)
        send_email_with_verification_link(user, self.auth)
        return {'status': 'success'}

    def login_user(self, email: str, password: str) -> dict:
        """

        """
        user = self.auth.get_user_by_email(email)
        if not user.email_verified:
            raise HttpError(400, 'email has not been confirmed')
        data = self.auth.login_to_firebase(email, password)
        token = data['idToken']
        cookies = self.auth.create_cookies(token)
        return cookies

    def send_password_reset_link(self, email: str) -> dict:

        """
        Send letter with link to reset password to user's email address
        :param: email: user's email
        :return: status dict
        """
        subject = 'Password Reset'
        try:
            link = self.auth.fb_auth.generate_password_reset_link(email)
            send_mail.delay(subject, email, link)
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        return {'status': True, 'message': 'email sent successfully'}
