
from flask import Flask
from flask_cors import CORS

from app.config import config_by_name
from app.extensions import db, migrate
from app.routes import register_routes
import app.models


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

    # Allow browser requests only from explicitly trusted frontend origins.
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["FRONTEND_ORIGINS"],
            }
        },
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-CSRF-Token"],
        vary_header=True,
    )

    db.init_app(app)
    migrate.init_app(app, db)

    register_routes(app)

    return app
