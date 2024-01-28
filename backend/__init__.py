from flask import Flask
from flask_mail import Mail
from dotenv import load_dotenv

from backend.celery import celery_init_app
from backend.error import error_handler, HttpError

load_dotenv()

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.debug = True
mail = Mail(app)
app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://127.0.0.1:6379/0",
        result_backend="redis://127.0.0.1:6379/1",
        task_ignore_result=True,
    ),
)
celery = celery_init_app(app)

from backend.users.view import user_api
from backend.tokens.view import token_api
from backend.collection.view import collection_api

app.register_blueprint(user_api, url_prefix='/user')
app.register_blueprint(token_api, url_prefix='/token')
app.register_blueprint(collection_api, url_prefix='/collection')
app.register_error_handler(HttpError, error_handler)



