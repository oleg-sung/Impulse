import io

from PIL import Image
from firebase_admin import firestore
from google.cloud.exceptions import NotFound
from google.cloud.firestore_v1 import DocumentSnapshot
from google.cloud.storage import Blob
from werkzeug.datastructures.file_storage import FileStorage

from backend.collection.schema import Collection, Card, UpdateSizeCollection
from backend.collection.validators import image_validate
from backend.error import validate, HttpError
from firebase_db import collection_model, bucket


def get_collection_data(_id: str) -> dict:
    """
    Getting the data with collection's info
    :param _id: id of the collection
    :return: data: dict with collection's info
    """
    collection_doc = get_collection_by_id(_id)
    data = collection_doc.to_dict()
    if data is None:
        raise HttpError(404, f'Collection with id {_id} not found')
    cards_list_path = data.pop('cards')
    cards_info = get_all_info_collection_cards(cards_list_path)
    data.update(cards_info)

    return {'status': 'success', 'data': data}


def get_all_info_collection_cards(cards_list_path: list) -> dict:
    """
    Getting the card's metadata from list cards path in the collection's dict
    :param cards_list_path: path to card in storage
    :return: dict with all cards metadata
    """
    cards_info = []
    for card in cards_list_path:
        blob = get_blob_image_from_storage(card)
        metadata = blob.metadata
        cards_info.append(metadata)
    return {'cards': cards_info}


def get_blob_image_from_storage(blob_name: str) -> Blob:
    """
    Getting the blob object from storage using blob name
    :param blob_name: blob's name in storage
    :return: blob object from storage
    """
    blob = bucket.get_blob(blob_name)
    return blob


def get_all_collections_data() -> dict:
    """
    Getting the data for all collections
    :return: data: dict with all collections info
    """
    data = []
    for collection in collection_model.stream():
        data.append(collection.to_dict())
    return {'status': 'success', 'data': data}


def create_new_collection(data: dict = None) -> dict:
    """
    Validate data and create a new collection to firebase
    :param data: data to be validated
    :return: dict with create collection status
    """
    data = validate(data, Collection)
    status = create_collection_to_firebase(data)

    if status:
        return {'msg': 'Collection is created'}
    return {'msg': 'Created error'}


def create_collection_to_firebase(data: dict) -> bool:
    """
    Create a new collection form data
    :param data: dict with data for creating the collection
    :return: bool status
    """
    try:
        collection_model.document().set(data)
    except Exception as e:
        raise HttpError(400, str(e))
    return True


def change_status_collection(data: dict, _id: str) -> dict:
    """
    Change status of collection's active to False
    :param data: data to be validated for changing collection status
    :param _id: collection's id in firebase
    :return: dict with info about updated status
    """
    data = validate(data, Collection)
    collection_doc = get_collection_by_id(_id)
    status = update_data_collection(collection_doc, is_active=data['is_active'])
    return status


def update_data_collection(collection_doc: DocumentSnapshot, **kwargs) -> dict:
    """
    Updating collection data using kwargs
    :param collection_doc: collection document in firebase(type DocumentSnapshot)
    :param kwargs: param for updating
    """
    try:
        collection_doc.reference.update({**kwargs})
    except NotFound:
        raise HttpError(404, f'Collection not found')
    return {'status': f'Collection {kwargs} has updated successful'}


def add_card_to_collection(collection_doc: DocumentSnapshot, path: str) -> dict:
    """
    Add the card to array collection using path in storage
    :param collection_doc: collection document in firebase(type DocumentSnapshot)
    :param path: the path to the image in the storage
    """
    try:
        collection_doc.reference.update({'cards': firestore.ArrayUnion((path,))})
    except NotFound:
        raise HttpError(404, f'Collection not found')
    return {'status': f'A new card has been added to collection'}


def get_collection_by_id(_id: str) -> DocumentSnapshot:
    """
    Get collection objects (DocumentSnapshot type) by id
    :param _id: collection's id in firebase
    :return: collection object Document Snapshot type
    """

    return collection_model.document(_id).get()


def create_card_to_collection(data: FileStorage, metadata: dict) -> dict:
    """
    Create a new card in collection and save it to storage
    :param data: image file (File Storage type)
    :param metadata: dict with metadata about the card
    :return: dict with info about card added to collection
    """
    collection_doc = get_collection_by_id(metadata['collection'])
    image, image_name = image_validate(data)
    metadata = validate(metadata, Card)
    content_type = data.content_type
    data = upload_image_to_firebase(image, image_name, content_type, metadata)
    add_card_to_collection(collection_doc, data['path'])

    return data


def upload_image_to_firebase(image: bytes, image_name: str, content_type: str, metadata: dict) -> dict:
    """
    Upload image to firebase with metadata and the collection's id
    :param image: image(bytes format)
    :param image_name: image name
    :param content_type: image content type
    :param metadata: image
    :return: dict with status, the public url and path of the image in storage
    """
    image_thumbnail = make_thumbnail(image)
    file_type = image_name.split('.')[-1]
    image_name = f'{metadata['collection']}_{metadata['name']}_{metadata['type']}.{file_type}'
    blob = bucket.blob(f'thumbnail/' + image_name)
    blob.metadata = metadata
    blob.content_type = content_type
    blob.upload_from_file(image_thumbnail)

    return {'status': 'image uploaded', 'path': blob.name}


def make_thumbnail(image: bytes) -> io.BytesIO:
    """
    Make thumbnail for the image and return it as a BytesIO
    :param image: image(bytes format)
    :return: BytesIO object of the thumbnail's image
    """
    image_io = io.BytesIO(image)
    image = Image.open(image_io)
    image.thumbnail((300, 300))
    image_bytes = io.BytesIO()
    image.save(image_bytes, format=image.format)
    image = io.BytesIO(image_bytes.getvalue())
    return image


def change_size_collection(collection_id: str, data: dict) -> dict:
    """
    Change the size of collection
    :param collection_id: the collection id
    :param data: dict with a new size of collection for changing
    :return: dict with status of change
    """
    collection_doc = get_collection_by_id(collection_id)
    collection_dict = collection_doc.to_dict()
    data = validate(data, UpdateSizeCollection)
    if len(collection_dict['cards']) > data['size']:
        raise HttpError(
            400,
            {'message': 'there are more images in the collection than in the new size'}
        )
    data = update_data_collection(collection_doc, **data)

    return data
