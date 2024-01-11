from flask import Flask
from flask_mail import Mail
from dotenv import load_dotenv


from backend.error import error_handler, HttpError

load_dotenv()

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.debug = True
mail = Mail(app)

from backend.users.view import user_api
from backend.tokens.view import token_api
from backend.collection.view import collection_api

app.register_blueprint(user_api, url_prefix='/user')
app.register_blueprint(token_api, url_prefix='/token')
app.register_blueprint(collection_api, url_prefix='/collection')
app.register_error_handler(HttpError, error_handler)


from backend.users import services, view, schema
from backend.tokens import services, view, schema
from backend.collection import services, view, schema

if __name__ == '__main__':
    app.run()
