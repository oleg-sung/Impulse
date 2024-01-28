from celery import shared_task
from firebase_admin.auth import UserRecord
from flask_mail import Message

from config import Config
from backend.firebase_db.services import FirebaseAuth
from backend import mail


@shared_task(ignore_result=True)
def send_mail(subject: str, recipient: str, email_link: str, **kwargs) -> None:
    msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[recipient])
    msg.html = email_link
    mail.send(msg)


def send_email_with_verification_link(user: UserRecord, auth_class: FirebaseAuth) -> None:
    """
    Send email with verification link to user email address
    :param user: object user(USer Record type)
    :param auth_class: firebase auth class
    :return: None
    """
    link = auth_class.fb_auth.generate_email_verification_link(user.email)
    subject = f'Verification link for {user.uid}'
    send_mail.delay(subject, user.email, link)
