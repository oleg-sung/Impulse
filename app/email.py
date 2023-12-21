from flask_mail import Message

from app.main import app, mail


def send_mail(subject, recipient, email_link, **kwargs):
    msg = Message(subject, sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[recipient])
    msg.html = email_link
    mail.send(msg)
    return True
