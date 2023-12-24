from flask_mail import Message

from manage import app, mail


def send_mail(subject: str, recipient: str, email_link: str, **kwargs) -> None:
    msg = Message(subject, sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[recipient])
    msg.html = email_link
    mail.send(msg)
