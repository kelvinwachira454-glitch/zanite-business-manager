import os
import secrets

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
SECRET_KEY_FILE = os.path.join(INSTANCE_DIR, "secret_key.txt")


def _get_or_create_secret_key():
    env_key = os.environ.get("SECRET_KEY")
    if env_key:
        return env_key

    os.makedirs(INSTANCE_DIR, exist_ok=True)
    if os.path.exists(SECRET_KEY_FILE):
        with open(SECRET_KEY_FILE, "r") as f:
            existing = f.read().strip()
            if existing:
                return existing

    new_key = secrets.token_hex(32)
    with open(SECRET_KEY_FILE, "w") as f:
        f.write(new_key)
    return new_key


SQLITE_PREFIX = "sqlite:///"


def _resolve_database_url():
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return f"{SQLITE_PREFIX}{os.path.join(BASE_DIR, 'database', 'business.db')}"
    if url.startswith(SQLITE_PREFIX) and not url.startswith("sqlite:////") and ":memory:" not in url:
        relative_path = url[len(SQLITE_PREFIX):]
        if not os.path.isabs(relative_path):
            return f"{SQLITE_PREFIX}{os.path.join(BASE_DIR, relative_path)}"
    return url


def _sqlite_file_path(url):
    if url.startswith(SQLITE_PREFIX):
        return url[len(SQLITE_PREFIX):]
    return None


DATABASE_URL = _resolve_database_url()


class Config:
    SECRET_KEY = _get_or_create_secret_key()
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    DEFAULT_CURRENCY = "KES"
    LOW_STOCK_DEFAULT_THRESHOLD = 5
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    FORCE_HTTPS = os.environ.get("FORCE_HTTPS", "false").lower() == "true"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8

    BACKUP_ENABLED = os.environ.get("BACKUP_ENABLED", "false").lower() == "true"
    BACKUP_INTERVAL_HOURS = float(os.environ.get("BACKUP_INTERVAL_HOURS", "24"))
    BACKUP_RETENTION_COUNT = int(os.environ.get("BACKUP_RETENTION_COUNT", "14"))
    BACKUP_DIR = os.environ.get("BACKUP_DIR", "").strip() or os.path.join(BASE_DIR, "backups")
    BACKUP_SOURCE_PATH = _sqlite_file_path(DATABASE_URL) or os.path.join(BASE_DIR, "database", "business.db")