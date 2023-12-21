import json

import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('env/key_develop.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()
pb = pyrebase.initialize_app(json.load(open('env/fb_kay.json')))
