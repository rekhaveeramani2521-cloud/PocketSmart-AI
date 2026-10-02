import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

APP_NAME = os.getenv("APP_NAME", "PocketSmart AI")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'pocketsmart.db'}")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() in {"1", "true", "yes", "on"}
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "5"))
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
