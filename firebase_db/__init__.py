import json

import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore, auth

cred = credentials.Certificate('env/key_develop.json')
default_app = firebase_admin.initialize_app(cred)

fb_auth = auth

db = firestore.client()
user_profile_model = db.collection('user_profile')
token_model = db.collection('tokens')


pb = pyrebase.initialize_app(json.load(open('env/fb_kay.json')))
pb_auth = pb.auth()


