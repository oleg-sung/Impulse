from werkzeug.datastructures.file_storage import FileStorage

from backend.error import HttpError
from config import ALLOWED_EXTENSIONS


def image_validate(file: FileStorage) -> tuple[bytes, str]:
    """
    Validate an image type using ALLOWED_EXTENSIONS from manage
    :param file: file to validate FileStorage type
    :return: file in format bytes
    """
    file_format = file.filename.split('.')[-1]
    if file_format not in ALLOWED_EXTENSIONS:
        error_dict = {
            'status': 'error',
            'message': f'File type not allowed: {file_format}',
            'allowed': ALLOWED_EXTENSIONS
        }
        raise HttpError(400, error_dict)

    return file.read(), file.filename
