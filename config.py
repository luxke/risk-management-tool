import os

class Config:

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = "your_email@gmail.com"
    MAIL_PASSWORD = "YOUR_APP_PASSWORD"

    MAIL_DEFAULT_SENDER = (
        "Risk Management System",
        "your_email@gmail.com"
    )