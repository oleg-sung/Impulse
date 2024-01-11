from flask import Blueprint, jsonify, request

from backend.collection.services import create_new_collection, change_status_collection, get_collection_data, \
    get_all_collections_data, create_card_to_collection, change_size_collection
from backend.users.decorators import authorization

collection_api = Blueprint('collection', __name__)


@collection_api.route('/', methods=['GET'])
@authorization
def get_all_collections():
    data = get_all_collections_data()
    return jsonify(data), 200


@collection_api.route('/<id_collection>/', methods=['GET'])
@authorization
def get_collection(id_collection: str):
    data = get_collection_data(id_collection)
    return jsonify(data), 200


@collection_api.route('/create/', methods=['POST'])
def create_collection():
    """
    Create a new empty collection
    :return: JSON data
    """

    data = create_new_collection(request.json)
    return jsonify(data), 201


@collection_api.route('/<id_collection>/disable/', methods=['PUT'])
@authorization
def disable_collection(id_collection: str):
    """
    Disable the collection by collections id
    """
    data = change_status_collection(request.json, id_collection)
    return jsonify(data), 201


@collection_api.route('/<id_collection>/delete/', methods=['DELETE'])
@authorization
def delete_collection(id_collection: str):
    ...


@collection_api.route('/<id_collection>/size/change/', methods=['PUT'])
@authorization
def change_size_collection(id_collection: str):
    data = change_size_collection(id_collection, request.json)
    return jsonify(data), 201


@collection_api.route('/<id_collection>/card/create/', methods=['POST'])
@authorization
def add_card_in_collection(id_collection: str):
    file = request.files['image']
    metadata = request.form.to_dict()
    metadata['collection'] = id_collection
    data = create_card_to_collection(file, metadata)
    return jsonify({'success': True, **data}), 201


@collection_api.route('/<id_collection>/card/', methods=['DELETE'])
@authorization
def delete_card_from_collection(id_collections: str):
    ...


@collection_api.route('/<id_collection>/card/<id_card>/', methods=['GET'])
@authorization
def get_card_from_collection(id_collection: str, id_card: str):
    ...
