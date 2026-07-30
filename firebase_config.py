import os
import json
import firebase_admin
from firebase_admin import credentials, firestore


def _load_firebase_credentials():
    env_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if env_json:
        return credentials.Certificate(json.loads(env_json))

    key_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")
    if os.path.isfile(key_path):
        return credentials.Certificate(key_path)

    raise RuntimeError(
        "Firebase credentials not found. Set FIREBASE_SERVICE_ACCOUNT or place "
        "serviceAccountKey.json in the project root."
    )


cred = _load_firebase_credentials()

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
