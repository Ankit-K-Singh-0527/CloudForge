
import os

from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    DEBUG = False
    TESTING = False

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CloudForge browser authentication cookie.
    AUTH_COOKIE_NAME = "cloudforge_session"
    AUTH_COOKIE_HTTPONLY = True
    AUTH_COOKIE_SECURE = False
    AUTH_COOKIE_SAMESITE = "Lax"
    AUTH_COOKIE_PATH = "/"

    # Frontend origins trusted by the backend.
    FRONTEND_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5173",
        ).split(",")
        if origin.strip()
    ]


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    AUTH_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    # Production must never use the development fallback.
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = False
    AUTH_COOKIE_SECURE = True

    FRONTEND_ORIGINS = [
        origin.strip()
        for origin in os.getenv("FRONTEND_ORIGINS", "").split(",")
        if origin.strip()
    ]


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    AUTH_COOKIE_SECURE = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
