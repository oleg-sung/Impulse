from flask import Blueprint, jsonify, request

from backend.collection.services import CollectionService, CardService
from backend.users.decorators import authorization

collection_api = Blueprint('collection', __name__)


@collection_api.route('/', methods=['GET'])
def get_all_collections():
    data = CollectionService().get_all_collections_data()
    return jsonify(data), 200


@collection_api.route('/<id_collection>/', methods=['GET'])
def get_collection(id_collection: str):
    data = CollectionService(id_collection).get_collection_data()
    return jsonify(data), 200


@collection_api.route('/create/', methods=['POST'])
@authorization
def create_collection():
    """
    Create a new empty collection
    :return: JSON data
    """

    data = CollectionService(request.user['user_id']).create_collection(request.json)
    return jsonify(data), 201


@collection_api.route('/<id_collection>/disable/', methods=['PUT'])
@authorization
def disable_collection(id_collection: str):
    """
    Disable the collection by collections id
    """
    data = CollectionService(request.user['user_id']).change_status_collection(id_collection)
    return jsonify(data), 201


@collection_api.route('/<id_collection>/card/create/', methods=['POST'])
@authorization
def add_card_in_collection(id_collection: str):
    file = request.files['image']
    metadata = request.form.to_dict()
    metadata['collection'] = id_collection
    data = CardService(id_collection).create_card(file, metadata)
    return jsonify({'success': True, **data}), 201


@collection_api.route('/<id_collection>/card/<id_card>/delete/', methods=['DELETE'])
@authorization
def delete_card_from_collection(id_collection: str, id_card: str):
    # delete_card(id_collection, id_card)
    ...
    return jsonify(), 204


@collection_api.route('/<id_collection>/card/<id_card>/', methods=['GET'])
@authorization
def get_card_from_collection(id_collection: str, id_card: str):
    data = CardService(id_collection).get_card_info(id_card)
    return jsonify(data), 200


@collection_api.route('/<id_collection>/cards/', methods=['GET'])
@authorization
def get_all_cards_info_for_collection(id_collection: str):
    data = CardService(id_collection).get_all_cards_info()
    return jsonify(data), 200


@collection_api.route('/<id_collection>/cards/<_type>/', methods=['GET'])
@authorization
def get_cards(id_collection: str, _type: str):
    data = CardService(id_collection).get_card_by_type(_type)
    return jsonify(data), 200
