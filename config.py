import os

from dotenv import load_dotenv

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


class Config(object):
    # Определяет, включен ли режим отладки
    # В случае если включен, flask будет показывать
    # подробную отладочную информацию. Если выключен -
    # - 500 ошибку без какой-либо дополнительной информации.
    DEBUG = False
    # Включение защиты против "Cross-site Request Forgery (CSRF)"
    CSRF_ENABLED = True
    # Случайный ключ, которые будет исползоваться для подписи
    # данных, например cookies.
    SECRET_KEY = os.environ.get('SECRET_KEY', None)

    load_dotenv()
    # Send email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', None)
    MAIL_PORT = os.environ.get('MAIL_PORT', None)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', None)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', None)
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', None)
    MAIL_DEFAULT_SENDER = MAIL_USERNAME


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
