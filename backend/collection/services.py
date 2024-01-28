from werkzeug.datastructures.file_storage import FileStorage

from backend.collection.schema import CollectionSchema, Card, UpdateCollection
from backend.collection.tasks import add_card_to_collection
from backend.collection.validators import image_validate
from backend.error import validate, HttpError
from backend.firebase_db.services import FirebaseDB, Storage


class CardService:
    collection_model_name = 'collection'

    def __init__(self, id_collection: str = None):
        self.id_collection = id_collection
        self.storage = Storage()
        self.db = FirebaseDB()

    def create_card(self, image: FileStorage, metadata: dict) -> dict:
        """

        """
        image_bytes, image_name = image_validate(image)
        self.id_collection = metadata['collection']
        metadata = validate(metadata, Card)
        content_type = image.content_type
        image_name = f'thumbnail/{metadata['collection']}/{metadata['id']}'
        self.storage.name = image_name
        _id = self.storage.create_blob(image_bytes, content_type, metadata)
        add_card_to_collection.delay(self.collection_model_name, 'cards', _id, self.id_collection)
        return {'status': True, 'card_id': _id}

    def get_card_info(self, id_card: str) -> dict:
        """

        """
        self.storage.name = f'thumbnail/{self.id_collection}/{id_card}'
        blob = self.storage.get_blob()
        if blob is None:
            raise HttpError(404, 'Document not found')
        return blob.metadata | {'url': blob.public_url}

    def get_card_by_type(self, _type: str) -> dict:
        prefix = f'thumbnail/{self.id_collection}/'
        data = self.storage.get_blobs(prefix=prefix)
        data = [i.metadata | {'url': i.public_url} for i in data if i.metadata['type'] == _type]
        return {'data': data, 'collection': self.id_collection, 'type': _type}

    def get_all_cards_info(self) -> dict:
        prefix = f'thumbnail/{self.id_collection}/'
        data = self.storage.get_blobs(prefix=prefix)
        cards_list = [i.metadata | {'url': i.public_url} for i in data]
        return {'collection': self.id_collection, 'cards': cards_list}


class CollectionService(CardService):
    collection_model_name = 'collection'

    def __init__(self, user_id: str = None):
        self.user_id = user_id
        self.db = FirebaseDB()
        self.storage = Storage()
        super(CardService, self).__init__()

    def create_collection(self, data: dict) -> dict:
        validate_data = validate(data | {'owner': self.user_id}, CollectionSchema)
        collection_doc = self.db.create_doc(self.collection_model_name, validate_data)
        return {'status': True, 'msg': 'A collection created', 'id': collection_doc.id}

    def get_collection_data(self) -> dict:
        collection_doc = self.db.get_doc(self.collection_model_name, self.user_id)
        collection_dict = collection_doc.to_dict()
        return collection_dict | {'id': collection_doc.id}

    def get_all_collections_data(self) -> dict:
        """
        Getting the data for all collections
        :return: data: dict with all collections info
        """
        data = []
        query_set = self.db.search_doc(self.collection_model_name, 'isActive', '==', True)
        for collection in query_set.stream():
            collection_dict = collection.to_dict()
            if collection_dict.get('cards', None):
                del collection_dict['cards']
            data.append(collection_dict)
        return {'status': 'success', 'data': data}

    def change_status_collection(self, _id: str) -> dict:
        """
        Change status of collection's active to False
        :param _id: collection's id in firebase
        :return: dict with info about updated status
        """

        collection_doc = self.db.get_doc(self.collection_model_name, _id)
        collection_dict = collection_doc.to_dict()
        if collection_dict['userCreatedID'] != self.user_id:
            raise HttpError(400, 'Permission denied')
        validated_data = validate(collection_dict, UpdateCollection)
        validated_data['isActive'] = False if collection_dict['isActive'] else True
        self.db.update_doc(self.collection_model_name, _id, validated_data)
        return {'status': True, 'id': collection_doc.id, 'isActive': validated_data['isActive']}
