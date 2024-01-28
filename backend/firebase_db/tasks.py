import base64
import io

from celery import shared_task

from backend.firebase_db import bucket, db

model_dict = {
    'collection': 'collection',
    'club': 'club',
    'user_profile': 'userProfile',
    'token': 'token'
}


@shared_task(ignore_result=True)
def upload_file_to_storage(content: str, blob_name: str, content_type: str = None, metadata: dict = None) -> None:
    blob = bucket.blob(blob_name)
    if content_type is not None:
        blob.content_type = content_type
    if metadata is not None:
        blob.metadata = metadata
    bytes_file = base64.b64decode(content.encode('utf-8'))
    _content = io.BytesIO(bytes_file)
    blob.upload_from_file(_content)
    blob.make_public()


@shared_task(ignore_result=True)
def delete_document(model_name: str, _id: str) -> None:
    doc = db.collection(model_dict.get(model_name)).document(_id)
    doc.delete()


@shared_task(ignore_result=True)
def update_document(model_name: str, _id: str, data: dict, ) -> None:
    doc = db.collection(model_dict.get(model_name)).document(_id)
    doc.update(data)
