import json

import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage

cred = credentials.Certificate('env/key_develop.json')
default_app = firebase_admin.initialize_app(cred)

# init firebase auth method
fb_auth = auth

# init database
db = firestore.client()
# init database models
club_model = db.collection('club')
user_profile_model = db.collection('userProfile')
token_model = db.collection('token')
collection_model = db.collection('collection')

# init pyrebase auth method
pb = pyrebase.initialize_app(json.load(open('env/fb_kay.json')))
pb_auth = pb.auth()

# init storage bucket
bucket = storage.bucket(json.load(open('env/fb_kay.json'))['storageBucket'])
