import json

from flask import jsonify
from pydantic import ValidationError


class HttpError(Exception):
    def __init__(self, status_code: int, message: dict | str | list):
        self.status_code = status_code
        self.message = message


def validate(json_data, schema):
    try:
        model = schema(**json_data)
        return model.dict(exclude_none=True)
    except ValidationError as err:
        error_message = json.loads(err.json())
        raise HttpError(400, error_message)


def error_handler(er: HttpError):
    http_response = jsonify({'status': 'error', 'message': er.message})
    http_response.status_code = er.status_code
    return http_response
