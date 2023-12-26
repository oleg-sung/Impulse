from flask import Blueprint, jsonify, request

from backend.collection.services import create_new_collection, change_status_collection
from backend.users.decorators import authorization

collection_api = Blueprint('collection', __name__)


@collection_api.route('/create/', methods=['POST'])
@authorization
def create_collection():
    """
    Create a new empty collection
    :return: JSON data
    """

    data = create_new_collection(request.json)
    return jsonify(data), 201


@collection_api.route('/disable/<id_collections>/', methods=['PUT'])
def disable_collection(id_collections):
    """
    Disable the collection by collections id
    """
    data = change_status_collection(request.json, id_collections)
    return jsonify(data), 201
