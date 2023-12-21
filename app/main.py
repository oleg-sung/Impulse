from flask import Flask
from flask_mail import Mail
from dotenv import load_dotenv

from app.error import error_handler, HttpError

load_dotenv()

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.debug = True
mail = Mail(app)

from app import user_view

app.register_blueprint(user_view.user_api, url_prefix='/users')
app.register_error_handler(HttpError, error_handler)

from app import user_view, error, services, email, schema, permissions
