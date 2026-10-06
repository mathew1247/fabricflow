import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration settings."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "fabricflow-analytics-secret-key-2024-jwt")
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    PORT = int(os.environ.get("PORT", 5000))
    HOST = os.environ.get("HOST", "0.0.0.0")

    # Firebase configuration
    FIREBASE_CREDENTIALS_PATH = os.environ.get("FIREBASE_CREDENTIALS_PATH", "backend/serviceaccountkey.json")
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", None)
    FIREBASE_DATABASE_URL = os.environ.get("FIREBASE_DATABASE_URL", None)

    # Local fallback storage directory (when live Firebase credentials are not yet configured)
    DATA_STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "generated")

    # Default Garment Thresholds
    DEFAULT_CRITICAL_STOCK_THRESHOLD = int(os.environ.get("DEFAULT_CRITICAL_STOCK_THRESHOLD", 5))
    DEFAULT_LOW_STOCK_THRESHOLD = int(os.environ.get("DEFAULT_LOW_STOCK_THRESHOLD", 20))
