from google.cloud.exceptions import NotFound
from google.cloud.firestore_v1 import DocumentSnapshot

from backend.collection.schema import Collection
from backend.error import validate, HttpError
from firebase_db import collection_model


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
    status = update_data_collection(_id, is_active=data['is_active'])
    return status


def update_data_collection(_id: str, **kwargs) -> dict:
    """
    Updating collection data using kwargs
    :param _id: collection id in firebase
    :param kwargs: param for updating
    """
    collection_doc = get_collection_by_id(_id)
    try:
        collection_doc.reference.update({**kwargs})
    except NotFound:
        raise HttpError(404, f'Collection with id {_id} not found')
    return {'status': f'Collection({collection_doc.id}) has updated successful'}


def get_collection_by_id(_id: str) -> DocumentSnapshot:
    """
    Get collection objects (DocumentSnapshot type) by id
    :param _id: collection's id in firebase
    :return: collection object Document Snapshot type
    """
    try:
        collection_doc = collection_model.document(_id).get()
    except Exception as e:
        raise HttpError(404, 'Collection not found')
    return collection_doc
