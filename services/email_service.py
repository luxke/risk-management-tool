from flask_mail import Message
from extensions import mail


def send_email(recipient, subject, html):

    msg = Message(
        subject=subject,
        recipients=[recipient]
    )

    msg.html = html

    mail.send(msg)