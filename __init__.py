import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firestore-keys.json")
firebase_admin.initialize_app(cred)