from celery import shared_task

from backend.firebase_db.services import FirebaseDB


@shared_task(ignore_result=True)
def add_card_to_collection(model_name, key, value, _id):
    FirebaseDB().add_doc_to_list(model_name, key, value, _id)
