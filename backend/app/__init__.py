from flask import Flask

from app.config import config_by_name
from app.extensions import db, migrate
from app.routes import register_routes


def create_app(config_name="development"):
    app = Flask(__name__)

    config_class = config_by_name.get(config_name)

    if config_class is None:
        raise ValueError(f"Invalid configuration: {config_name}")

    app.config.from_object(config_class)

    # Prevent production from running without a secure secret key.
    if config_name == "production" and not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY must be set in the environment when running in production."
        )

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError(
            "DATABASE_URL must be configured before initializing the database."
        )

    db.init_app(app)
    migrate.init_app(app, db)
    register_routes(app)

    return app