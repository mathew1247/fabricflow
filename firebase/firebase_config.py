"""
FABRICFLOW ANALYTICS - FIREBASE CONFIGURATION
Initializes Firebase Admin SDK and Cloud Firestore client.
Only uses Firebase Cloud Firestore.
"""

import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore, auth
from config import Config

logger = logging.getLogger("fabricflow.firebase")

_firebase_app = None
_firestore_db = None
_firebase_initialized = False


def locate_service_account_key():
    """
    Safely locates the Firebase service account credentials JSON file.
    Checks environment variable path, backend/serviceaccountkey.json, and root paths.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    candidate_paths = [
        Config.FIREBASE_CREDENTIALS_PATH,
        os.path.join(project_root, "backend", "serviceaccountkey.json"),
        os.path.join(project_root, "backend", "serviceAccountKey.json"),
        os.path.join(project_root, "serviceaccountkey.json"),
        os.path.join(project_root, "serviceAccountKey.json"),
        os.path.join(os.path.dirname(__file__), "serviceaccountkey.json"),
        os.path.join(os.path.dirname(__file__), "serviceAccountKey.json"),
        os.path.join(os.path.dirname(__file__), "firebase-credentials.json"),
    ]

    for p in candidate_paths:
        if p:
            abs_p = p if os.path.isabs(p) else os.path.join(project_root, p)
            if os.path.isfile(abs_p):
                return abs_p

    return None


def init_firebase():
    """
    Initializes Firebase Admin SDK only once and connects to Cloud Firestore.
    """
    global _firebase_app, _firestore_db, _firebase_initialized

    if _firestore_db is not None:
        return _firestore_db

    key_path = locate_service_account_key()
    if not key_path:
        raise FileNotFoundError(
            "Firebase service account key not found! Place it in 'backend/serviceaccountkey.json' "
            "or set FIREBASE_CREDENTIALS_PATH in .env"
        )

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(key_path)
            options = {}
            if Config.FIREBASE_PROJECT_ID:
                options["projectId"] = Config.FIREBASE_PROJECT_ID
            _firebase_app = firebase_admin.initialize_app(cred, options)
            logger.info("Firebase Admin SDK initialized successfully.")
        else:
            _firebase_app = firebase_admin.get_app()

        _firestore_db = firestore.client()
        _firebase_initialized = True
        logger.info(f"Connected to Firebase Cloud Firestore using credentials at {key_path}")
        return _firestore_db
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
        raise


def get_db():
    """Returns the initialized Cloud Firestore client."""
    global _firestore_db
    if _firestore_db is None:
        return init_firebase()
    return _firestore_db


def get_auth():
    """Returns Firebase Authentication module."""
    if _firebase_app is None:
        init_firebase()
    return auth


def check_firestore_connection():
    """
    Tests live Cloud Firestore connectivity by performing an actual read operation.
    Returns (True, "connected") if healthy, otherwise (False, error_details).
    """
    try:
        db = get_db()
        # Perform safe read operation on products collection with limit 1
        docs = list(db.collection("products").limit(1).stream())
        return True, "connected"
    except Exception as e:
        logger.error(f"Firestore connectivity check failed: {e}")
        return False, str(e)


def is_firebase_initialized():
    """Checks if Firebase is initialized."""
    return _firebase_initialized
