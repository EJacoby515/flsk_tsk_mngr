import pyrebase
from config import Config


firebase = pyrebase.initialize_app(Config.FIREBASE_CONFIG)
auth = firebase.auth()